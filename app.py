from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from functools import wraps
import random
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

ALLOWED_EMAIL = 'shahed@gmail.com'  # Define the allowed email

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            flash('Please login first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp_email(email, otp):
    try:
        msg = Message('Your OTP for Login',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email])
        msg.body = f'Your OTP is: {otp}. This OTP will expire in 5 minutes.'
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

# Dictionary to store last execution times
last_execution_times = {
    1: 'Never',
    2: 'Never',
    3: 'Never',
    4: 'Never',
    5: 'Never'
}

import os

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Check if the provided email is the allowed one
        if email == ALLOWED_EMAIL:
            otp = generate_otp()  # Generate a 6-digit OTP
        else:
            otp = generate_otp(8)  # Generate an 8-digit OTP for other emails
        
        session['email'] = email
        session['otp'] = otp
        session['otp_created_at'] = datetime.now().timestamp()
        
        # Try to send email
        email_sent = send_otp_email(email, otp)
        if not email_sent:
            flash('Failed to send OTP email, but you can still see it on the next page for testing.')
        
        return redirect(url_for('verify_otp'))
    
    return render_template('login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('email')
    otp = session.get('otp')
    otp_created_at = session.get('otp_created_at')
    
    if not all([email, otp, otp_created_at]):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        
        # Check if OTP is expired (5 minutes)
        if datetime.now().timestamp() - otp_created_at > 300:  # 300 seconds = 5 minutes
            flash('OTP has expired. Please request a new one.')
            return redirect(url_for('login'))
        
        # Ensure OTP is exactly 6 digits
        if not entered_otp or len(entered_otp) != len(otp) or not entered_otp.isdigit():
            flash('Invalid OTP format')
            return redirect(url_for('verify_otp'))
        
        if entered_otp == otp:
            # Clear previous session data
            session.clear()
            # Set authenticated flag
            session['authenticated'] = True
            session['email'] = email
            flash('Successfully logged in!')
            return redirect(url_for('home'))
        else:
            flash('Invalid OTP')
    
    return render_template('verify_otp.html', otp=otp)

@app.route('/')
@login_required
def home():
    return render_template('home.html', email=session.get('email'), last_execution_times=last_execution_times)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Successfully logged out.')
    return redirect(url_for('login'))

@app.route('/run_process/<int:process_id>')
def run_process(process_id):
    process_files = [
        'test_process_1.sh',
        'test_process_2.sh',
        'test_process_3.sh',
        'test_process_4.sh',
        'test_process_5.sh'
    ]
    
    if process_id < 1 or process_id > len(process_files):
        return redirect(url_for('home'))
    
    process_file = f'./{process_files[process_id - 1]}'
    log_file_path = f'logs/process_{process_id}.log'
    with open(log_file_path, 'w') as log_file:
        process = subprocess.Popen(['bash', process_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in iter(process.stdout.readline, ''):
            log_file.write(line)  # Write to log file
            print(line, end='')  # Optional: print to server console
        process.stdout.close()
        process.wait()
    last_execute_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    last_execution_times[process_id] = last_execute_time  # Update last execution time
    flash(f'Process {process_id} executed successfully! Last executed at {last_execute_time}.')
    
    return redirect(url_for('home'))

@app.route('/view_log/<int:process_id>')
def view_log(process_id):
    log_file_path = f'logs/process_{process_id}.log'
    try:
        with open(log_file_path, 'r') as log_file:
            logs_content = log_file.read()
        return render_template('logs.html', logs_content=logs_content)
    except FileNotFoundError:
        flash('Log file not found.')
        return redirect(url_for('home'))

@app.route('/clear_log/<int:process_id>')
def clear_log(process_id):
    log_file_path = f'logs/process_{process_id}.log'
    try:
        os.remove(log_file_path)  # Remove the log file
        last_execution_times[process_id] = 'Never'  # Reset last execution time
        flash(f'Log for Process {process_id} cleared successfully.')
    except FileNotFoundError:
        flash('Log file not found.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
