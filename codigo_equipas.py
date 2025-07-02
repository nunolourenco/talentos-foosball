import socket

import cv2
import numpy as np
import json


MODO_TEST = True  # Modo de teste, se True envia comandos para o localhost, se False envia para o servidor real

# Network communication
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
CHUNK_SIZE = 900

# Configurações do servidor
SERVER_IP = "10.6.1.31"
if MODO_TEST:
    # Configurações para o modo de teste
    SERVER_IP = "localhost"

print(f"Conectando ao servidor em {SERVER_IP}...")
CONTROL_PORT = 6006
GAME_PORT = 5010

# Socket para controlo do cliente
control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
control_sock.settimeout(2)

# socket para enviar comandos para o jogo
game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
game_sock.settimeout(2)



# ID da equipa e segredo
ID_EQUIPA = 1  # ID da equipa do cliente
SECRET_EQUIPA = 'segredoA'  # Código secreto da equipa do cliente   

# COMANDOS POSSIVEIS
comandos_possiveis = [
    'UP',  # Mover para cima
    'DOWN',  # Mover para baixo
    'LEFT',  # Mover para a esquerda
    'RIGHT',  # Mover para a direita
    'POWER_SHOT_ON'  # Ativar power shot
]

# Buffer para armazenar dados de frames recebidos
frame_data = b""

camera_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
camera_sock.bind((UDP_IP, UDP_PORT))

TARGET_COLORS_HSV = [
    [110, 75, 50],
    [200, 75, 50],
]

H_TOLERANCE = 10
S_TOLERANCE = 40
V_TOLERANCE = 40

TARGET_COLORS_HSV_LIMITS = None


def calculate_hsv_limits():
    """Calculate HSV limits for each target color using tolerance"""
    global TARGET_COLORS_HSV, TARGET_COLORS_HSV_LIMITS
    TARGET_COLORS_HSV_LIMITS = []
    for hsv in TARGET_COLORS_HSV:
        h, s, v = hsv
        lower = np.array([max(0, h - H_TOLERANCE), max(0, s - S_TOLERANCE), max(0, v - V_TOLERANCE)], dtype=np.uint8)
        upper = np.array([min(179, h + H_TOLERANCE), min(255, s + S_TOLERANCE), min(255, v + V_TOLERANCE)], dtype=np.uint8)
        TARGET_COLORS_HSV_LIMITS.append([lower, upper])


def where_the_magic_happens(frame_bgr):
    # ----------------------------------------
    # TODO analyse input image

    # ----------------------------------------
    # TODO send commands to control the game
    send_command('UP')  # Example command, replace with actual logic

    # Show video frame
    cv2.imshow("Talentos", frame_bgr)

    # Check for key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Saindo...")
        return


def send_command(command):
    """
    Envia um comando para o servidor
    """
    message = json.dumps({'id': ID_EQUIPA, 'secret': SECRET_EQUIPA, 'comando': command}).encode('utf-8')
    game_sock.sendto(message, (SERVER_IP, GAME_PORT))

def register_client():
    control_sock.sendto(b"REGISTER", (SERVER_IP, CONTROL_PORT))
    try:
        data, _ = control_sock.recvfrom(1024)
        print("Resposta do servidor:", data.decode())
    except socket.timeout:
        print("Sem resposta do servidor.")


def unregister_client():
    control_sock.sendto(b"UNREGISTER", (SERVER_IP, CONTROL_PORT))
    try:
        data, _ = control_sock.recvfrom(1024)
        print("Resposta do servidor:", data.decode())
    except socket.timeout:
        print("Sem resposta do servidor.")


def receive_stream():
    global frame_data

    while True:
        # read a chunk of data from the socket
        # the first byte indicates if this is the first chunk of a new frame (1)
        # or a continuation of the previous frame (0)
        # the rest of the chunk contains the image data
        # we assume the chunk size is fixed at CHUNK_SIZE + 1 for the flag
        # so we can read the flag and the data in one go
        chunk, _ = camera_sock.recvfrom(CHUNK_SIZE + 1)

        if len(chunk) < 2:
            print("Received chunk too small, ignoring")
            continue

        flag = chunk[0]
        data = chunk[1:]

        if flag == 0:
            frame_data += data
        else:
            # If this is the first chunk of a new frame, we need to process the previous frame data
            try:
                img_array = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                frame_data = data  # Reset frame data for the next frame
                if frame is None:
                    print("Failed to decode frame")
                    continue
                else:
                    return frame
            except Exception as e:
                print(f"Error decoding frame: {e}")
            frame_data = data


if __name__ == "__main__":
    calculate_hsv_limits()
    register_client()
    try:
        while True:
            frame = receive_stream()
            if frame is not None:
                where_the_magic_happens(frame)
    except KeyboardInterrupt:
        pass
    finally:
        unregister_client()
        cv2.destroyAllWindows()  # Close OpenCV windows
