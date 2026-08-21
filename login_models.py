from datetime import datetime

from models import db


class UserLoginEvent(db.Model):
    """Persistent authentication audit trail.

    Passwords are intentionally never stored here. The users table stores only
    a one-way password hash, which is enough to verify future logins without
    retaining a readable password.
    """

    __tablename__ = "user_login_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    event_type = db.Column(db.String(30), nullable=False, index=True)
    occurred_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref=db.backref("login_events", lazy=True))
