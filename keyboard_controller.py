# test client that waits for keypresses and sends them to the server via UDP
import socket
import tkinter as tk
import json

ID_EQUIPA = 1  # ID da equipa do cliente
SECRET_EQUIPA = 'segredoA'  # Código secreto da equipa do cliente


# === Configurações ===
SERVER_IP = 'localhost'  # IP do servidor
SERVER_PORT = 5010  # Porta do servidor

# Lista de teclas registadas
registered_keys = {'w':'UP', 'a': 'LEFT', 's':'DOWN', 'd':'RIGHT', 'p':'POWER_SHOT_ON'}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(command):
    """
    Envia um comando para o servidor
    """
    message = json.dumps({'id': ID_EQUIPA, 'secret': SECRET_EQUIPA, 'comando': command}).encode('utf-8')
    sock.sendto(message, (SERVER_IP, SERVER_PORT))
    

# Função chamada quando uma tecla é pressionada
def on_key(event):
    tecla = event.char or event.keysym
    if tecla in registered_keys.keys():
        
        send_command(registered_keys[tecla])

        print(f"[CLIENTE] Enviado: {registered_keys[tecla]}")
    else:
        print(f"[CLIENTE] Tecla não registada: {tecla}")

# Criar janela
root = tk.Tk()
root.title("Detetor de Teclas")
root.geometry("400x150")

# Instruções
label = tk.Label(root, text="Pressiona qualquer tecla...\n(Fecha a janela para sair)", font=("Arial", 12))
label.pack(pady=30)

# Ligar evento de teclado
root.bind("<Key>", on_key)

# Iniciar ciclo da interface
root.mainloop()