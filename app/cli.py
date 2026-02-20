import click
from flask.cli import with_appcontext
from . import db
from .models import Room, Bed

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

    if not Room.query.first():
        r1 = Room(number="101", capacity=3)
        r2 = Room(number="102", capacity=2)
        r3 = Room(number="201", capacity=4)
        db.session.add_all([r1, r2, r3])
        db.session.flush()

        for r in [r1, r2, r3]:
            for i in range(1, r.capacity + 1):
                db.session.add(Bed(room_id=r.id, label=str(i)))

        db.session.commit()

    click.echo("DB initialized")
