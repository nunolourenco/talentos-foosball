# test client that waits for keypresses and sends them to the server via UDP
import socket
import tkinter as tk
import json
import keyboard

# === Configurações ===
SERVER_IP = 'localhost'  # IP do servidor
SERVER_PORT = 5010  # Porta do servidor

# Lista de teclas registadas
registered_keys = {'w':'UP', 'a': 'LEFT', 's':'DOWN', 'd':'RIGHT', 'p':'POWER_SHOT_ON', 'o':'POWER_SHOT_OFF'}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    

def on_key(event):
    tecla = event.char or event.keysym
    if tecla in registered_keys.keys():
        message = json.dumps({'id':1, 'secret':'segredoA', 'comando': registered_keys[tecla]}).encode('utf-8')

        print(message)
        sock.sendto(message, (SERVER_IP, SERVER_PORT))
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