from flask import Flask, request, jsonify
import subprocess
import os
import uuid
import base64
import tempfile
import glob

app = Flask(__name__)

@app.route('/')
def index():
    return 'FFmpeg Audio Split API running!'

@app.route('/convert', methods=['POST'])
def convert_video():
    try:
        # Validación de archivo
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        # Duración de cada parte (en minutos). Default: 15
        # Enviá en form-data (key: segment_minutes) para cambiarlo, ej: 10, 20, etc.
        segment_minutes_str = request.form.get('segment_minutes', '').strip()
        try:
            segment_minutes = int(segment_minutes_str) if segment_minutes_str else 15
            if segment_minutes <= 0:
                raise ValueError()
        except Exception:
            return jsonify({'error': 'segment_minutes debe ser un entero positivo'}), 400

        segment_seconds = segment_minutes * 60

        # Carpeta temporal aislada
        tmpdir = tempfile.mkdtemp(prefix="ffmpeg_split_")

        # Mantener extensión original (no obligatorio, pero prolijo)
        _, ext = os.path.splitext(file.filename)
        if not ext:
            ext = '.mkv'  # fallback
        input_filename = os.path.join(tmpdir, f"{uuid.uuid4()}{ext}")

        # Guardar archivo subido
        file.save(input_filename)

        # Salida en partes: part_000.mp3, part_001.mp3, ...
        output_pattern = os.path.join(tmpdir, "part_%03d.mp3")

        # Ejecutar FFmpeg para EXTRAER AUDIO y dividir en segmentos
        # - Descarta video (-vn)
        # - Mono 16kHz (-ac 1 -ar 16000)
        # - MP3 con bitrate moderado (48k) para achicar tamaño
        # - Divide en segmentos de N segundos
        cmd = [
            'ffmpeg',
            '-hide_banner',
            '-y',
            '-i', input_filename,
            '-vn',
            '-ac', '1',
            '-ar', '16000',
            '-c:a', 'libmp3lame',
            '-b:a', '48k',
            '-f', 'segment',
            '-segment_time', str(segment_seconds),
            '-reset_timestamps', '1',
            output_pattern
        ]

        subprocess.run(cmd, check=True)

        # Buscar todas las partes generadas
        parts = sorted(glob.glob(os.path.join(tmpdir, "part_*.mp3")))
        if not parts:
            return jsonify({'error': 'No se generaron partes de audio. Verificá el archivo de entrada.'}), 500

        # Leer y codificar cada parte a Base64
        chunks = []
        for idx, p in enumerate(parts):
            with open(p, 'rb') as f:
                audio_data = f.read()
            chunks.append({
                'index': idx,
                'filename': os.path.basename(p),
                'audio_mp3_base64': base64.b64encode(audio_data).decode()
            })

        # Limpieza de archivos temporales
        try:
            for p in parts:
                os.remove(p)
            os.remove(input_filename)
            os.rmdir(tmpdir)
        except Exception:
            # Si falla la limpieza, no rompemos la respuesta
            pass

        return jsonify({
            'segment_minutes': segment_minutes,
            'total_chunks': len(chunks),
            'chunks': chunks
        })

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'FFmpeg failed: {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ejecución local
if __name__ == '__main__':
    # En Render, el puerto lo suele inyectar la plataforma con PORT.
    # Para local, dejamos 10000 por defecto.
    port = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=port)
