import logging
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, after_this_request, g
from yt_dlp import YoutubeDL
import os
import time
from threading import Thread
import subprocess

# Konfiguration des Loggings
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'


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
        elif format in ['mp3', 'aac', 'wav', 'm4a']:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': '320',
            }]

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            downloaded_file_path = ydl.prepare_filename(info_dict)
            if format in ['mp4', 'webm', 'mkv', 'flv']:
                file_path = downloaded_file_path.rsplit('.', 1)[0] + f'.{format}'
            elif format in ['mp3', 'aac', 'wav', 'm4a']:
                file_path = downloaded_file_path.rsplit('.', 1)[0] + f'.{format}'

        return file_path

    except Exception as e:
        logger.error(f"Ein Fehler ist beim YouTube-Download aufgetreten: {e}")
        return None

def delayed_file_removal(file_path):
    time.sleep(5)
    try:
        os.remove(file_path)
        logger.info(f"Datei erfolgreich gelöscht: {file_path}")
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Datei: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format = request.form['format']
    
    if 'youtube.com' in url or 'youtu.be' in url:
        file_path = download_youtube_video(url, format)
    else:
        logger.warning(f"Nicht unterstützte URL eingegeben: {url}")
        return "Unsupported URL."

    if file_path:
        @after_this_request
        def remove_file(response):
            Thread(target=delayed_file_removal, args=(file_path,)).start()
            return response
        
        @after_this_request
        def stop_loader(response):
            response.direct_passthrough = False
            response.set_data(response.get_data() + b"<script>document.getElementById('loading-overlay').style.display = 'none';</script>")
            return response

        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))

    else:
        logger.error("Ein Fehler ist beim Download-Prozess aufgetreten.")
        return "An error occurred during the download process."


if __name__ == '__main__':
    app.run(debug=True)
