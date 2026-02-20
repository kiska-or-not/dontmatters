from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Room, Bed, Student, Application
from .utils import free_beds_query, occupied_beds_query, find_student_by_contact

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.get("/")
def dashboard():
    rooms = Room.query.count()
    beds = Bed.query.count()
    free_beds = Bed.query.filter(Bed.occupied_by_student_id.is_(None)).count()
    students = Student.query.count()
    queued = Application.query.filter_by(status="queued").count()
    return render_template("admin/dashboard.html", rooms=rooms, beds=beds, free_beds=free_beds, students=students, queued=queued)

@bp.get("/rooms")
def rooms_list():
    rooms = Room.query.order_by(Room.number).all()
    return render_template("admin/rooms_list.html", rooms=rooms)

@bp.get("/rooms/new")
def rooms_new_get():
    return render_template("admin/rooms_form.html", room=None)

@bp.post("/rooms/new")
def rooms_new_post():
    number = request.form.get("number", "").strip()
    capacity = request.form.get("capacity", "").strip()
    if not number:
        flash("Укажите номер комнаты", "danger")
        return redirect(url_for("admin.rooms_new_get"))
    try:
        cap = int(capacity)
        if cap <= 0:
            raise ValueError()
    except Exception:
        flash("Вместимость должна быть числом > 0", "danger")
        return redirect(url_for("admin.rooms_new_get"))

    if Room.query.filter_by(number=number).first():
        flash("Комната с таким номером уже существует", "warning")
        return redirect(url_for("admin.rooms_new_get"))

    room = Room(number=number, capacity=cap)
    db.session.add(room)
    db.session.flush()
    for i in range(1, cap + 1):
        db.session.add(Bed(room_id=room.id, label=str(i)))
    db.session.commit()
    flash("Комната создана", "success")
    return redirect(url_for("admin.rooms_list"))

@bp.get("/rooms/<int:room_id>/edit")
def rooms_edit_get(room_id):
    room = Room.query.get_or_404(room_id)
    return render_template("admin/rooms_form.html", room=room)

@bp.post("/rooms/<int:room_id>/edit")
def rooms_edit_post(room_id):
    room = Room.query.get_or_404(room_id)
    number = request.form.get("number", "").strip()
    capacity = request.form.get("capacity", "").strip()
    if not number:
        flash("Укажите номер комнаты", "danger")
        return redirect(url_for("admin.rooms_edit_get", room_id=room_id))
    try:
        cap = int(capacity)
        if cap <= 0:
            raise ValueError()
    except Exception:
        flash("Вместимость должна быть числом > 0", "danger")
        return redirect(url_for("admin.rooms_edit_get", room_id=room_id))

    existing = Room.query.filter(Room.number == number, Room.id != room.id).first()
    if existing:
        flash("Комната с таким номером уже существует", "warning")
        return redirect(url_for("admin.rooms_edit_get", room_id=room_id))

    room.number = number
    old_cap = room.capacity
    room.capacity = cap
    db.session.flush()

    beds = Bed.query.filter_by(room_id=room.id).order_by(Bed.id).all()
    if cap > len(beds):
        start = len(beds) + 1
        for i in range(start, cap + 1):
            db.session.add(Bed(room_id=room.id, label=str(i)))
    elif cap < len(beds):
        to_remove = beds[cap:]
        if any(b.occupied_by_student_id for b in to_remove):
            flash("Нельзя уменьшить вместимость: есть занятые места вне нового лимита", "danger")
            db.session.rollback()
            return redirect(url_for("admin.rooms_edit_get", room_id=room_id))
        for b in to_remove:
            db.session.delete(b)

    db.session.commit()
    if old_cap != cap:
        flash("Комната обновлена, места синхронизированы", "success")
    else:
        flash("Комната обновлена", "success")
    return redirect(url_for("admin.rooms_list"))

@bp.post("/rooms/<int:room_id>/delete")
def rooms_delete(room_id):
    room = Room.query.get_or_404(room_id)
    if any(b.occupied_by_student_id for b in room.beds):
        flash("Нельзя удалить комнату с занятыми местами", "danger")
        return redirect(url_for("admin.rooms_list"))
    db.session.delete(room)
    db.session.commit()
    flash("Комната удалена", "success")
    return redirect(url_for("admin.rooms_list"))

@bp.get("/students")
def students_list():
    students = Student.query.order_by(Student.full_name).all()
    occupied = occupied_beds_query().all()
    return render_template("admin/students_list.html", students=students, occupied=occupied)

@bp.get("/students/new")
def students_new_get():
    return render_template("admin/students_form.html", student=None)

@bp.post("/students/new")
def students_new_post():
    full_name = request.form.get("full_name", "").strip()
    group = request.form.get("group", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    if not full_name:
        flash("Укажите ФИО", "danger")
        return redirect(url_for("admin.students_new_get"))
    s = Student(full_name=full_name, group=group or None, email=email or None, phone=phone or None)
    db.session.add(s)
    db.session.commit()
    flash("Студент добавлен", "success")
    return redirect(url_for("admin.students_list"))

@bp.get("/students/<int:student_id>/edit")
def students_edit_get(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("admin/students_form.html", student=student)

@bp.post("/students/<int:student_id>/edit")
def students_edit_post(student_id):
    student = Student.query.get_or_404(student_id)
    full_name = request.form.get("full_name", "").strip()
    group = request.form.get("group", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    if not full_name:
        flash("Укажите ФИО", "danger")
        return redirect(url_for("admin.students_edit_get", student_id=student_id))
    student.full_name = full_name
    student.group = group or None
    student.email = email or None
    student.phone = phone or None
    db.session.commit()
    flash("Данные обновлены", "success")
    return redirect(url_for("admin.students_list"))

@bp.post("/students/<int:student_id>/delete")
def students_delete(student_id):
    student = Student.query.get_or_404(student_id)
    bed = Bed.query.filter_by(occupied_by_student_id=student.id).first()
    if bed:
        flash("Нельзя удалить: студент заселён. Освободите место.", "danger")
        return redirect(url_for("admin.students_list"))
    db.session.delete(student)
    db.session.commit()
    flash("Студент удалён", "success")
    return redirect(url_for("admin.students_list"))

@bp.get("/applications")
def applications_list():
    status = request.args.get("status", "queued").strip()
    q = Application.query
    if status and status != "all":
        q = q.filter_by(status=status)
    apps = q.order_by(Application.created_at.asc()).all()
    return render_template("admin/apps_list.html", apps=apps, status=status)

@bp.get("/applications/<int:app_id>")
def applications_view(app_id):
    app = Application.query.get_or_404(app_id)
    free_beds = free_beds_query().all()
    return render_template("admin/apps_view.html", app=app, free_beds=free_beds)

def ensure_student_from_application(app):
    s = None
    if app.linked_student_id:
        s = Student.query.get(app.linked_student_id)
        if s:
            return s
    s = find_student_by_contact(app.student_name, app.contact_email, app.contact_phone)
    if s:
        app.linked_student_id = s.id
        return s
    s = Student(
        full_name=app.student_name,
        group=app.student_group,
        email=app.contact_email,
        phone=app.contact_phone
    )
    db.session.add(s)
    db.session.flush()
    app.linked_student_id = s.id
    return s

@bp.post("/applications/<int:app_id>/reject")
def applications_reject(app_id):
    app = Application.query.get_or_404(app_id)
    note = request.form.get("admin_note", "").strip()
    app.status = "rejected"
    app.admin_note = note or None
    db.session.commit()
    flash("Заявка отклонена", "success")
    return redirect(url_for("admin.applications_list"))

@bp.post("/applications/<int:app_id>/approve")
def applications_approve(app_id):
    app = Application.query.get_or_404(app_id)
    bed_id = request.form.get("bed_id", "").strip()
    note = request.form.get("admin_note", "").strip()

    if app.status not in {"queued", "approved"}:
        flash("Нельзя подтвердить заявку в этом статусе", "danger")
        return redirect(url_for("admin.applications_view", app_id=app_id))

    if not bed_id:
        flash("Выберите место", "danger")
        return redirect(url_for("admin.applications_view", app_id=app_id))

    bed = Bed.query.get(int(bed_id))
    if not bed or bed.occupied_by_student_id is not None:
        flash("Место недоступно", "danger")
        return redirect(url_for("admin.applications_view", app_id=app_id))

    student = ensure_student_from_application(app)

    if app.kind == "settle":
        current = Bed.query.filter_by(occupied_by_student_id=student.id).first()
        if current:
            flash("Студент уже заселён. Используйте заявку на переселение.", "danger")
            return redirect(url_for("admin.applications_view", app_id=app_id))
        bed.occupied_by_student_id = student.id

    if app.kind == "move":
        current = Bed.query.filter_by(occupied_by_student_id=student.id).first()
        if not current:
            flash("Студент не найден среди заселённых. Можно подтвердить как заселение.", "warning")
        else:
            current.occupied_by_student_id = None
        bed.occupied_by_student_id = student.id

    app.assigned_bed_id = bed.id
    app.status = "completed"
    app.admin_note = note or None
    db.session.commit()
    flash("Заявка выполнена", "success")
    return redirect(url_for("admin.applications_list", status="queued"))

@bp.get("/occupancy")
def occupancy():
    rooms = Room.query.order_by(Room.number).all()
    return render_template("admin/occupancy.html", rooms=rooms)

@bp.post("/beds/<int:bed_id>/free")
def bed_free(bed_id):
    bed = Bed.query.get_or_404(bed_id)
    bed.occupied_by_student_id = None
    db.session.commit()
    flash("Место освобождено", "success")
    return redirect(url_for("admin.occupancy"))
