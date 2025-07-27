from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import yt_dlp
from uuid import uuid4

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        format_id = request.form.get('format')

        # Create a unique filename
        filename = f"{uuid4()}.%(ext)s"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        ydl_opts = {
            'outtmpl': filepath,
            'quiet': True,
        }

        # Add format
        if format_id:
            ydl_opts['format'] = format_id

        # Enable merging for video+audio
        ydl_opts['merge_output_format'] = 'mp4'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                actual_path = ydl.prepare_filename(info)

            return send_file(actual_path, as_attachment=True)
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('index.html')

# ✅ Use dynamic port for Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

