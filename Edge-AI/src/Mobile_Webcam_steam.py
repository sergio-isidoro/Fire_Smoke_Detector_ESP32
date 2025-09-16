from flask import Flask, Response
import cv2
import socket
import time

# --- Configuração do Servidor ---
# Encontra o IP local da máquina automaticamente
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Não precisa de ser alcançável, apenas inicia a conexão
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1" # Retorna localhost se não conseguir encontrar

IP_ADDRESS = get_ip_address()
PORT = 5000 # Pode alterar esta porta se desejar

# Inicializa o Flask
app = Flask(__name__)

# Inicializa a webcam
# Se o erro persistir, tente alterar o número 0 para 1, 2, etc.
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    raise IOError("Não foi possível abrir a webcam. Verifique se está conectada e não está em uso.")

# --- Lógica do Servidor ---

# --- FUNÇÃO CORRIGIDA ---
def generate_frames():
    """Lê frames da webcam, codifica-os como JPEG e envia-os como um stream."""
    while True:
        # Captura um único frame
        success, frame = video_capture.read()
        if not success:
            print("(!) Falha ao ler frame da câmara. A tentar novamente...")
            # Pausa por meio segundo antes de tentar novamente
            time.sleep(0.5) 
            continue # <-- ALTERAÇÃO PRINCIPAL: Continua a tentar em vez de parar o loop
        else:
            # Inverte o frame para um efeito de espelho (opcional)
            frame = cv2.flip(frame, 1)

            # Codifica o frame para o formato JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("(!) Falha ao codificar o frame.")
                continue

            # Converte os bytes do buffer para um formato que pode ser enviado
            frame_bytes = buffer.tobytes()

            # Envia o frame para o cliente no formato multipart
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Página principal que mostra o vídeo."""
    return f"""
    <html>
        <head>
            <title>Camera Stream</title>
            <style>
                body {{ font-family: sans-serif; background-color: #2c3e50; color: #ecf0f1; text-align: center; margin: 0; padding-top: 20px; }}
                h1 {{ font-weight: 300; }}
                img {{ border-radius: 8px; border: 3px solid #3498db; max-width: 90%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>Webcam Live Stream</h1>
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
    print(f"  Servidor de vídeo a iniciar...")
    print(f"  Abra este endereço no navegador de outro dispositivo:")
    print(f"  >> http://{IP_ADDRESS}:{PORT} <<")
    print("======================================================")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)

# Quando o servidor for parado (Ctrl+C), liberta a câmara
print("A desligar o servidor e a libertar a câmara...")
video_capture.release()
