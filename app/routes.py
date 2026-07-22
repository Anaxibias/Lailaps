from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import StatusEnum, User, Job, UserJob
from app import app, db
from app.forms import LoginForm, RegistrationForm, JobUrlForm
from app.dtos import TrackedJob

@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = JobUrlForm()
    if request.method == 'POST':
        if form.validate():
            job_url = form.url.data
            
            existing_job = db.session.scalar(current_user.jobs.select().where(Job.source == job_url))
            
            if existing_job:
                flash('You have already saved this job.', 'warning')
                return redirect(url_for('dashboard'))

            # If not, proceed to add it
            job = db.session.scalar(sa.select(Job).where(Job.source == job_url))
            
            if job is None:
                job = Job(source=job_url, job_title="Unknown", company="Unknown", description="")
            
            job.users.add(current_user)
            db.session.add(job)
            db.session.commit()
            
            flash('Job saved!', 'success')
            return redirect(url_for('dashboard'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{error}", 'danger')
            return redirect(url_for('dashboard'))
    
    # GET request logic
    job_listings = db.session.execute(
        sa.select(Job, UserJob).join(UserJob).where(UserJob.user_id == current_user.id)
    ).all()
    user_jobs = db.session.execute(
        sa.select(UserJob).where(UserJob.user_id == current_user.id)
    ).all()
    return render_template('dashboard.html', form=form, job_listings=job_listings, user_jobs=user_jobs, status_enum=list(StatusEnum))

@app.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('profile.html', user=user)

@app.route('/dashboard/delete/<int:id>', methods=['POST'])
@login_required
def remove_job(id):
    # Find the association between the user and the job
    job_to_delete = db.session.scalar(
        sa.select(UserJob).where(
            UserJob.job_id == id,
            UserJob.user_id == current_user.id
        )
    )

    if job_to_delete:
        db.session.delete(job_to_delete)
        db.session.commit()
        flash('Job removed successfully.')
    else:
        flash('Could not find the specified job.')

    return redirect(url_for('dashboard'))

@app.route('/dashboard/update-status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    status_str = request.form.get('status')
    app_status = StatusEnum(status_str)

    job_to_update = db.session.scalar(sa.select(UserJob).where(UserJob.job_id == id, UserJob.user_id == current_user.id))

    if job_to_update:
        job_to_update.application_status = app_status
        db.session.commit()
        flash('Application status updated.', 'success')
    else:
        flash('Job not found.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard/archive/<int:id>', methods=['POST'])
@login_required
def archive_application(id):

    job_to_update = db.session.scalar(sa.select(UserJob).where(UserJob.job_id == id, UserJob.user_id == current_user.id))

    if job_to_update:
        job_to_update.is_archived = True
        job_to_update.application_status = StatusEnum.ARCHIVED
        db.session.commit()
        flash('Application archived', 'success')
    else:
        flash('Job not found.', 'danger')

    return redirect(url_for('dashboard'))