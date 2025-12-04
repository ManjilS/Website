from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
# Removed email sending to simplify deployment on Render
import sqlite3
from datetime import datetime
import os
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'necsprint-admin-secret-key-2024-change-in-production')

# Email configuration - Using a simple SMTP setup
# Mail configuration removed

# Database configuration
DB_PATH = os.environ.get('DATABASE_PATH', 'registrations.db')

def get_conn():
    # Use a connection timeout and allow cross-thread access in Gunicorn workers
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    try:
        conn.execute('PRAGMA busy_timeout=5000')
    except Exception:
        pass
    return conn

def execute_with_retry(cursor, query, params=(), retries=5, delay=0.2):
    for attempt in range(retries):
        try:
            cursor.execute(query, params)
            return True
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e).lower() and attempt < retries - 1:
                time.sleep(delay)
                continue
            raise

# Admin credentials (in production, use environment variables or database)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'necsprint2024')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    # Ensure directory exists for DB_PATH if a nested path is provided
    try:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    except Exception:
        pass

    conn = get_conn()
    cursor = conn.cursor()
    # Enable WAL for better concurrency on Render
    try:
        cursor.execute('PRAGMA journal_mode=WAL')
    except Exception:
        pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            leader_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            university TEXT NOT NULL,
            theme TEXT NOT NULL,
            team_members TEXT,
            github_link TEXT,
            proposal_file TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migrate old schema: drop experience_level if still present
    try:
        cursor.execute("PRAGMA table_info(registrations)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'experience_level' in cols:
            # Attempt direct drop (SQLite >= 3.35 supports DROP COLUMN)
            try:
                cursor.execute('ALTER TABLE registrations DROP COLUMN experience_level')
                conn.commit()
            except sqlite3.OperationalError:
                # Fallback: recreate table without experience_level
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS registrations_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        team_name TEXT NOT NULL,
                        leader_name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        university TEXT NOT NULL,
                        theme TEXT NOT NULL,
                        team_members TEXT,
                        github_link TEXT,
                        proposal_file TEXT,
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cursor.execute('''
                    INSERT INTO registrations_new (id, team_name, leader_name, email, university, theme, team_members, github_link, proposal_file, registration_date)
                    SELECT id, team_name, leader_name, email, university, theme, team_members, github_link, proposal_file, registration_date FROM registrations
                ''')
                cursor.execute('DROP TABLE registrations')
                cursor.execute('ALTER TABLE registrations_new RENAME TO registrations')
                conn.commit()
    except Exception:
        pass
    
    # Add team_members column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE registrations ADD COLUMN team_members TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
    # Add github_link column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE registrations ADD COLUMN github_link TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    # Add proposal_file column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE registrations ADD COLUMN proposal_file TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    # Add phone column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE registrations ADD COLUMN phone TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            email TEXT NOT NULL,
            project_title TEXT NOT NULL,
            description TEXT NOT NULL,
            github_url TEXT NOT NULL,
            demo_url TEXT,
            video_url TEXT,
            theme TEXT NOT NULL,
            presentation_file TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            file_path TEXT,
            original_filename TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add new columns to existing notices table if they don't exist
    try:
        cursor.execute('ALTER TABLE notices ADD COLUMN file_path TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE notices ADD COLUMN original_filename TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return redirect(url_for('admin_login'))

@app.route('/admin/login')
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    data = request.get_json()
    
    if data['username'] == ADMIN_USERNAME and data['password'] == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/submit')
def submit_page():
    return render_template('submit.html')

@app.route('/live')
def live_updates():
    return render_template('live.html')

@app.route('/stream')
def live_stream():
    return render_template('stream.html')

@app.route('/notices')
def notices_page():
    return render_template('notices.html')

@app.route('/documents')
def documents_page():
    return render_template('documents.html')

@app.route('/admin/add-notice', methods=['POST'])
@login_required
def add_notice():
    content = request.form.get('content')
    file_path = None
    original_filename = None
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            original_filename = filename
            file_path = unique_filename
    
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notices (content, file_path, original_filename) VALUES (?, ?, ?)', 
                   (content, file_path, original_filename))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/delete-notice/<int:notice_id>', methods=['DELETE'])
@login_required
def delete_notice(notice_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notices WHERE id = ?', (notice_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/delete-submission/<int:submission_id>', methods=['DELETE'])
@login_required
def delete_submission(submission_id):
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM submissions WHERE id = ?', (submission_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/upload-document', methods=['POST'])
@login_required
def upload_document():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['file']
    title = request.form.get('title')
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO documents (title, description, filename, original_filename, file_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, unique_filename, filename, filename.rsplit('.', 1)[1].lower()))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Document uploaded successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid file type. Only PDF, DOC, DOCX allowed'})

@app.route('/admin/documents')
@login_required
def get_admin_documents():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, original_filename, file_type, created_at FROM documents ORDER BY created_at DESC')
    documents = [{
        'id': row[0], 'title': row[1], 'description': row[2], 
        'filename': row[3], 'file_type': row[4], 'created_at': row[5]
    } for row in cursor.fetchall()]
    conn.close()
    return jsonify(documents)

@app.route('/admin/delete-document/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM documents WHERE id = ?', (doc_id,))
    result = cursor.fetchone()
    
    if result:
        filename = result[0]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/download/notice/<int:notice_id>')
def download_notice_file(notice_id):
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT file_path, original_filename FROM notices WHERE id = ?', (notice_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        file_path, original_filename = result
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        if os.path.exists(full_path):
            from flask import send_file
            return send_file(full_path, as_attachment=True, download_name=original_filename)
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/notice/<int:notice_id>')
def notice_details(notice_id):
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, content, file_path, original_filename, created_at FROM notices WHERE id = ? AND is_active = 1', (notice_id,))
    notice = cursor.fetchone()
    conn.close()
    
    if notice:
        notice_data = {
            'id': notice[0],
            'content': notice[1], 
            'file_path': notice[2],
            'original_filename': notice[3],
            'created_at': notice[4]
        }
        return render_template('notice_details.html', notice=notice_data)
    
    return jsonify({'error': 'Notice not found'}), 404

@app.route('/view/notice/<int:notice_id>')
def view_notice_file(notice_id):
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT file_path, original_filename FROM notices WHERE id = ?', (notice_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        file_path, original_filename = result
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        if os.path.exists(full_path) and original_filename.lower().endswith('.pdf'):
            from flask import send_file
            return send_file(full_path, mimetype='application/pdf')
    
    return jsonify({'error': 'File not found or not viewable'}), 404

@app.route('/api/documents')
def get_public_documents():
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, original_filename, file_type, created_at FROM documents ORDER BY created_at DESC')
    documents = [{
        'id': row[0], 'title': row[1], 'description': row[2], 
        'filename': row[3], 'file_type': row[4], 'created_at': row[5]
    } for row in cursor.fetchall()]
    conn.close()
    return jsonify(documents)

@app.route('/api/notices')
def get_notices():
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM notices WHERE is_active = 1 ORDER BY created_at DESC')
    notices = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(notices)

@app.route('/admin/notices')
@login_required
def get_admin_notices():
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, content, file_path, original_filename, created_at FROM notices WHERE is_active = 1 ORDER BY created_at DESC')
    notices = [{'id': row[0], 'content': row[1], 'file_path': row[2], 'original_filename': row[3], 'created_at': row[4]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(notices)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    try:
        # Support JSON (legacy) and multipart/form-data (new page)
        is_multipart = request.content_type and 'multipart/form-data' in request.content_type
        if is_multipart:
            form = request.form
            data = {
                'teamName': form.get('teamName'),
                'leaderName': form.get('leaderName'),
                'email': form.get('email'),
                'phone': form.get('phone', ''),
                'university': form.get('university'),
                'theme': form.get('theme'),
                'githubLink': form.get('githubLink', '')
            }
        else:
            data = request.get_json()
        
        conn = get_conn()
        cursor = conn.cursor()
        
        # Process team members
        team_members = []
        for i in range(1, 5):
            name_key = f'member{i}Name'
            email_key = f'member{i}Email'
            if name_key in data and data[name_key]:
                team_members.append({
                    'name': data[name_key],
                    'email': data.get(email_key, '')
                })
        
        import json
        team_members_json = json.dumps(team_members) if team_members else None
        
        # Optional proposal file upload
        saved_proposal = None
        if is_multipart and 'proposal' in request.files:
            file = request.files['proposal']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(file_path)
                saved_proposal = unique_filename
        
        execute_with_retry(cursor, '''
            INSERT INTO registrations (team_name, leader_name, email, phone, university, theme, team_members, github_link, proposal_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['teamName'],
            data['leaderName'],
            data['email'],
            data.get('phone', ''),
            data['university'],
            data['theme'],
            team_members_json,
            (data.get('githubLink') if isinstance(data, dict) else ''),
            saved_proposal
        ))
        
        conn.commit()
        conn.close()
        
        # Email sending removed for Render deployment stability
        
        return jsonify({'success': True, 'message': 'Registration successful! Welcome to TechSprint! Check your email for confirmation details.'})
    
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already registered!'})
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'message': 'Registration failed!'})

@app.route('/registrations', methods=['GET'])
@login_required
def get_registrations():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, team_name, leader_name, email, phone, university, theme, team_members, registration_date
        FROM registrations ORDER BY registration_date DESC
    ''')
    registrations = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': r[0],
        'team_name': r[1],
        'leader_name': r[2],
        'email': r[3],
        'phone': r[4],
        'university': r[5],
        'theme': r[6],
        'team_members': r[7],
        'registration_date': r[8]
    } for r in registrations])

@app.route('/admin/export')
@login_required
def export_registrations():
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, team_name, leader_name, email, phone, university, theme, team_members, registration_date
        FROM registrations ORDER BY registration_date DESC
    ''')
    registrations = cursor.fetchall()
    conn.close()
    
    import csv
    import io
    from flask import make_response
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Team Name', 'Leader Name', 'Email', 'Phone', 'University', 'Theme', 'Team Members', 'Registration Date'])
    
    for reg in registrations:
        writer.writerow(reg)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=registrations.csv'
    return response

@app.route('/submit-project', methods=['POST'])
def submit_project():
    try:
        data = request.form
        
        # Handle file upload
        presentation_file = None
        if 'presentation' in request.files:
            file = request.files['presentation']
            if file.filename:
                import os
                upload_folder = 'uploads'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                presentation_file = f"{upload_folder}/{data['teamName']}_{file.filename}"
                file.save(presentation_file)
        
        conn = sqlite3.connect('registrations.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO submissions (team_name, email, project_title, description, github_url, demo_url, video_url, theme, presentation_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['teamName'],
            data['email'],
            data['projectTitle'],
            data['description'],
            data['githubUrl'],
            data.get('demoUrl', ''),
            data.get('videoUrl', ''),
            data['theme'],
            presentation_file
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Project submitted successfully!'})
    
    except Exception as e:
        print(f"Submission error: {e}")
        return jsonify({'success': False, 'message': 'Submission failed!'})

@app.route('/submissions')
@login_required
def view_submissions():
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM submissions ORDER BY submission_date DESC')
    submissions = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': s[0],
        'team_name': s[1],
        'email': s[2],
        'project_title': s[3],
        'description': s[4],
        'github_url': s[5],
        'demo_url': s[6],
        'video_url': s[7],
        'theme': s[8],
        'presentation_file': s[9],
        'submission_date': s[10]
    } for s in submissions])

@app.route('/send-notification', methods=['POST'])
@login_required
def send_notification():
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('registrations.db')
        cursor = conn.cursor()
        
        # Get recipients based on selection
        if data['recipients'] == 'all':
            cursor.execute('SELECT email, leader_name FROM registrations')
        else:
            cursor.execute('SELECT email, leader_name FROM registrations WHERE theme = ?', (data['recipients'],))
        
        recipients = cursor.fetchall()
        conn.close()
        
        # Send emails
        sent_count = 0
        for email, name in recipients:
            try:
                msg = Message(
                    data['subject'],
                    recipients=[email]
                )
                msg.html = f'''
                <h2>{data['subject']}</h2>
                <p>Hi {name},</p>
                <p>{data['message']}</p>
                <p>Best regards,<br>NECSprint Team</p>
                '''
                mail.send(msg)
                sent_count += 1
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'Notification sent to {sent_count} recipients'
        })
    
    except Exception as e:
        print(f"Notification error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send notifications'})

@app.route('/admin/delete-registration/<int:registration_id>', methods=['DELETE'])
@login_required
def delete_registration(registration_id):
    try:
        conn = sqlite3.connect('registrations.db')
        cursor = conn.cursor()
        
        # Check if registration exists
        cursor.execute('SELECT id FROM registrations WHERE id = ?', (registration_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Registration not found'})
        
        # Delete the registration
        cursor.execute('DELETE FROM registrations WHERE id = ?', (registration_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Registration deleted successfully'})
    
    except Exception as e:
        print(f"Delete error: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete registration'})

@app.route('/admin/announcements')
@login_required
def get_announcements():
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM announcements ORDER BY created_at DESC')
    announcements = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': a[0],
        'title': a[1],
        'content': a[2],
        'created_at': a[3]
    } for a in announcements])

@app.route('/admin/add-announcement', methods=['POST'])
@login_required
def add_announcement():
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('registrations.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO announcements (title, content)
            VALUES (?, ?)
        ''', (data['title'], data['content']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Announcement added successfully'})
    
    except Exception as e:
        print(f"Add announcement error: {e}")
        return jsonify({'success': False, 'message': 'Failed to add announcement'})

@app.route('/admin/delete-announcement/<int:announcement_id>', methods=['DELETE'])
@login_required
def delete_announcement(announcement_id):
    try:
        conn = sqlite3.connect('registrations.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Announcement deleted successfully'})
    
    except Exception as e:
        print(f"Delete announcement error: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete announcement'})

@app.route('/api/announcements')
def public_announcements():
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM announcements ORDER BY created_at DESC LIMIT 10')
    announcements = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': a[0],
        'title': a[1],
        'content': a[2],
        'created_at': a[3]
    } for a in announcements])

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)