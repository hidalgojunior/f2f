from datetime import datetime
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    # keep cor field for backwards compatibility if some code uses it
    cor = db.Column(db.String(50), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    region = db.relationship('Region', back_populates='users')
    email = db.Column(db.String(120))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    attendances = db.relationship('Attendance', back_populates='user', cascade='all, delete-orphan')
    admin_record = db.relationship('Admin', back_populates='user', uselist=False, cascade='all, delete-orphan')
    # teams this user belongs to
    teams = db.relationship('Team', secondary='team_user', back_populates='users')

    def __repr__(self):
        return f"<User {self.telefone} - {self.nome}>"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # scrypt hashes can exceed 128 characters; accommodate longer values
    password_hash = db.Column(db.String(256), nullable=False)
    is_original = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='admin_record')

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Admin {self.user.telefone} original={self.is_original}>"


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', back_populates='region')


team_user = db.Table('team_user',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    # optional leader for the team; a user who leads this group
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    leader = db.relationship('User', foreign_keys=[leader_id])
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    meeting = db.relationship('Meeting', back_populates='teams')
    region = db.relationship('Region')
    users = db.relationship('User', secondary=team_user, back_populates='teams')




class Setting(db.Model):
    """Flexible key/value configuration stored in the database."""
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(256))

    @staticmethod
    def get(key, default=None):
        s = Setting.query.get(key)
        return s.value if s else default

    @staticmethod
    def set(key, val):
        s = Setting.query.get(key)
        if s:
            s.value = val
        else:
            s = Setting(key=key, value=val)
            db.session.add(s)
        db.session.commit()


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120),nullable=False)
    data_inicial = db.Column(db.Date, nullable=False)
    data_final = db.Column(db.Date, nullable=False)
    meetings = db.relationship('Meeting', back_populates='event', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Event {self.nome} {self.data_inicial}..{self.data_final}>"


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    titulo = db.Column(db.String(120), nullable=False, default='')
    data = db.Column(db.Date, nullable=False)
    special = db.Column(db.Boolean, default=False)
    event = db.relationship('Event', back_populates='meetings')
    attendances = db.relationship('Attendance', back_populates='meeting', cascade='all, delete-orphan')
    qrcodes = db.relationship('QRCode', back_populates='meeting', cascade='all, delete-orphan')
    teams = db.relationship('Team', back_populates='meeting', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Meeting {self.titulo or self.data} for event {self.event.nome}>"


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    confirmado_em = db.Column(db.DateTime, default=datetime.utcnow)
    meeting = db.relationship('Meeting', back_populates='attendances')
    user = db.relationship('User', back_populates='attendances')

    def __repr__(self):
        return f"<Attendance user={self.user.telefone} meeting={self.meeting.data}>"


class AccessRequest(db.Model):
    __tablename__ = 'access_requests'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    purpose = db.Column(db.String(256))
    password_hash = db.Column(db.String(256), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    region = db.relationship('Region')

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f"<AccessRequest {self.telefone} approved={self.approved}>"


class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    gerado_em = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    meeting = db.relationship('Meeting', back_populates='qrcodes')

    def __repr__(self):
        return f"<QRCode {self.token} for {self.meeting.data} active={self.active}>"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
