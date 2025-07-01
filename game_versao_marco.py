# foosball_game.py
# Author: Nuno Lourenço
# Affiliation: Department of Informatics Engineering, University of Coimbra
# Email: naml@dei.uc.pt
# Copyright © 2025 Nuno Lourenço
# License: MIT License

"""
This script is part of a foosball game project developed for educational and research purposes.

Unauthorized copying, distribution, or modification of this file, via any medium, is strictly prohibited without
explicit permission from the author.

Use only for academic or non-commercial purposes, unless otherwise licensed.
"""

from foosbal import *

import socket
import threading
import json

# Configurações de rede
UDP_IP = "0.0.0.0"  # Escuta em todas as interfaces
UDP_PORT = 5010  # Porta para escutar comandos UDP


fila_de_comandos = []

# lock para sincronização de acesso à fila
lock = threading.Lock()



TEAMS = []

# Funções responsáveis pelo movimento dos jogadores no ambiente. 
# O número de unidades que o jogador se pode movimentar é definida pela constante 
# PIXEIS_MOVIMENTO. As funções recebem um dicionário que contém o estado 
# do jogo e o jogador que se está a movimentar. 

def jogador_cima(estado_jogo, jogador):
    y = min(estado_jogo[jogador].ycor()+PIXEIS_MOVIMENTO, ALTURA_JANELA/2-RAIO_JOGADOR)
    goto(estado_jogo[jogador].xcor(), y, estado_jogo[jogador])
    

def jogador_baixo(estado_jogo, jogador):
    y = max(estado_jogo[jogador].ycor()-PIXEIS_MOVIMENTO, -ALTURA_JANELA/2+RAIO_JOGADOR)
    goto(estado_jogo[jogador].xcor(), y, estado_jogo[jogador])    
    
def jogador_direita(estado_jogo, jogador):
    x = min(estado_jogo[jogador].xcor()+PIXEIS_MOVIMENTO, LARGURA_JANELA/2-RAIO_JOGADOR)
    goto(x, estado_jogo[jogador].ycor(), estado_jogo[jogador])

def jogador_esquerda(estado_jogo, jogador):
    x = max(estado_jogo[jogador].xcor()-PIXEIS_MOVIMENTO, -LARGURA_JANELA/2+RAIO_JOGADOR)
    goto(x, estado_jogo[jogador].ycor(), estado_jogo[jogador])


def start_power_shot(estado_jogo, jogador):
    estado_jogo['power_shot_info'][jogador]['pressed_time'] = time.time()

def end_power_shot(estado_jogo, jogador):
    estado_jogo['power_shot_info'][jogador]['pressed_time'] = None




comandos = {
    'UP' : jogador_cima,
    'DOWN': jogador_baixo,
    'LEFT': jogador_esquerda,
    'RIGHT': jogador_direita,
    'POWER_SHOT_ON': start_power_shot,
    'POWER_SHOT_OFF': release_power_shot,
}



def verifica_golo_jogador_vermelho(estado_jogo):
    '''
    Função responsável por verificar se um determinado jogador marcou golo. 
    Para fazer esta verificação poderá fazer uso das constantes: 
    LADO_MAIOR_AREA e START_POS_BALIZAS. 
    Note que sempre que há um golo, deverá atualizar a pontuação do jogador
    '''
    x, y = estado_jogo['bola']['objecto'].xcor(),estado_jogo['bola']['objecto'].ycor()
    if x+RAIO_BOLA>=LARGURA_JANELA/2 and y-RAIO_BOLA >= -START_POS_BALIZAS/2 and y+RAIO_BOLA<=START_POS_BALIZAS/2:
        estado_jogo['pontuacao_jogador_vermelho']+=1
        return True
    return False    

def verifica_golo_jogador_azul(estado_jogo):
    '''
    Função responsável por verificar se um determinado jogador marcou golo. 
    Para fazer esta verificação poderá fazer uso das constantes: 
    LADO_MAIOR_AREA e START_POS_BALIZAS. 
    Note que sempre que há um golo, deverá atualizar a pontuação do jogador
    '''
    x, y = estado_jogo['bola']['objecto'].xcor(),estado_jogo['bola']['objecto'].ycor()
    if x-RAIO_BOLA<=-LARGURA_JANELA/2 and y-RAIO_BOLA >= -START_POS_BALIZAS/2 and y+RAIO_BOLA<=START_POS_BALIZAS/2:
        estado_jogo['pontuacao_jogador_azul']+=1
        return True
    return False


def load_teams():
    '''Função responsável por carregar as equipas do json.'''
    global TEAMS

    try:
        with open('equipas.json', 'r') as file:
            TEAMS = json.load(file)
            print("[INFO] Equipas carregadas com sucesso.")
    except FileNotFoundError:
        print("[ERROR] O ficheiro teams.json não foi encontrado.")
    except json.JSONDecodeError:
        print("[ERROR] Erro ao decodificar o ficheiro teams.json. Verifique o formato JSON.")


def select_teams():

    # selecionar equipa vermelha
    print("Selecione a equipa vermelha:")
    for i, team in enumerate(TEAMS):
        print(f"{i + 1}. {team['name']}")
    escolha_vermelha = int(input("Digite o número da equipa vermelha: ")) - 1
    if escolha_vermelha < 0 or escolha_vermelha >= len(TEAMS):
        print("Escolha inválida. Usando a primeira equipa por padrão.")
        escolha_vermelha = 0 
    equipa_vermelha = TEAMS[escolha_vermelha]
    print(f"Equipa vermelha selecionada: {equipa_vermelha['name']}")

    # selecionar equipa azul
    print("Selecione a equipa azul:")
    for i, team in enumerate(TEAMS):
        if i != escolha_vermelha:
            print(f"{i + 1}. {team['name']}")
    escolha_azul = int(input("Digite o número da equipa azul: ")) - 1
    if escolha_azul < 0 or escolha_azul >= len(TEAMS) or escolha_azul == escolha_vermelha:
        print("Escolha inválida. Usando a primeira equipa diferente da vermelha por padrão.")
        escolha_azul = (escolha_vermelha + 1) % len(TEAMS)
    equipa_azul = TEAMS[escolha_azul]
    print(f"Equipa azul selecionada: {equipa_azul['name']}")

    # Retorna as equipas selecionadas
    return equipa_vermelha, equipa_azul


def decode_message(msg, addr):
    """    Função responsável por decodificar a mensagem recebida via UDP.
    Verifica se a equipa é autorizada e se o código secreto é válido.
    Se tudo estiver correto, executa o comando associado.
    """
    global estado_jogo

    try:
        dados = json.loads(msg)
        equipa = dados.get("id")
        segredo = dados.get("secret")
        comando = dados.get("comando")

        if equipa == JOGADOR_VERMELHO:
            jogador = 'jogador_vermelho'
            equipa_autorizada = equipa_vermelha

        elif equipa == JOGADOR_AZUL:
            jogador = 'jogador_azul'
            equipa_autorizada = equipa_azul

        else:
            print(f"[UDP] Equipa não reconhecida: {equipa} de {addr}")
            return

        # Verifica se a equipa é autorizada e se o segredo é válido    
        if equipa_autorizada["secret"] != segredo:
            print(f"[UDP] Código secreto inválido para {equipa} de {addr}: {segredo} != {equipa_autorizada['secret' ]}" )
            return

        if comando not in comandos:
            print(f"[UDP] Comando inválido: {comando}")
            return

        print(f"[UDP] {equipa} executou comando: {comando}")

        with lock:  # Garante acesso exclusivo à fila de comandos
            fila_de_comandos.append((comando, jogador))
        
    
    except json.JSONDecodeError:
        print(f"[UDP] Mensagem inválida recebida de {addr}: {msg}")





# Função que corre na thread separada
def escuta_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"[UDP] A escutar na porta {UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(1024)  # buffer de 1024 bytes
        message = data.decode('utf-8')
        print(f"[UDP] Recebido '{message}' de {addr}")

        decode_message(message, addr)  # Decodifica e processa a mensagem recebida


if __name__ == '__main__':
    
    global estado_jogo, equipa_vermelha, equipa_azul
    load_teams()  # Carrega as equipas do ficheiro JSON

    equipa_vermelha, equipa_azul = TEAMS[JOGADOR_VERMELHO-1], TEAMS[JOGADOR_AZUL-1]

    ##dicionario com as funcoes de movimento dos jogadores
    funcoes_jogadores = {'jogador_cima': jogador_cima, 'jogador_baixo': jogador_baixo, 'jogador_esquerda': jogador_esquerda, 'jogador_direita': jogador_direita}    
   

    #funções de inicio do jogo
    estado_jogo, estado_campeonato = init_state()
    print(estado_campeonato)
    setup(estado_jogo, True, funcoes_jogadores, estado_campeonato)
    inicia_jogo(estado_jogo)
    desenha_hierarquia_jogos(estado_campeonato) #desenha a hierarquia dos jogo
    
    
    # Iniciar a thread de escuta
    udp_thread = threading.Thread(target=escuta_udp, daemon=True)
    udp_thread.start()

    while True:
        
        estado_jogo['janela'].update() #actualiza a janela

        if estado_jogo['arrancou'] is True:
            if estado_jogo['bola'] is not None:
                movimenta_bola(estado_jogo) #movimenta a bola

            verifica_colisoes_ambiente(estado_jogo) #verifica colisoes da bola com o ambiente (para mudar a sua direcao)
            verifica_golos(estado_jogo, estado_campeonato, verifica_golo_jogador_vermelho, verifica_golo_jogador_azul) #verifica se houve golo
            
            if estado_jogo['jogador_vermelho'] is not None:
                verifica_toque_jogador_vermelho(estado_jogo) #verifica se a bola tocou no jogador vermelho
            if estado_jogo['jogador_azul'] is not None:
                verifica_toque_jogador_azul(estado_jogo) #verifica se a bola tocou no jogador azul
            
            atualiza_power_bar(estado_jogo, 'jogador_vermelho')
            atualiza_power_bar(estado_jogo, 'jogador_azul')

            atualiza_timer(estado_jogo) #atualiza o timer do jogo

            # Processa os comandos recebidos via UDP
            with lock:
                while fila_de_comandos:
                    comando, jogador = fila_de_comandos.pop(0)
                    comandos[comando](estado_jogo, jogador)
                    
    