from flask import Flask, render_template, request, send_file
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

        # Unique file name
        filename = f"{uuid4()}.%(ext)s"
        path_template = os.path.join(DOWNLOAD_FOLDER, filename)

        ydl_opts = {
            'outtmpl': path_template,
            'quiet': True,
            'merge_output_format': 'mp4'
        }

        if format_id:
            ydl_opts['format'] = format_id

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                return "Error: File not found after download."

            return send_file(
                file_path,
                as_attachment=True,
                download_name=os.path.basename(file_path),
                mimetype='application/octet-stream'
            )

        except Exception as e:
            print(f"[ERROR] {e}")
            return f"Error: {str(e)}"

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

