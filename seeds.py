"""Utility to seed initial data such as original administrator."""
import os
from app import create_app, db
from app.models import User, Admin
from datetime import datetime
import secrets


def create_original_admin():
    app = create_app()
    with app.app_context():
        # create tables if they don't exist (useful for sqlite/local dev)
        db.create_all()
        # if using sqlite and tables lack new columns, alter them
        if db.engine.url.drivername.startswith('sqlite'):
            from sqlalchemy import text
            with db.engine.connect() as conn:
                # qr_code active column
                res = conn.execute(text("PRAGMA table_info(qr_code);"))
                cols = [row[1] for row in res]
                if 'active' not in cols:
                    conn.execute(text('ALTER TABLE qr_code ADD COLUMN active BOOLEAN DEFAULT 1'))
                # meeting titulo column
                res2 = conn.execute(text("PRAGMA table_info(meeting);"))
                cols2 = [row[1] for row in res2]
                if 'titulo' not in cols2:
                    conn.execute(text("ALTER TABLE meeting ADD COLUMN titulo VARCHAR(120) DEFAULT ''"))
                # event final date column
                res3 = conn.execute(text("PRAGMA table_info(event);"))
                cols3 = [row[1] for row in res3]
                if 'data_final' not in cols3:
                    # default to distant future if missing
                    conn.execute(text("ALTER TABLE event ADD COLUMN data_final DATE NOT NULL DEFAULT '2099-12-31'"))
                # region table and user region_id
                res4 = conn.execute(text("PRAGMA table_info(region);"))
                cols4 = [row[1] for row in res4]
                if not cols4:
                    conn.execute(text("CREATE TABLE region (id INTEGER PRIMARY KEY AUTOINCREMENT, nome VARCHAR(50) UNIQUE NOT NULL)"))
                res5 = conn.execute(text("PRAGMA table_info(user);"))
                cols5 = [row[1] for row in res5]
                if 'region_id' not in cols5:
                    conn.execute(text('ALTER TABLE user ADD COLUMN region_id INTEGER'))
        # default administrator credentials (same as in app/__init__)
        telefone = ''.join(ch for ch in os.environ.get('DEFAULT_ADMIN_PHONE', '14981364342') if ch.isdigit())
        senha = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'jr34139251')
        user = User.query.filter_by(telefone=telefone).first()
        if user is None:
            user = User(telefone=telefone, nome='Arnaldo Martins Hidalgo Junior', cor='azul celeste')
        else:
            # ensure name and color are updated
            user.nome = 'Arnaldo Martins Hidalgo Junior'
            user.cor = 'azul celeste'
        db.session.add(user)
        db.session.commit()
        if not user.admin_record:
            admin = Admin(user_id=user.id, is_original=True)
            admin.set_password(senha)
            db.session.add(admin)
            db.session.commit()
        print('Original administrator ensured.')
        # ensure default regions exist
        from app.models import Region, Setting
        default = ['Branco', 'black', 'verde', 'azul marinho', 'azul celeste', 'vinho novo', 'roxa', 'amarelo', 'laranja']
        for name in default:
            up = name.strip().upper()
            if not Region.query.filter_by(nome=up).first():
                db.session.add(Region(nome=up))
        db.session.commit()
        # ensure basic settings exist
        if not Setting.get('API_TOKEN'):
            Setting.set('API_TOKEN', secrets.token_urlsafe(16))
        # if SMTP env vars provided (e.g. MailHog) copy them into db settings
        # other keys left blank until configured

        # create a sample event/meeting/qrcode for testing
        from app.models import Event, Meeting, QRCode
        ev = Event.query.filter_by(nome='Evento de Teste').first()
        if ev is None:
            today = datetime.utcnow().date()
            ev = Event(nome='Evento de Teste', data_inicial=today, data_final=today)
            db.session.add(ev)
            db.session.commit()
        mt = Meeting.query.filter_by(event_id=ev.id).first()
        if mt is None:
            mt = Meeting(event=ev, titulo='Reunião de Teste', data=datetime.utcnow().date())
            db.session.add(mt)
            db.session.commit()
        else:
            if not mt.titulo:
                mt.titulo = 'Reunião de Teste'
                db.session.commit()
        if not QRCode.query.filter_by(meeting_id=mt.id).first():
            token = secrets.token_urlsafe(16)
            q = QRCode(meeting=mt, token=token)
            db.session.add(q)
            db.session.commit()
        print('Sample event/meeting/qr is present for testing.')


if __name__ == '__main__':
    create_original_admin()
