"""
Resume Parser - SQLAlchemy Database Models
==========================================
Defines the database models that mirror the schema.sql structure:
- Resume: Main resume record with personal info
- Education: Education entries (one-to-many with Resume)
- Experience: Work experience entries (one-to-many with Resume)
- Skill: Individual skills with categories (one-to-many with Resume)
"""

from datetime import datetime, timezone
from app import db


class Resume(db.Model):
    """Main resume record containing personal info and raw text."""

    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    linkedin_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    summary = db.Column(db.Text)
    raw_text = db.Column(db.Text)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    education = db.relationship(
        'Education', backref='resume', lazy=True, cascade='all, delete-orphan'
    )
    experience = db.relationship(
        'Experience', backref='resume', lazy=True, cascade='all, delete-orphan'
    )
    projects = db.relationship(
        'Project', backref='resume', lazy=True, cascade='all, delete-orphan'
    )
    skills = db.relationship(
        'Skill', backref='resume', lazy=True, cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert resume and all related records to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'summary': self.summary,
            'file_name': self.file_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'education': [edu.to_dict() for edu in self.education],
            'experience': [exp.to_dict() for exp in self.experience],
            'projects': [proj.to_dict() for proj in self.projects],
            'skills': [skill.to_dict() for skill in self.skills],
        }

    def __repr__(self):
        return f'<Resume {self.id}: {self.name}>'


class Education(db.Model):
    """Education entry linked to a resume."""

    __tablename__ = 'education'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(
        db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False
    )
    institution = db.Column(db.String(255))
    degree = db.Column(db.String(255))
    field_of_study = db.Column(db.String(255))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    gpa = db.Column(db.String(20))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert education record to a dictionary."""
        return {
            'id': self.id,
            'institution': self.institution,
            'degree': self.degree,
            'field_of_study': self.field_of_study,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'gpa': self.gpa,
        }

    def __repr__(self):
        return f'<Education {self.id}: {self.degree} at {self.institution}>'


class Experience(db.Model):
    """Work experience entry linked to a resume."""

    __tablename__ = 'experience'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(
        db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False
    )
    company = db.Column(db.String(255))
    job_title = db.Column(db.String(255))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    description = db.Column(db.Text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert experience record to a dictionary."""
        return {
            'id': self.id,
            'company': self.company,
            'job_title': self.job_title,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'description': self.description,
        }

    def __repr__(self):
        return f'<Experience {self.id}: {self.job_title} at {self.company}>'


class Project(db.Model):
    """Project entry linked to a resume."""

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(
        db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False
    )
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    technologies = db.Column(db.String(500))
    link = db.Column(db.String(500))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert project record to a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'technologies': self.technologies,
            'link': self.link,
        }

    def __repr__(self):
        return f'<Project {self.id}: {self.title}>'


class Skill(db.Model):
    """Individual skill linked to a resume with category classification."""

    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(
        db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False
    )
    skill_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert skill record to a dictionary."""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'category': self.category,
        }

    def __repr__(self):
        return f'<Skill {self.id}: {self.skill_name} ({self.category})>'
