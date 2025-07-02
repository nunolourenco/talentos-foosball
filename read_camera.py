import cv2
import socket
import threading

# === Configurações ===
VIDEO_PORT = 5005
CONTROL_PORT = 6006
CHUNK_SIZE = 900

# Área de corte da imagem
X_MIN = 100
X_MAX = 500
Y_MIN = 50
Y_MAX = 300

FLAG_0, FLAG_1 = b'\x00', b'\x01'

# Lista de IPs registados
clients = set()
clients_lock = threading.Lock()

# Socket de envio (UDP)
video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# === Função para enviar frames para todos os clientes ===
def broadcast(img):
    # Cortar a imagem
    cropped = img[Y_MIN:Y_MAX, X_MIN:X_MAX]
    
    # Codificar como JPEG
    ret, buffer = cv2.imencode('.jpg', cropped)
    if not ret:
        print("Falha ao codificar imagem.")
        return
    data = buffer.tobytes()
    
    # Dividir em pacotes
    total = len(data)
    for i in range(0, total, CHUNK_SIZE):
        chunk = data[i:i+CHUNK_SIZE]
        flag = FLAG_1 if i == 0 else FLAG_0
        message = flag + chunk

        # Enviar para todos os clientes registados
        with clients_lock:
            for ip in clients:
                video_sock.sendto(message, (ip, VIDEO_PORT))

# === Função para escutar canal de controlo ===
def control_listener():
    control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_sock.bind(('', CONTROL_PORT))  # escuta em todas as interfaces
    print(f"[CONTROLO] A escutar na porta {CONTROL_PORT}...")

    while True:
        data, addr = control_sock.recvfrom(1024)
        ip = addr[0]
        msg = data.decode().strip().upper()

        with clients_lock:
            if msg == "REGISTER":
                clients.add(ip)
                print(f"[CONTROLO] IP {ip} registado.")
                control_sock.sendto(b"OK: REGISTERED", addr)
            elif msg == "UNREGISTER":
                clients.discard(ip)
                print(f"[CONTROLO] IP {ip} removido.")
                control_sock.sendto(b"OK: UNREGISTERED", addr)
            else:
                print(f"[CONTROLO] Mensagem desconhecida de {ip}: {msg}")
                control_sock.sendto(b"ERROR: UNKNOWN COMMAND", addr)

# === Thread do canal de controlo ===
threading.Thread(target=control_listener, daemon=True).start()

# === Captura de vídeo ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Erro ao abrir câmara.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao capturar frame.")
            break

        broadcast(frame)

        cv2.imshow("Servidor de Câmara", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            print("A sair...")
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
