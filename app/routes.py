"""
Resume Parser - Application Routes
====================================
Defines all HTTP endpoints:
- GET  /           → Upload page (home)
- POST /upload     → Upload and parse resume  
- GET  /resume/<id> → View parsed resume details
- GET  /resumes    → List all parsed resumes
- GET  /api/resume/<id> → JSON API for resume data
"""

import os
from functools import wraps
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, jsonify, current_app, session, send_from_directory
)
from werkzeug.utils import secure_filename
from app import db
from app.models import Resume, Education, Experience, Project, Skill, User
from app.services.parser import parse_resume

main = Blueprint('main', __name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'docx'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


@main.route('/')
@login_required
def index():
    """Home page with upload form."""
    recent_resumes = Resume.query.order_by(Resume.created_at.desc()).limit(5).all()
    return render_template('index.html', resumes=recent_resumes)


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')
            
    return render_template('login.html')


@main.route('/register', methods=['POST'])
def register():
    """Register logic."""
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(email=email).first():
        flash('Email address already exists', 'error')
        return redirect(url_for('main.login'))
        
    new_user = User(name=name, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id
    flash('Account created successfully!', 'success')
    return redirect(url_for('main.index'))


@main.route('/logout')
def logout():
    """Logout user."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


@main.route('/upload', methods=['POST'])
@login_required
def upload():
    """Handle resume file upload and parsing."""
    if 'resume' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('main.index'))

    file = request.files['resume']

    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('main.index'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a PDF or DOCX file.', 'error')
        return redirect(url_for('main.index'))

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Parse resume
        parsed = parse_resume(file_path)

        # Save to database
        resume = Resume(
            name=parsed.get('name'),
            email=parsed.get('email'),
            phone=parsed.get('phone'),
            linkedin_url=parsed.get('linkedin_url'),
            github_url=parsed.get('github_url'),
            summary=parsed.get('summary'),
            raw_text=parsed.get('raw_text'),
            file_name=filename,
            file_path=file_path,
        )
        db.session.add(resume)
        db.session.flush()  # Get resume.id

        # Add education entries
        for edu in parsed.get('education', []):
            education = Education(
                resume_id=resume.id,
                institution=edu.get('institution'),
                degree=edu.get('degree'),
                field_of_study=edu.get('field_of_study'),
                start_date=edu.get('start_date'),
                end_date=edu.get('end_date'),
                gpa=edu.get('gpa'),
            )
            db.session.add(education)

        # Add experience entries
        for exp in parsed.get('experience', []):
            experience = Experience(
                resume_id=resume.id,
                company=exp.get('company'),
                job_title=exp.get('job_title'),
                start_date=exp.get('start_date'),
                end_date=exp.get('end_date'),
                description=exp.get('description'),
            )
            db.session.add(experience)

        # Add projects
        for proj in parsed.get('projects', []):
            proj_title = proj.get('title') or 'Project'
            if proj_title or proj.get('description'):
                project = Project(
                    resume_id=resume.id,
                    title=proj_title,
                    description=proj.get('description'),
                    technologies=proj.get('technologies'),
                    link=proj.get('link'),
                )
                db.session.add(project)

        # Add skills
        for skill in parsed.get('skills', []):
            s = Skill(
                resume_id=resume.id,
                skill_name=skill.get('skill_name'),
                category=skill.get('category'),
            )
            db.session.add(s)

        db.session.commit()
        flash(f'Resume parsed successfully!', 'success')
        return redirect(url_for('main.resume_detail', resume_id=resume.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing resume: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@main.route('/resume/<int:resume_id>')
@login_required
def resume_detail(resume_id):
    """Display parsed resume details."""
    resume = Resume.query.get_or_404(resume_id)
    return render_template('resume_detail.html', resume=resume)


@main.route('/resumes')
@login_required
def resume_list():
    """List all parsed resumes."""
    resumes = Resume.query.order_by(Resume.created_at.desc()).all()
    return render_template('resume_list.html', resumes=resumes)


@main.route('/uploads/<path:filename>')
@login_required
def serve_resume(filename):
    """Serve uploaded resume file."""
    # Ensure the path is absolute relative to the project root, not the app module
    upload_folder = os.path.abspath(os.path.join(current_app.root_path, '..', current_app.config['UPLOAD_FOLDER']))
    return send_from_directory(upload_folder, filename)


@main.route('/api/resume/<int:resume_id>')
def api_resume(resume_id):
    """JSON API endpoint for resume data."""
    resume = Resume.query.get_or_404(resume_id)
    return jsonify(resume.to_dict())


@main.route('/delete/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    """Delete a resume and its associated records."""
    resume = Resume.query.get_or_404(resume_id)

    # Delete the uploaded file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.session.delete(resume)
    db.session.commit()
    flash('Resume deleted successfully.', 'success')
    return redirect(url_for('main.resume_list'))
