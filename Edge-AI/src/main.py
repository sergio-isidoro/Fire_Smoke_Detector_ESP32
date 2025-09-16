import cv2
import sys
from config import Config
from fire_detector import Detector
import time
import logging

# --- NOVO: Configuração do logging para ver mensagens de erro do detector ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- NOVO: Função para escolher a fonte de vídeo ---
def get_video_source():
    """
    Pergunta ao utilizador qual fonte de vídeo usar (webcam ou IP) e retorna
    o identificador apropriado para o OpenCV.
    """
    while True:
        print("Escolha a fonte de vídeo:")
        print("1: Webcam Local")
        print("2: Câmera IP (ESP32-S3)")
        choice = input("Digite sua escolha (1 ou 2): ")

        if choice == '1':
            # Retorna 0, que é o índice padrão para a primeira webcam
            return 0
        elif choice == '2':
            ip_address = input("Digite o endereço IP do seu ESP32-S3: ")
            # O URL de stream para o web server da câmara do ESP32 é geralmente neste formato
            url = f"http://{ip_address}:81/stream"
            print(f"A tentar conectar ao stream: {url}")
            return url
        else:
            print("❌ Escolha inválida. Por favor, tente novamente.\n")


# Coordenadas do botão "EXIT" para Full HD
BUTTON_X, BUTTON_Y, BUTTON_W, BUTTON_H = 20, 20, 200, 80

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if BUTTON_X <= x <= BUTTON_X + BUTTON_W and BUTTON_Y <= y <= BUTTON_Y + BUTTON_H:
            param['exit'] = True

def main():
    # --- ALTERADO: Primeiro, obter a fonte de vídeo do utilizador ---
    video_source = get_video_source()

    try:
        # Inicializar o detector
        detector = Detector(Config.MODEL_PATH, iou_threshold=0.20)

        # --- ALTERADO: Abrir a fonte de vídeo escolhida (webcam ou IP) ---
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"❌ Não foi possível abrir a fonte de vídeo: {video_source}")
            sys.exit(1)

        # --- REMOVIDO/COMENTADO: A definição de resolução pode causar erros com streams IP ---
        # A resolução do stream será a nativa da câmara ESP32.
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        alert_cooldown = Config.ALERT_COOLDOWN
        last_alert_time = 0
        next_detection_to_report = "any"

        # Configurar o callback do rato
        mouse_param = {'exit': False}
        cv2.namedWindow("Fire Detection System")
        cv2.setMouseCallback("Fire Detection System", click_event, mouse_param)

        print("\n✅ Sistema iniciado. Pressione 'q' ou clique em 'EXIT' para sair.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Falha ao capturar frame. A conexão pode ter sido perdida.")
                break

            # Pipeline de deteção
            processed_frame, detection = detector.process_frame(frame)

            if detection:
                current_time = time.time()
                if (next_detection_to_report == "any" or detection == next_detection_to_report) \
                        and (current_time - last_alert_time) > alert_cooldown:
                    print(f"🐦‍🔥 {detection} detectado!")
                    last_alert_time = current_time
                    next_detection_to_report = "Smoke" if detection == "Fire" else "Fire"

            # Desenhar o botão EXIT
            cv2.rectangle(processed_frame, (BUTTON_X, BUTTON_Y),
                          (BUTTON_X + BUTTON_W, BUTTON_Y + BUTTON_H), (0,0,255), -1)
            cv2.putText(processed_frame, "EXIT", (BUTTON_X + 40, BUTTON_Y + 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)

            cv2.imshow("Fire Detection System", processed_frame)

            # Sair se o botão for clicado ou 'q' for pressionado
            if cv2.waitKey(1) & 0xFF == ord('q') or mouse_param['exit']:
                break

    except Exception as e:
        print(f"🚨 Falha crítica: {str(e)}")
        sys.exit(1)
    finally:
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()