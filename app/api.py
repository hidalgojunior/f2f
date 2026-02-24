from flask import Blueprint, request, jsonify, current_app
from app.models import Event, User, Attendance, Setting, QRCode
from app import db

bp = Blueprint('api', __name__)


def check_token():
    token = request.args.get('token') or request.headers.get('X-API-Token')
    if not token:
        return False
    expected = Setting.get('API_TOKEN') or current_app.config.get('API_TOKEN')
    return token == expected

@bp.before_request
def require_token():
    if not check_token():
        return jsonify({'error': 'invalid or missing API token'}), 401

@bp.route('/events', methods=['GET'])
def get_events():
    evs = Event.query.all()
    return jsonify([{'id':e.id, 'nome':e.nome, 'data_inicial':e.data_inicial.isoformat(), 'data_final':e.data_final.isoformat()} for e in evs])

@bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id':u.id, 'telefone':u.telefone, 'nome':u.nome, 'region':u.region.nome if u.region else None} for u in users])

@bp.route('/attendance', methods=['POST'])
def post_attendance():
    data = request.json or {}
    token = data.get('token')
    telefone = data.get('telefone')
    if not token or not telefone:
        return jsonify({'error': 'token and telefone required'}), 400
    q = current_app.extensions['sqlalchemy'].db.session
    qr = q.query(QRCode).filter_by(token=token).first()
    if not qr or not qr.active:
        return jsonify({'error': 'invalid qrcode'}), 404
    meeting = qr.meeting
    user = q.query(User).filter_by(telefone=telefone).first()
    if not user:
        return jsonify({'error': 'user not found'}), 404
    existing = q.query(Attendance).filter_by(meeting=meeting, user=user).first()
    if existing:
        return jsonify({'status': 'already registered'})
    att = Attendance(meeting=meeting, user=user)
    q.add(att)
    q.commit()
    return jsonify({'status': 'ok'})
