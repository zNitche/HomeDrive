from home_drive import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(90), nullable=False)
    can_delete_files = db.Column(db.Boolean, default=False, nullable=False)
    have_private_space = db.Column(db.Boolean, default=False, nullable=False)
    can_upload = db.Column(db.Boolean, default=False, nullable=False)
    max_files_size = db.Column(db.Integer, default=0,  nullable=False)
