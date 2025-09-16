from flask import Flask, Response
import cv2
import socket
import time
from waitress import serve # Importa o servidor de produção Waitress

# --- Configuração do Servidor ---
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

IP_ADDRESS = get_ip_address()
PORT = 5000

app = Flask(__name__)

# --- Otimizações de Captura ---
# 1. Resolução baixa para processamento rápido
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not video_capture.isOpened():
    raise IOError("Não foi possível abrir a webcam. Verifique se está conectada e não está em uso.")

# --- Lógica do Servidor ---

def generate_frames():
    """Lê frames da webcam, codifica-os como JPEG e envia-os como um stream."""
    while True:
        success, frame = video_capture.read()
        if not success:
            print("(!) Falha ao ler frame da câmara. A tentar novamente...")
            time.sleep(0.5) 
            continue
        else:
            frame = cv2.flip(frame, 1)

            # 2. Qualidade JPEG agressiva para menor latência de rede
            # Experimente valores entre 50-75 para encontrar o seu equilíbrio ideal
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                print("(!) Falha ao codificar o frame.")
                continue

            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Página principal que mostra o vídeo."""
    return f"""
    <html>
        <head>
            <title>Low Latency Camera Stream</title>
            <style>
                body {{ font-family: sans-serif; background-color: #2c3e50; color: #ecf0f1; text-align: center; margin: 0; padding-top: 20px; }}
                h1 {{ font-weight: 300; }}
                img {{ border-radius: 8px; border: 3px solid #3498db; max-width: 90%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>Webcam Live Stream (Low Latency)</h1>
            <p>A transmitir a partir de: {IP_ADDRESS}:{PORT}</p>
            <img src="/video_feed">
        </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    """Endpoint que fornece o stream de vídeo."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# --- Ponto de Entrada ---
if __name__ == '__main__':
    print("======================================================")
    print(f"  Servidor de baixa latência a iniciar...")
    print(f"  A usar o servidor de produção 'Waitress'.")
    print(f"  Abra este endereço no navegador de outro dispositivo:")
    print(f"  >> http://{IP_ADDRESS}:{PORT} <<")
    print("======================================================")
    
    # 3. Usa o servidor Waitress em vez do servidor de desenvolvimento do Flask
    serve(app, host='0.0.0.0', port=PORT)

print("A desligar o servidor e a libertar a câmara...")
video_capture.release()