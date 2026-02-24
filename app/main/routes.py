from flask import render_template, request, redirect, url_for, flash, abort
from app.main import bp
from app import db
from app.models import User, Attendance, QRCode, Meeting, Region, AccessRequest
from datetime import datetime


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/scan/<token>', methods=['GET', 'POST'])
def scan(token):
    # token identifies a QRCode which is tied to a meeting
    qrcode = QRCode.query.filter_by(token=token).first_or_404()
    meeting = qrcode.meeting
    # if this qrcode was deprecated but another active exists, redirect
    if not qrcode.active:
        replacement = QRCode.query.filter_by(meeting_id=meeting.id, active=True).first()
        if replacement:
            return redirect(url_for('main.scan', token=replacement.token))
    # compute closed flag (inactive, event over, or outside allowed time)
    today = datetime.utcnow().date()
    now = datetime.utcnow()
    closed = False
    if not qrcode.active or meeting.event.data_final < today:
        closed = True
    elif meeting.data != today:
        h = now.hour
        m = now.minute
        if not ((h >= 18 and h < 23) or (h == 23 and m <= 30)):
            closed = True
    if closed:
        flash('Inscrições encerradas para este QR code', 'danger')
        return render_template('scan.html', token=token, meeting=meeting, datetime=datetime, closed=True, simple=True)
    if request.method == 'POST':
        telefone = request.form.get('telefone') or ''
        # remove non-digit characters
        telefone = ''.join(ch for ch in telefone if ch.isdigit())
        if not telefone:
            flash('Informe o telefone', 'danger')
            return redirect(url_for('main.scan', token=token))
        # re-check closed on POST as well
        today = datetime.utcnow().date()
        now = datetime.utcnow()
        if not qrcode.active or meeting.event.data_final < today or (meeting.data != today and not ((now.hour >= 18 and now.hour < 23) or (now.hour == 23 and now.minute <= 30))):
            flash('Inscrições encerradas para este QR code', 'danger')
            return redirect(url_for('main.scan', token=token))
        user = User.query.filter_by(telefone=telefone).first()
        if user:
            # register attendance if not already done
            existing = Attendance.query.filter_by(meeting=meeting, user=user).first()
            if existing:
                flash('Telefone já registrado nesta reunião', 'info')
            else:
                from zoneinfo import ZoneInfo
                att = Attendance(meeting=meeting, user=user,
                                 confirmado_em=datetime.now(ZoneInfo('America/Sao_Paulo')))
                db.session.add(att)
                db.session.commit()
                flash('Presença confirmada!', 'success')
                # notifications removed (no external integrations)
            return render_template('confirm.html', user=user, meeting=meeting, simple=True)
        else:
            # flow to register new user
            return redirect(url_for('main.register', token=token, telefone=telefone))
    return render_template('scan.html', token=token, meeting=meeting, datetime=datetime, simple=True)


@bp.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    telefone = request.args.get('telefone') or ''
    telefone = ''.join(ch for ch in telefone if ch.isdigit())
    if not telefone:
        return redirect(url_for('main.scan', token=token))
    qrcode = QRCode.query.filter_by(token=token).first_or_404()
    meeting = qrcode.meeting
    regions = Region.query.order_by(Region.nome).all()
    if request.method == 'POST':
        # prevent register if closed
        today = datetime.utcnow().date()
        now = datetime.utcnow()
        if not qrcode.active or meeting.event.data_final < today or (meeting.data != today and not ((now.hour >= 18 and now.hour < 23) or (now.hour == 23 and now.minute <= 30))):
            flash('Inscrições encerradas para este QR code', 'danger')
            return redirect(url_for('main.scan', token=token))
        nome = request.form.get('nome', '').strip().upper()
        region_id = request.form.get('region_id')
        email = request.form.get('email')
        if not nome or not region_id:
            flash('Nome e região são obrigatórios', 'danger')
            return redirect(url_for('main.register', token=token, telefone=telefone))
        reg = Region.query.get(region_id)
        user = User(telefone=telefone, nome=nome, cor=reg.nome if reg else '', region=reg, email=email)
        db.session.add(user)
        db.session.commit()
        # create attendance record
        from zoneinfo import ZoneInfo
        att = Attendance(meeting=meeting, user=user,
                         confirmado_em=datetime.now(ZoneInfo('America/Sao_Paulo')))
        db.session.add(att)
        db.session.commit()
        # no external notifications
        return render_template('confirm.html', user=user, meeting=meeting, simple=True)
    return render_template('register.html', telefone=telefone, regions=regions, simple=True)


@bp.route('/request-access', methods=['GET','POST'])
def request_access():
    regions = Region.query.order_by(Region.nome).all()
    if request.method == 'POST':
        nome = request.form.get('nome','').strip().upper()
        telefone = ''.join(ch for ch in request.form.get('telefone','') if ch.isdigit())
        region_id = request.form.get('region_id')
        purpose = request.form.get('purpose','').strip()
        password = request.form.get('password','')
        if not nome or not telefone or not region_id or not password:
            flash('Nome, telefone, região e senha são obrigatórios', 'danger')
            return redirect(url_for('main.request_access'))
        req = AccessRequest(nome=nome, telefone=telefone, region_id=region_id, purpose=purpose)
        req.set_password(password)
        db.session.add(req)
        db.session.commit()
        flash('Solicitação enviada, aguarde aprovação', 'success')
        return redirect(url_for('main.index'))
    return render_template('request_access.html', regions=regions)
