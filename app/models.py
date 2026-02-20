import datetime as dt
import secrets
import string
from . import db

def gen_code(n=8):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(32), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=2)

    beds = db.relationship("Bed", backref="room", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Room {self.number}>"

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    group = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(60), nullable=True)

    bed = db.relationship("Bed", backref="student", uselist=False, foreign_keys="Bed.occupied_by_student_id")

    def __repr__(self):
        return f"<Student {self.full_name}>"

class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    label = db.Column(db.String(32), nullable=False)
    occupied_by_student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=True, unique=True)

    def __repr__(self):
        return f"<Bed {self.room_id}:{self.label}>"

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_code = db.Column(db.String(16), unique=True, nullable=False, index=True, default=gen_code)

    kind = db.Column(db.String(16), nullable=False)
    status = db.Column(db.String(16), nullable=False, default="queued")

    student_name = db.Column(db.String(200), nullable=False)
    student_group = db.Column(db.String(50), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(60), nullable=True)

    desired_room = db.Column(db.String(32), nullable=True)
    reason = db.Column(db.Text, nullable=True)

    assigned_bed_id = db.Column(db.Integer, db.ForeignKey("bed.id"), nullable=True)
    assigned_bed = db.relationship("Bed", foreign_keys=[assigned_bed_id])

    linked_student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=True)
    linked_student = db.relationship("Student", foreign_keys=[linked_student_id])

    admin_note = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: dt.datetime.utcnow())
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow())

    def __repr__(self):
        return f"<Application {self.public_code} {self.kind} {self.status}>"
