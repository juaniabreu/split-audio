from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return 'FFmpeg Audio Split API running!'

@app.route('/convert', methods=['POST'])
def convert_video():
    try:
        # Verificamos si se envió un archivo
        if 'video' not in request.files:
            return jsonify({'error': 'No video file part'}), 400

        file = request.files['video']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Guardamos archivo temporal
        input_filename = f"/tmp/{uuid.uuid4()}.mkv"
        output_filename = input_filename.replace('.mkv', '.mp3')
        file.save(input_filename)

        # Ejecutamos ffmpeg
        cmd = [
            'ffmpeg',
            '-i', input_filename,
            '-vn',
            '-acodec', 'mp3',
            '-ar', '16000',
            '-ac', '1',
            output_filename
        ]
        subprocess.run(cmd, check=True)

        # Leemos el resultado
        with open(output_filename, 'rb') as f:
            audio_data = f.read()

        # Limpiamos
        os.remove(input_filename)
        os.remove(output_filename)

        return jsonify({
            'audio_mp3_base64': audio_data.encode("base64").decode()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
