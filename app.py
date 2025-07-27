from flask import Flask, render_template, request, send_file, after_this_request
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    video_data = None

    if request.method == 'POST':
        url = request.form['url']
        quality = request.form['quality']

        ydl_opts = {'quiet': True, 'skip_download': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'No Title')
            thumbnail = info.get('thumbnail', '')
            duration = info.get('duration', 0)
            mins, secs = divmod(duration, 60)
            duration_str = f"{mins}:{secs:02d}"

        video_data = {
            'url': url,
            'quality': quality,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration_str
        }

    return render_template('index.html', video=video_data)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form['quality']
    unique_id = str(uuid.uuid4())
    base_path = os.path.join(DOWNLOAD_DIR, unique_id)
    filename_template = f"{base_path}.%(ext)s"

    ydl_opts = {
        'outtmpl': filename_template,
        'quiet': True,
        'noplaylist': True
    }

    if quality == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'prefer_ffmpeg': True,
        })

    elif quality == '720':
        ydl_opts.update({
            'format': 'bestvideo[height<=720]+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    elif quality == '1080':
        ydl_opts.update({
            'format': 'bestvideo[height<=1080]+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    elif quality == '360':
        ydl_opts.update({
            'format': 'best[height<=360]',
        })

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if quality == 'audio':
            downloaded_file = None
            for file in os.listdir(DOWNLOAD_DIR):
                if file.startswith(unique_id) and file.endswith(".mp3"):
                    downloaded_file = os.path.join(DOWNLOAD_DIR, file)
                    break
            if not downloaded_file:
                return "MP3 file not found.", 500
        else:
            downloaded_file = ydl.prepare_filename(info)

    @after_this_request
    def cleanup(response):
        try:
            os.remove(downloaded_file)
        except Exception as e:
            print(f"Cleanup error: {e}")
        return response

    return send_file(downloaded_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

