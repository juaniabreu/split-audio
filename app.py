from flask import Flask, request, jsonify
import subprocess
import os
import uuid
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return 'FFmpeg Audio Split API running!'

@app.route('/convert', methods=['POST'])
def convert_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400

        file = request.files['video']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        # Guardar temporalmente
        input_filename = f"/tmp/{uuid.uuid4()}.mkv"
        output_filename = input_filename.replace('.mkv', '.mp3')
        file.save(input_filename)

        # Ejecutar ffmpeg
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

        # Leer resultado
        with open(output_filename, 'rb') as f:
            audio_data = f.read()

        # Limpiar archivos
        os.remove(input_filename)
        os.remove(output_filename)

        return jsonify({
            'audio_mp3_base64': base64.b64encode(audio_data).decode()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 👇 Esto es lo que probablemente falta:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
