from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import StatusEnum, User
from app import app, db
from app.forms import LoginForm, RegistrationForm, JobUrlForm, InfoForm
import app.services.job_services as job_services

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
    url_form = JobUrlForm()
    info_form = InfoForm()
    if request.method == 'POST':

        has_url = bool(url_form.data and url_form.url.data.strip())
        has_title = bool(info_form.data and info_form.job_title.data.strip())
        has_company = bool(info_form.data and info_form.job_company.data.strip())

        print(f"Flags -> URL: {has_url} | Title: {has_title} | Company: {has_company}", flush=True)

        if has_url:
            if url_form.data and url_form.validate_on_submit():

                job_url = url_form.url.data

                status = job_services.create_job_from_url(job_url, current_user.id, db)
                if status is job_services.JobOperationStatus.UNSUPPORTED_DOMAIN:
                    flash('This domain is currently unsupported; manual entry of job details required')
                    return redirect(url_for('dashboard'))
                if status is job_services.JobOperationStatus.EXISTS: 
                    flash('You have already saved this job.', 'warning')
                    return redirect(url_for('dashboard'))
                elif status is job_services.JobOperationStatus.NOTFOUND:
                    flash('User not found', 'warning')
                    return redirect(url_for('dashboard'))
                elif status is job_services.JobOperationStatus.COMMIT_FAILED:
                    flash('Internal Error. Job not saved', 'warning')
                elif status is job_services.JobOperationStatus.CREATED:
                    flash('Job saved!', 'success')
                    return redirect(url_for('dashboard'))
                
        elif has_title and has_company:
            if info_form.data and info_form.validate_on_submit():
                title = info_form.job_title.data
                company = info_form.job_company.data

                status = job_services.create_job_from_info(title, company, current_user.id, db)

                if status is job_services.JobOperationStatus.EXISTS: 
                    flash('FIXME - need verification message popup')
                    return redirect(url_for('dashboard'))
                elif status is job_services.JobOperationStatus.NOTFOUND:
                    flash('User not found', 'warning')
                    return redirect(url_for('dashboard'))
                elif status is job_services.JobOperationStatus.URL_NOTFOUND:
                    flash('Job saved, but automation could not find a matching URL. Edit your job record to add a URL', 'warning')
                    return redirect(url_for('dashboard'))
                elif status is job_services.JobOperationStatus.COMMIT_FAILED:
                    flash('Internal Error. Job not saved', 'warning')
                elif status is job_services.JobOperationStatus.CREATED:
                    flash('Job saved!', 'success')
                    return redirect(url_for('dashboard'))

        elif has_title or has_company:
            if not has_title:
                flash('Please enter a job title')
            elif not has_company:
                flash('Please enter a company name')

        else:
            flash('Please enter a job listing URL or fill out the job title and company')            

    # GET request logic

    job_listings, user_jobs = job_services.get_job_listings(current_user.id, db)
    return render_template('dashboard.html', url_form=url_form, info_form=info_form, job_listings=job_listings, user_jobs=user_jobs, status_enum=list(StatusEnum))

@app.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('profile.html', user=user)

@app.route('/dashboard/delete/<int:job_id>', methods=['POST'])
@login_required
def remove_job(job_id):
    # Find the association between the user and the job

    status = job_services.delete_job(job_id, current_user.id, db)

    if status is job_services.JobOperationStatus.DELETED:
        flash('Job removed successfully.')
    else:
        flash('Could not find the specified job.')

    return redirect(url_for('dashboard'))

@app.route('/dashboard/update-status/<int:job_id>', methods=['POST'])
@login_required
def update_status(job_id):
    status_str = request.form.get('status')

    status = job_services.update_job_status(job_id, current_user.id, status_str, db)

    if status == job_services.JobOperationStatus.UPDATED:
        flash('Application status updated.', 'success')
    else:
        flash('Job not found.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard/archive/<int:job_id>', methods=['POST'])
@login_required
def archive_application(job_id):

    status = job_services.archive_job(job_id, current_user.id, db)

    if status == job_services.JobOperationStatus.UPDATED:
        flash('Application archived', 'success')
    else:
        flash('Job not found.', 'danger')

    return redirect(url_for('dashboard'))