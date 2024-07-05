from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from yt_dlp import YoutubeDL
import os
import time
from threading import Thread
from models import User, get_user_by_username, get_user_by_id, get_user_by_token, add_user, update_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ändere dies zu einem sicheren Schlüssel
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
DOWNLOAD_FOLDER = 'downloads'

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))

def download_youtube_video(youtube_url, format='mp4'):
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        }

        if format in ['mp4', 'webm', 'mkv', 'flv']:
            ydl_opts['format'] = f'bestvideo[ext={format}]+bestaudio[ext=m4a]/best[ext={format}]/best'
            ydl_opts['merge_output_format'] = format
        elif format in ['mp3', 'aac', 'wav', 'm4a', 'opus']:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': '192',
            }]

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            downloaded_file_path = ydl.prepare_filename(info_dict)
            if format in ['mp4', 'webm', 'mkv', 'flv']:
                file_path = downloaded_file_path.rsplit('.', 1)[0] + f'.{format}'
            elif format in ['mp3', 'aac', 'wav', 'm4a', 'opus']:
                file_path = downloaded_file_path.rsplit('.', 1)[0] + f'.{format}'

        return file_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def delayed_file_removal(file_path):
    # Warte ein paar Sekunden, bevor du die Datei löschst
    time.sleep(5)
    try:
        os.remove(file_path)
        print(f"File removed: {file_path}")
    except Exception as e:
        print(f"Error removing file: {e}")

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    user = get_user_by_token(token)
    if not user or user.registered:
        return "Invalid or expired registration link."

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user.username == username:
            user.password = password
            user.registered = True
            user.registration_token = None
            update_user(user)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username.')
    return render_template('register.html', token=token)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user_page():
    if current_user.username != 'admin':
        return "Unauthorized", 403
    
    if request.method == 'POST':
        username = request.form['username']
        token = add_user(username)
        flash(f'User added. Registration link: {url_for("register", token=token, _external=True)}')
    
    return render_template('add_user.html')

@app.route('/download', methods=['POST'])
@login_required
def download():
    youtube_url = request.form['youtube_url']
    format = request.form['format']
    file_path = download_youtube_video(youtube_url, format)
    if file_path:
        @after_this_request
        def remove_file(response):
            Thread(target=delayed_file_removal, args=(file_path,)).start()
            return response

        return send_file(file_path, as_attachment=True)
    else:
        return "An error occurred during the download process."

if __name__ == '__main__':
    app.run(debug=True)
