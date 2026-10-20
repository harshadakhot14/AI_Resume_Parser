"""
Resume Parser - Parsing Service
================================
Extracts text from PDF/DOCX files and uses NLP (spaCy) & regex patterns
to extract structured resume fields: contact details, summary, education,
work experience (with company, title, dates & descriptions), projects, and skills.
"""

import re
import fitz  # PyMuPDF
import docx2txt
import spacy

# Load spaCy English model (small)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None


# ---------------------
# Common skill keywords
# ---------------------
PROGRAMMING_LANGUAGES = {
    'python', 'java', 'javascript', 'c', 'c++', 'c#', 'ruby', 'go', 'golang',
    'rust', 'swift', 'kotlin', 'typescript', 'php', 'r', 'scala', 'perl',
    'matlab', 'dart', 'lua', 'haskell', 'objective-c', 'assembly',
    'visual basic', 'vb.net', 'groovy', 'elixir', 'clojure', 'fortran',
    'cobol', 'sql', 'html', 'css', 'sass', 'less', 'shell', 'bash',
    'powershell', 'xml', 'json', 'yaml',
}

FRAMEWORKS = {
    'react', 'react.js', 'angular', 'vue', 'vue.js', 'django', 'flask', 'spring',
    'spring boot', 'express', 'express.js', 'node.js', 'nodejs', 'nextjs',
    'next.js', 'nuxt', 'nuxt.js', 'rails', 'ruby on rails', 'laravel',
    'fastapi', 'asp.net', '.net', '.net core', 'bootstrap', 'tailwind',
    'tailwindcss', 'jquery', 'svelte', 'ember', 'backbone', 'gatsby',
    'flutter', 'react native', 'electron', 'tensorflow', 'pytorch',
    'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'opencv',
    'hadoop', 'spark', 'kafka', 'streamlit', 'langchain', 'faiss',
}

DATABASES = {
    'mysql', 'postgresql', 'postgres', 'mongodb', 'sqlite', 'oracle',
    'sql server', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
    'firebase', 'mariadb', 'couchdb', 'neo4j', 'influxdb', 'supabase',
}

TOOLS = {
    'git', 'github', 'gitlab', 'bitbucket', 'docker', 'kubernetes', 'k8s',
    'jenkins', 'ci/cd', 'aws', 'azure', 'gcp', 'google cloud', 'heroku',
    'vercel', 'netlify', 'linux', 'unix', 'windows', 'macos', 'nginx',
    'apache', 'terraform', 'ansible', 'jira', 'confluence', 'slack',
    'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'postman',
    'swagger', 'graphql', 'rest', 'restful', 'api', 'agile', 'scrum',
    'kanban', 'devops', 'microservices', 'serverless', 'vs code',
    'intellij', 'eclipse', 'vim', 'webpack', 'vite', 'npm', 'yarn',
    'pip', 'maven', 'gradle', 'cmake', 'make', 'ocr', 'llm', 'rag',
}

ALL_SKILLS = {
    **{s: 'Programming Language' for s in PROGRAMMING_LANGUAGES},
    **{s: 'Framework' for s in FRAMEWORKS},
    **{s: 'Database' for s in DATABASES},
    **{s: 'Tool' for s in TOOLS},
}

MONTHS_REGEX = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
DATE_RANGE_REGEX = rf'(?:{MONTHS_REGEX}\s*\d{{4}}|\d{{4}})\s*[-–—\sTo]+\s*(?:Present|Current|{MONTHS_REGEX}\s*\d{{4}}|\d{{4}})'


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text.strip()


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    return docx2txt.process(file_path).strip()


def extract_text(file_path):
    """Extract text from a resume file (PDF or DOCX)."""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")


def extract_email(text):
    """Extract email address from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text):
    """Extract phone number from text."""
    patterns = [
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'(?:\+?\d{1,3}[-.\s]?)?\d{10}',
        r'(?:\+?\d{1,3}[-.\s]?)?\d{5}[-.\s]?\d{5}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def extract_linkedin(text):
    """Extract LinkedIn URL from text."""
    pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_github(text):
    """Extract GitHub URL from text."""
    pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_name(text):
    """Extract candidate name using spaCy NER or line heuristics."""
    first_lines = [line.strip() for line in text.split('\n') if line.strip()][:5]
    
    # Try spaCy NER on top lines first
    if nlp:
        header_text = '\n'.join(first_lines)
        doc = nlp(header_text)
        for ent in doc.ents:
            if ent.label_ == 'PERSON' and len(ent.text.split()) in (2, 3):
                return ent.text.strip()

    # Fallback to first line if it looks like a clean name (2-3 words, no digits/emails/URLs)
    for line in first_lines:
        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$', line) or re.match(r'^[A-Z\s]{4,30}$', line):
            if not any(char in line for char in ['@', 'http', 'www', ':', '+', '/']):
                return line.strip().title()

    return None


def extract_skills(text):
    """Extract skills from text by matching against known skill keywords."""
    text_lower = text.lower()
    found_skills = []
    seen = set()

    for skill, category in ALL_SKILLS.items():
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            display_name = skill.title() if len(skill) > 3 else skill.upper()
            if display_name.lower() not in seen:
                seen.add(display_name.lower())
                found_skills.append({
                    'skill_name': display_name,
                    'category': category,
                })

    return found_skills


def parse_sections(text):
    """
    Splits resume text into labeled sections (education, experience, projects, skills, summary).
    """
    sections = {}
    current_section = 'header'
    sections[current_section] = []

    lines = text.split('\n')
    
    # Section header patterns
    header_patterns = {
        'summary': r'^(?:OBJECTIVE|SUMMARY|PROFILE|ABOUT\s+ME)\b',
        'education': r'^(?:EDUCATION|ACADEMIC\s+BACKGROUND|QUALIFICATIONS)\b',
        'experience': r'^(?:EXPERIENCE|WORK\s+EXPERIENCE|EMPLOYMENT|PROFESSIONAL\s+EXPERIENCE|WORK\s+HISTORY)\b',
        'projects': r'^(?:PROJECTS?|PERSONAL\s+PROJECTS?|ACADEMIC\s+PROJECTS?|KEY\s+PROJECTS?|MAJOR\s+PROJECTS?|FEATURED\s+PROJECTS?|TECHNICAL\s+PROJECTS?|PROJECT\s+WORK|RELEVANT\s+PROJECTS?|PORTFOLIO|PROJECT\s+HIGHLIGHTS)\b',
        'skills': r'^(?:SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES)\b',
    }

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Check if line is a section header (short, uppercase or title-case)
        is_header = False
        if len(stripped) < 40:
            for sec_name, pattern in header_patterns.items():
                if re.match(pattern, stripped, re.IGNORECASE):
                    current_section = sec_name
                    if current_section not in sections:
                        sections[current_section] = []
                    is_header = True
                    break
        
        if not is_header:
            sections[current_section].append(stripped)

    # Convert line arrays to text blocks
    return {k: '\n'.join(v) for k, v in sections.items()}


def extract_summary(text, sections):
    """Extract summary/objective."""
    if 'summary' in sections and sections['summary']:
        return sections['summary'][:1000]

    # Fallback search
    pattern = r'(?:SUMMARY|PROFILE|OBJECTIVE|ABOUT\s*ME)[:\s]*\n([\s\S]*?)(?:\n\s*\n|\n[A-Z]{2,})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        summary = match.group(1).strip()
        if len(summary) > 20:
            return summary[:1000]
    return None


def extract_education(text, sections):
    """Extract structured education entries."""
    edu_text = sections.get('education', text)
    education_entries = []

    lines = [l.strip() for l in edu_text.split('\n') if l.strip()]
    if not lines:
        return education_entries

    current_entry = None
    degree_keywords = [
        'b.tech', 'btech', 'b.e', 'b.s', 'bachelor', 'm.tech', 'mtech', 'm.s',
        'master', 'ph.d', 'phd', 'diploma', 'hsc', 'ssc', 'secondary', 'degree'
    ]

    for line in lines:
        is_new_degree = any(dk in line.lower() for dk in degree_keywords)
        
        if is_new_degree or not current_entry:
            if current_entry:
                education_entries.append(current_entry)
            
            current_entry = {
                'degree': line,
                'institution': None,
                'field_of_study': None,
                'start_date': None,
                'end_date': None,
                'gpa': None,
            }

            # Check for GPA/percentage in degree line
            gpa_match = re.search(r'(?:CGPA|GPA|Percentage)[:\s]*([\d.]+%?)', line, re.IGNORECASE)
            if gpa_match:
                current_entry['gpa'] = gpa_match.group(1)

            # Check for year/dates in degree line
            date_match = re.search(r'(\d{4}(?:\s*[-–—]\s*\d{4})?)', line)
            if date_match:
                dates = date_match.group(1).split('-')
                current_entry['start_date'] = dates[0].strip()
                if len(dates) > 1:
                    current_entry['end_date'] = dates[1].strip()
        else:
            # Check if this line has institution or GPA/percentage details
            gpa_match = re.search(r'(?:CGPA|GPA|Percentage)[:\s]*([\d.]+%?)', line, re.IGNORECASE)
            if gpa_match and current_entry:
                current_entry['gpa'] = gpa_match.group(1)
            elif not current_entry['institution'] and not line.startswith(('CGPA', 'Percentage', 'GPA')):
                current_entry['institution'] = line
            elif not current_entry['start_date']:
                date_match = re.search(r'(\d{4}(?:\s*[-–—]\s*\d{4})?)', line)
                if date_match and current_entry:
                    current_entry['start_date'] = date_match.group(1)

    if current_entry:
        education_entries.append(current_entry)

    return education_entries


def extract_experience(text, sections):
    """
    Extract work experience entries with title, company, dates, and full description.
    """
    exp_text = sections.get('experience', '')
    if not exp_text:
        return extract_experience_fallback(text)

    entries = []
    lines = [l.strip() for l in exp_text.split('\n') if l.strip()]

    current_exp = None
    
    title_keywords = [
        'developer', 'engineer', 'architect', 'analyst', 'consultant',
        'intern', 'manager', 'lead', 'designer', 'administrator', 'specialist',
        'trainee', 'associate', 'head', 'officer', 'director'
    ]

    for line in lines:
        is_bullet = bool(re.match(r'^[•\-\*⁃▪\ufffd\d+\.]\s*', line))
        has_date = bool(re.search(DATE_RANGE_REGEX, line, re.IGNORECASE)) or bool(re.search(r'\b(?:20\d{2}|19\d{2})\b', line))
        has_title_kw = any(kw in line.lower() for kw in title_keywords)

        date_match = re.search(DATE_RANGE_REGEX, line, re.IGNORECASE)
        if not date_match:
            date_match = re.search(r'\b(?:20\d{2}|19\d{2})\s*[-–—\sTo]+\s*(?:20\d{2}|19\d{2}|Present|Current)\b', line, re.IGNORECASE)

        # If we have an existing experience block that is still gathering header info (title/company/date)
        if current_exp is not None and not is_bullet and len(current_exp['description_lines']) == 0:
            if date_match and not current_exp['start_date']:
                date_str = date_match.group(0)
                parts = re.split(r'[-–—\sTo]+', date_str)
                current_exp['start_date'] = parts[0].strip()
                current_exp['end_date'] = parts[1].strip() if len(parts) > 1 else 'Present'
                clean_line = re.sub(r'[-–—\sTo]+\s*(?:Present|Current|\d{4})', '', line, flags=re.IGNORECASE).strip()
                clean_line = re.sub(MONTHS_REGEX, '', clean_line, flags=re.IGNORECASE).strip()
                if clean_line and not current_exp['job_title']:
                    current_exp['job_title'] = clean_line
                elif clean_line and not current_exp['company'] and clean_line != current_exp['job_title']:
                    current_exp['company'] = clean_line
                continue
            elif has_title_kw and not current_exp['job_title']:
                current_exp['job_title'] = line
                continue
            elif not current_exp['company'] and not has_title_kw and len(line) < 60 and not has_date and not line.startswith(('•', '-', '*', '⁃', '▪', '')):
                current_exp['company'] = line
                continue

        # A new entry starts if line is a job title or date line (and current_exp already has description or full info)
        if (has_title_kw or (has_date and not is_bullet)) and not is_bullet:
            if current_exp and (current_exp['job_title'] or current_exp['company']):
                entries.append(current_exp)

            job_title = line if has_title_kw else None
            company = line if not has_title_kw else None
            start_date = None
            end_date = None

            if date_match:
                date_str = date_match.group(0)
                parts = re.split(r'[-–—\sTo]+', date_str)
                start_date = parts[0].strip()
                end_date = parts[1].strip() if len(parts) > 1 else 'Present'
                clean_line = re.sub(r'[-–—\sTo]+\s*(?:Present|Current|\d{4})', '', line, flags=re.IGNORECASE).strip()
                clean_line = re.sub(MONTHS_REGEX, '', clean_line, flags=re.IGNORECASE).strip()
                if has_title_kw:
                    job_title = clean_line if clean_line else line
                else:
                    company = clean_line if clean_line else line

            current_exp = {
                'job_title': job_title,
                'company': company,
                'start_date': start_date,
                'end_date': end_date,
                'description_lines': []
            }
        elif current_exp:
            if is_bullet:
                clean_bullet = re.sub(r'^[•\-\*⁃▪\ufffd\s]+', '', line)
                current_exp['description_lines'].append(f"• {clean_bullet}")
            else:
                current_exp['description_lines'].append(line)

    if current_exp and (current_exp['job_title'] or current_exp['company']):
        entries.append(current_exp)

    formatted_entries = []
    for exp in entries:
        desc = '\n'.join(exp['description_lines']).strip() if exp['description_lines'] else None
        title = exp['job_title'] or exp['company'] or 'Position'
        company = exp['company'] if exp['job_title'] and exp['company'] != exp['job_title'] else None
        
        formatted_entries.append({
            'job_title': title,
            'company': company,
            'start_date': exp['start_date'],
            'end_date': exp['end_date'],
            'description': desc,
        })

    return formatted_entries


def extract_experience_fallback(text):
    """Fallback experience extraction using title patterns."""
    experience = []
    title_patterns = [
        r'(?:Software|Senior|Junior|Lead|Staff|Principal|Full[\s-]?Stack|Front[\s-]?End|Back[\s-]?End|DevOps|Data|ML|AI|Cloud|QA|Gen\s+AI)\s*(?:Engineer|Developer|Architect|Analyst|Scientist|Manager|Consultant|Designer|Intern)',
        r'(?:Project|Product|Program|Engineering|Technical)\s+(?:Manager|Lead|Director|Coordinator)',
        r'(?:Web|Mobile|iOS|Android|System|Network|Database|Security)\s+(?:Developer|Engineer|Administrator|Admin|Analyst)',
    ]

    for pattern in title_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            title = match.group(0).strip()
            experience.append({
                'job_title': title,
                'company': None,
                'start_date': None,
                'end_date': None,
                'description': None,
            })
    return experience


def parse_project_block(proj_text):
    """
    Parses a block of text containing project details into structured project records.
    """
    if not proj_text:
        return []

    lines = [l.strip() for l in proj_text.split('\n') if l.strip()]
    if not lines:
        return []

    projects = []
    current_proj = None

    # Verbs and keywords commonly starting bullet/description lines
    description_starters = (
        'developed', 'created', 'built', 'implemented', 'designed', 'managed',
        'integrated', 'configured', 'achieved', 'utilizing', 'utilized',
        'engineered', 'spearheaded', 'constructed', 'maintained', 'deployed',
        'automated', 'optimized', 'enhanced', 'architected', 'worked',
        'responsible', 'used', 'leveraged', 'contributed', 'wrote',
        'role:', 'features:', 'key features:', 'responsibilities:'
    )

    header_pattern = r'^(?:PROJECTS?|PERSONAL\s+PROJECTS?|ACADEMIC\s+PROJECTS?|KEY\s+PROJECTS?|MAJOR\s+PROJECTS?|FEATURED\s+PROJECTS?|TECHNICAL\s+PROJECTS?|PROJECT\s+WORK|RELEVANT\s+PROJECTS?|PORTFOLIO|PROJECT\s+HIGHLIGHTS)[:\s]*$'

    for line in lines:
        if re.match(header_pattern, line, re.IGNORECASE):
            continue

        # 1. Bullet point check
        is_bullet = bool(re.match(r'^[•\-\*⁃▪\ufffd\d+\.]\s*', line))

        # 2. Tech stack line check
        tech_match = re.search(r'^(?:Technologies|Tech\s+Stack|Tools\s+Used|Tools|Built\s+With|Environment|Stack)[:\s]+(.*)', line, re.IGNORECASE)

        # 3. Link check
        link_match = re.search(r'(?:https?://[^\s><")]+|(?:www\.)?github\.com/[^\s><")]+)', line, re.IGNORECASE)

        line_lower = line.lower()
        is_desc_starter = any(line_lower.startswith(verb) for verb in description_starters)

        # Handle explicit tech stack line
        if tech_match and current_proj:
            tech_val = tech_match.group(1).strip()
            if tech_val:
                current_proj['technologies'] = tech_val
            continue

        # Handle explicit link line or link inside line
        if link_match and current_proj and not current_proj['link']:
            link_url = link_match.group(0)
            if not link_url.startswith('http'):
                link_url = 'https://' + link_url
            current_proj['link'] = link_url
            # If line contains ONLY the link (or "Link: https://..."), skip adding as description line
            clean_link_line = re.sub(r'^(?:Link|GitHub|Live|Demo|URL)[:\s]*', '', line, flags=re.IGNORECASE).strip()
            if clean_link_line == link_match.group(0):
                continue

        # Determine if this line is a new project title
        is_new_title = False
        if not is_bullet and not tech_match and not is_desc_starter:
            if current_proj is None:
                is_new_title = True
            elif len(current_proj['description_lines']) > 0 or current_proj['technologies'] or current_proj['link']:
                is_new_title = True
            elif len(line) < 70 and not line.endswith(('.', ',')):
                is_new_title = True

        if is_new_title:
            if current_proj and current_proj['title']:
                projects.append(current_proj)

            title_str = line
            tech_extracted = None
            link_extracted = None

            if link_match:
                link_url = link_match.group(0)
                if not link_url.startswith('http'):
                    link_url = 'https://' + link_url
                link_extracted = link_url
                title_str = title_str.replace(link_match.group(0), '').strip(' |-–—()[]:')

            # Extract tech stack embedded in title line (e.g., "Resume Parser | Python, Flask" or "Chatbot (React, Node)")
            if '|' in title_str:
                parts = title_str.split('|', 1)
                title_str = parts[0].strip()
                tech_extracted = parts[1].strip()
            elif re.search(r'\(([^)]+)\)', title_str):
                m = re.search(r'\(([^)]+)\)', title_str)
                inner = m.group(1).strip()
                if any(kw in inner.lower() for kw in ['python', 'java', 'react', 'node', 'sql', 'flask', 'html', 'css', 'js', 'aws', 'django', 'c++', 'c#', 'php', 'ruby', 'go', 'ai', 'ml', 'nlp']):
                    tech_extracted = inner
                    title_str = re.sub(r'\([^)]+\)', '', title_str).strip()

            current_proj = {
                'title': title_str if title_str else line,
                'technologies': tech_extracted,
                'description_lines': [],
                'link': link_extracted,
            }
        elif current_proj:
            clean_line = line
            if is_bullet:
                bullet_content = re.sub(r'^[•\-\*⁃▪\ufffd\s\d+\.]+', '', line).strip()
                clean_line = "- " + bullet_content
            current_proj['description_lines'].append(clean_line)

    if current_proj and current_proj['title']:
        projects.append(current_proj)

    formatted = []
    for proj in projects:
        desc = '\n'.join(proj['description_lines']).strip() if proj['description_lines'] else None
        formatted.append({
            'title': proj['title'],
            'technologies': proj['technologies'],
            'description': desc,
            'link': proj['link'],
        })

    return formatted


def extract_projects(text, sections):
    """
    Extract project entries with title, technologies, description, and link.
    """
    proj_text = sections.get('projects', '')
    if proj_text:
        projects = parse_project_block(proj_text)
        if projects:
            return projects

    # Fallback search if section header wasn't caught by parse_sections
    pattern = r'(?:PROJECTS?|PORTFOLIO|PROJECT\s+HIGHLIGHTS|KEY\s+PROJECTS)[:\s]*\n([\s\S]*?)(?:\n\s*\n[A-Z\s]{3,20}\n|\Z)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return parse_project_block(match.group(1).strip())

    return []


def parse_resume(file_path):
    """
    Main function: Parse a resume file and return structured data.

    Returns a dict with keys:
        name, email, phone, linkedin_url, github_url, summary,
        raw_text, skills, education, experience, projects
    """
    # Step 1: Extract raw text
    raw_text = extract_text(file_path)

    if not raw_text:
        raise ValueError("Could not extract any text from the file.")

    # Step 2: Split into section blocks
    sections = parse_sections(raw_text)

    # Step 3: Extract structured fields
    return {
        'name': extract_name(raw_text),
        'email': extract_email(raw_text),
        'phone': extract_phone(raw_text),
        'linkedin_url': extract_linkedin(raw_text),
        'github_url': extract_github(raw_text),
        'summary': extract_summary(raw_text, sections),
        'raw_text': raw_text,
        'skills': extract_skills(raw_text),
        'education': extract_education(raw_text, sections),
        'experience': extract_experience(raw_text, sections),
        'projects': extract_projects(raw_text, sections),
    }

