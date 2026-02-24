import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    # prefer explicit DATABASE_URL; fall back to sqlite file for local dev
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # use sqlite in project directory so that running without docker works
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'f2f.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANG = 'pt_BR'
    TZ = 'America/Sao_Paulo'
    # base URL used for external links (override with env var if needed)
    SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS', 'http://31.97.251.198:5000')

