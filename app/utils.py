from .models import Student, Bed, Room

def free_beds_query():
    return Bed.query.filter(Bed.occupied_by_student_id.is_(None)).join(Room).order_by(Room.number, Bed.label)

def occupied_beds_query():
    return Bed.query.filter(Bed.occupied_by_student_id.isnot(None)).join(Room).order_by(Room.number, Bed.label)

def find_student_by_contact(name, email, phone):
    q = Student.query
    if email:
        s = q.filter(Student.email == email).first()
        if s:
            return s
    if phone:
        s = q.filter(Student.phone == phone).first()
        if s:
            return s
    return q.filter(Student.full_name == name).first()
