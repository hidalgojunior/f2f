from app import create_app, db
from app.models import User, Admin, Event, Meeting, Attendance, QRCode, Team

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Admin': Admin,
        'Event': Event,
        'Meeting': Meeting,
        'Attendance': Attendance,
        'QRCode': QRCode,
        'Team': Team,
            }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
