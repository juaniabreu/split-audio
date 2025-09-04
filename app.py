from flask import Flask, request, jsonify
import base64
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
        data = request.json
        video_b64 = data['video']
        input_filename = f'/tmp/{uuid.uuid4()}.mp4'
        output_filename = input_filename.replace('.mp4', '.mp3')

        # Guardar archivo temporal
        with open(input_filename, 'wb') as f:
            f.write(base64.b64decode(video_b64))

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

        # Leer archivo generado
        with open(output_filename, 'rb') as f:
            mp3_data = f.read()

        # Limpiar
        os.remove(input_filename)
        os.remove(output_filename)

        return jsonify({
            'audio_mp3_base64': base64.b64encode(mp3_data).decode()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ AGREGA ESTO AL FINAL
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
