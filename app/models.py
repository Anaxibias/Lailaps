from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(255), unique=True, nullable=False)
    password: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    jobs: so.WriteOnlyMapped['Job'] = so.relationship(secondary='user_jobs', back_populates='users')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, pw):
        self.password = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password, pw)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Job(db.Model):
    __tablename__ = 'jobs'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    job_title: so.Mapped[str] = so.mapped_column(sa.String(255))
    company: so.Mapped[str] = so.mapped_column(sa.String(255))
    source: so.Mapped[str] = so.mapped_column(sa.Text)
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    users: so.WriteOnlyMapped['User'] = so.relationship(secondary='user_jobs', back_populates='jobs')

    def __repr__(self):
        return f'<Job {self.job_title}>'

class UserJob(db.Model):
    __tablename__ = 'user_jobs'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    job_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('jobs.id'))
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    applied: so.Mapped[Optional[bool]] = so.mapped_column(sa.Boolean, nullable=True)

    def __repr__(self):
        return f'<UserJob user_id={self.user_id} job_id={self.job_id}>'
