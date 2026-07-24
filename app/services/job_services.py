from enum import Enum, auto
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from app.models import User, Job, UserJob, StatusEnum
from .external import fetch_job_details, fetch_job_url

class JobOperationStatus(Enum):
    CREATED = auto()
    EXISTS = auto()
    NOTFOUND = auto()
    DELETED = auto()
    UPDATED = auto()
    UNSUPPORTED_DOMAIN = auto()
    URL_NOTFOUND = auto()
    COMMIT_FAILED = auto()


def create_job_from_url(job_url, user_id, db):

    user = db.session.get(User, user_id)

    if not user:
        return JobOperationStatus.NOTFOUND

    existing_job = db.session.scalar(user.jobs.select().where(Job.source == job_url))
    
    if existing_job:
        return JobOperationStatus.EXISTS
        
    # If not, proceed to add it
    job = db.session.scalar(sa.select(Job).where(Job.source == job_url))
    
    if job is None:
        title, company = fetch_job_details(job_url)

        job = Job(source=job_url, job_title=title, company=company, description="")

    try:
        job.users.add(user)
        db.session.add(job)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return JobOperationStatus.COMMIT_FAILED

    return JobOperationStatus.CREATED

def create_job_from_info(job_title, job_company, user_id, db):

    user = db.session.get(User, user_id)

    if not user:
        return JobOperationStatus.NOTFOUND

    existing_job = db.session.scalar(user.jobs.select().where(Job.job_title == job_title, Job.company == job_company))

    if existing_job:
        return JobOperationStatus.EXISTS

    job = db.session.scalar(sa.select(Job).where(Job.job_title == job_title, Job.company == job_company))

    if job is None:
        url = fetch_job_url(job_title, job_company)

        job = Job(source=url, job_title=job_title, company=job_company, description="")

    try:
        job.users.add(user)
        db.session.add(job)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return JobOperationStatus.COMMIT_FAILED


    if job.source == "":
        return JobOperationStatus.URL_NOTFOUND

    return JobOperationStatus.CREATED

def get_job_listings(user_id, db):
    job_listings = db.session.execute(
        sa.select(Job, UserJob).join(UserJob).where(UserJob.user_id == user_id)
    ).all()
    user_jobs = db.session.execute(
        sa.select(UserJob).where(UserJob.user_id == user_id)
    ).all()

    return job_listings, user_jobs

def delete_job(job_id, user_id, db):

    job_to_delete = db.session.scalar(
        sa.select(UserJob).where(
            UserJob.job_id == job_id,
            UserJob.user_id == user_id
            )
        )
     
    if job_to_delete:
        db.session.delete(job_to_delete)
        db.session.commit()
        return JobOperationStatus.DELETED
    else:
        return JobOperationStatus.NOTFOUND

def update_job_status(job_id, user_id, status, db):

    app_status = StatusEnum(status)

    job_to_update = db.session.scalar(sa.select(UserJob).where(UserJob.job_id == job_id, UserJob.user_id == user_id))
    
    if job_to_update:
        job_to_update.application_status = app_status
        db.session.commit()
    else:
        return JobOperationStatus.NOTFOUND

    return JobOperationStatus.UPDATED

def archive_job(job_id, user_id, db):

    job_to_update = db.session.scalar(sa.select(UserJob).where(UserJob.job_id == job_id, UserJob.user_id == user_id))
    
    if job_to_update:
        job_to_update.is_archived = True
        job_to_update.application_status = StatusEnum.ARCHIVED
        db.session.commit()
    else:
        return JobOperationStatus.NOTFOUND

    return JobOperationStatus.UPDATED