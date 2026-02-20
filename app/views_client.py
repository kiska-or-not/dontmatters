from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Application, Room

bp = Blueprint("client", __name__)

@bp.get("/")
def index():
    return render_template("client/index.html")

@bp.get("/apply")
def apply_get():
    rooms = Room.query.order_by(Room.number).all()
    return render_template("client/apply.html", rooms=rooms)

@bp.post("/apply")
def apply_post():
    kind = request.form.get("kind", "").strip()
    student_name = request.form.get("student_name", "").strip()
    student_group = request.form.get("student_group", "").strip()
    contact_email = request.form.get("contact_email", "").strip()
    contact_phone = request.form.get("contact_phone", "").strip()
    desired_room = request.form.get("desired_room", "").strip()
    reason = request.form.get("reason", "").strip()

    if kind not in {"settle", "move"}:
        flash("Выберите тип заявки", "danger")
        return redirect(url_for("client.apply_get"))
    if not student_name:
        flash("Укажите ФИО", "danger")
        return redirect(url_for("client.apply_get"))

    app = Application(
        kind=kind,
        student_name=student_name,
        student_group=student_group or None,
        contact_email=contact_email or None,
        contact_phone=contact_phone or None,
        desired_room=desired_room or None,
        reason=reason or None,
        status="queued",
    )
    db.session.add(app)
    db.session.commit()

    return render_template("client/submitted.html", code=app.public_code)

@bp.get("/status")
def status_get():
    return render_template("client/status.html")

@bp.post("/status")
def status_post():
    code = request.form.get("code", "").strip().upper()
    if not code:
        flash("Введите код заявки", "danger")
        return redirect(url_for("client.status_get"))
    return redirect(url_for("client.status_view", code=code))

@bp.get("/status/<code>")
def status_view(code):
    code = (code or "").strip().upper()
    app = Application.query.filter_by(public_code=code).first()
    if not app:
        flash("Заявка не найдена", "warning")
        return redirect(url_for("client.status_get"))
    return render_template("client/status_view.html", app=app)
