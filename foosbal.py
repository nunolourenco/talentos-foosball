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

import turtle as t
import functools
import random
import math
import time
import json

MODO_TESTE = True # Modo teste/desenvolvimento (para deploy colocar False)

LARGURA_PAINEL = 350 # 1080
PADDING_PAINEL = 20 # 100
LARGURA_JANELA = 1024 # 7560
ALTURA_JANELA = 600 #1920
ESPACO_ENTRE_JOGOS = 30
ESCALA_TIPOGRAFIA = 1



DEFAULT_TURTLE_SIZE = 40
DEFAULT_TURTLE_SCALE = 3


if not MODO_TESTE:
    LARGURA_PAINEL = 1080
    PADDING_PAINEL = 100
    LARGURA_JANELA = 7560
    ALTURA_JANELA = 1920
    ESPACO_ENTRE_JOGOS = 100
    ESCALA_TIPOGRAFIA = 3
    DEFAULT_TURTLE_SCALE = 7 


RAIO_JOGADOR = DEFAULT_TURTLE_SIZE / DEFAULT_TURTLE_SCALE
RAIO_BOLA = DEFAULT_TURTLE_SIZE / 2 
LADO_MAIOR_AREA = ALTURA_JANELA / 3
LADO_MENOR_AREA = 50
RAIO_MEIO_CAMPO = LADO_MAIOR_AREA / 4
START_POS_BALIZAS = ALTURA_JANELA / 3
BOLA_START_POS = (0,0)
BALL_SPEED = 20
PIXEIS_MOVIMENTO = 25

JOGADOR_VERMELHO = 1
JOGADOR_AZUL = 2


t.colormode(255)

def start_power_shot(estado_jogo, jogador):
    estado_jogo['power_shot_info'][jogador]['pressed_time'] = time.time()

def release_power_shot(estado_jogo, jogador):
    estado_jogo['power_shot_info'][jogador]['pressed_time'] = None
    estado_jogo['power_shot_info'][jogador]['duration'] = 0
    atualiza_power_bar(estado_jogo, jogador)

def check_power_shot(estado_jogo, jogador):
    pressed = estado_jogo['power_shot_info'][jogador]['pressed_time']
    if pressed is not None:
        delta = time.time() - pressed
        estado_jogo['power_shot_info'][jogador]['duration'] = min(delta, estado_jogo['power_shot_info']['max_duration'])
        if delta >= estado_jogo['power_shot_info']['max_duration']:
            # Finaliza o power shot
            estado_jogo['power_shot_info'][jogador]['pressed_time'] = None
            estado_jogo['power_shot_info'][jogador]['duration'] = 0
            
            atualiza_power_bar(estado_jogo, jogador)

def get_power_speed(estado_jogo, jogador):
    ratio = estado_jogo['power_shot_info'][jogador]['duration'] / estado_jogo['power_shot_info']['max_duration']
    return estado_jogo['power_shot_info']['base_speed'] + (estado_jogo['power_shot_info']['max_speed'] - estado_jogo['power_shot_info']['base_speed']) * ratio


def goto(x,y, t):
    t.pu()
    t.goto(x,y)
    t.pd()
    
def desenha_baliza(t):
    for i in range(2):
        t.fd(LADO_MENOR_AREA)
        t.rt(90)
        t.fd(LADO_MAIOR_AREA)
        t.rt(90)
        
def desenha_linhas_campo():
    t.hideturtle()
    marcador = t.Turtle()
    marcador.fillcolor('white')
    marcador.pencolor('white')
    marcador.pensize(7)

     # desenha o contorno do campo
    goto(-LARGURA_JANELA / 2, -ALTURA_JANELA / 2, marcador)
    marcador.setheading(0)
    marcador.fillcolor('green')
    marcador.begin_fill()
    for _ in range(2):
        marcador.forward(LARGURA_JANELA)
        marcador.left(90)
        marcador.forward(ALTURA_JANELA)
        marcador.left(90)
    marcador.end_fill()

    marcador.shape('circle')
    goto(-LARGURA_JANELA/2, START_POS_BALIZAS/2,marcador)
    t.seth(0)
    desenha_baliza(marcador)
    goto(LARGURA_JANELA/2, -START_POS_BALIZAS/2,marcador)
    marcador.seth(180)
    desenha_baliza(marcador)

    goto(0, -ALTURA_JANELA/2,marcador)
    marcador.seth(90)
    marcador.goto(0,0)
    marcador.stamp()
    marcador.goto(0,ALTURA_JANELA/2)
    
    goto(RAIO_MEIO_CAMPO*2,0,marcador)
    marcador.circle(RAIO_MEIO_CAMPO*2)

    marcador.hideturtle()
    
    ''' Função responsável por desenhar as linhas do campo, 
    nomeadamente a linha de meio campo, o círculo central, e as balizas. '''
    pass


def inicia_velocidades_bola():
    direcao_bola = random.random()*math.pi*2
    velocidade_bola_x = BALL_SPEED*math.cos(direcao_bola)
    velocidade_bola_y = BALL_SPEED*math.sin(direcao_bola)
    return velocidade_bola_x, velocidade_bola_y
def criar_bola():
    bola = t.Turtle()
    bola.fillcolor('black')
    bola.shape('circle')
    #bola.shapesize(RAIO_BOLA/2, RAIO_BOLA/2)
    '''
    Função responsável pela criação da bola. 
    Deverá considerar que esta tem uma forma redonda, é de cor preta, 
    começa na posição BOLA_START_POS com uma direção aleatória. 
    Deverá ter em conta que a velocidade da bola deverá ser superior à dos jogadores. 
    A função deverá devolver um dicionário contendo 4 elementos: o objeto bola, 
    a sua velocidade no eixo dos xx, a sua velocidade no eixo dos yy, 
    e um elemento inicialmente a None que corresponde à posição anterior da mesma.
    '''
    velocidade_bola_x, velocidade_bola_y = inicia_velocidades_bola()
    return {'objecto':bola, 'velocidade_bola_x':velocidade_bola_x, 'velocidade_bola_y':velocidade_bola_y, 'posicao_anterior':None}


def cria_jogador(x_pos_inicial, y_pos_inicial, cor):
    ''' Função responsável por criar e devolver o objeto que corresponde a um jogador (um objecto Turtle). 
    A função recebe 3 argumentos que correspondem às coordenadas da posição inicial 
    em xx e yy, e a cor do jogador. A forma dos jogadores deverá ser um círculo, 
    cujo seu tamanho deverá ser definido através da função shapesize
    do módulo \texttt{turtle}, usando os seguintes parâmetros: 
    stretch_wid=DEFAULT_TURTLE_SCALE, stretch_len=DEFAULT_TURTLE_SCALE. '''
    jogador = t.Turtle()
    goto(x_pos_inicial, y_pos_inicial, jogador)
    jogador.shape('circle')
    jogador.shapesize(stretch_wid=DEFAULT_TURTLE_SCALE, stretch_len=DEFAULT_TURTLE_SCALE)
    jogador.fillcolor(cor)
    return jogador

def guardar_estado_campeonato(estado, filename='estado_campeonato.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(estado, f, indent=4, ensure_ascii=False)


def ler_estado_campeonato(filename='estado_campeonato.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def init_state():
    estado_campeonato = ler_estado_campeonato()

    estado_jogo = {}
    estado_jogo['arrancou'] = False

    estado_jogo['bola'] = None
    estado_jogo['jogador_vermelho'] = None
    estado_jogo['jogador_azul'] = None
    estado_jogo['var'] = {
        'bola' : [],
        'jogador_vermelho' : [],
        'jogador_azul' : [],
    }
    estado_jogo['pontuacao_jogador_vermelho'] = 0
    estado_jogo['pontuacao_jogador_azul'] = 0
    return estado_jogo, estado_campeonato

def cria_janela():
    #create a window and declare a variable called window and call the screen()
    window=t.Screen()
    window.title("Foosball Game")
    #window.bgcolor("green")
    window.bgcolor((0, 50, 0))
    window.setup(width = LARGURA_JANELA+LARGURA_PAINEL*2,height = ALTURA_JANELA)
    
    canvas = window.getcanvas()
    root = canvas.winfo_toplevel()
    root.overrideredirect(True)  # Remove window decorations
    
    window.tracer(0)
    return window

def get_nome_jogador(estado_campeonato, id_jogador):
    for jogador in estado_campeonato['jogadores']:
        if jogador['id'] == id_jogador:
            return jogador['nome']
    return "—"

def desenha_hierarquia_jogos(estado_campeonato):
    quadro = t.Turtle()
    quadro.speed(0)
    quadro.color("white")
    quadro.penup()
    quadro.hideturtle()
    
    x_inicial = LARGURA_JANELA/2 
    y_inicial = ALTURA_JANELA/2 - PADDING_PAINEL*2

    def desenha_divisao(nome_divisao, jogos, y_start):
        if nome_divisao == 'divisao_1':
            div_nome = "Divisão 1"
        elif nome_divisao == 'divisao_2':
            div_nome = "Divisão 2"
        quadro.goto(x_inicial, y_start)
        quadro.write(f"{div_nome}", align="left", font=('Monaco', 11*ESCALA_TIPOGRAFIA, "bold"))
        y = y_start - ESPACO_ENTRE_JOGOS

        for jogo in jogos:
            nome_r = get_nome_jogador(estado_campeonato, jogo['jogador_vermelho']) if jogo['jogador_vermelho'] else "—"
            nome_a = get_nome_jogador(estado_campeonato, jogo['jogador_azul']) if jogo['jogador_azul'] else "—"
            texto = f"(R) {nome_r} vs (B) {nome_a}"
            if jogo['nivel'] == 1:  
                quadro.goto(x_inicial + 5, y)
            if jogo['nivel'] == 2:  
                y -= ESPACO_ENTRE_JOGOS
                quadro.goto(x_inicial + 5, y)
            quadro.write(texto, align="left", font=('Monaco', 10*ESCALA_TIPOGRAFIA, "normal"))
            y -= ESPACO_ENTRE_JOGOS
        return y - PADDING_PAINEL
        

    y_atual = y_inicial
    for divisao, dados in estado_campeonato['jogos'].items():
        if divisao == 'divisao_1': 
            x_inicial = -LARGURA_JANELA/2  - LARGURA_PAINEL + PADDING_PAINEL
            desenha_divisao(divisao, dados['jogos'], y_atual)
        else:
            x_inicial = LARGURA_JANELA/2 + PADDING_PAINEL
            y_atual = desenha_divisao(divisao, dados['jogos'], y_atual)
            y_atual -= ESPACO_ENTRE_JOGOS
        

    # Final
    quadro.goto(x_inicial, y_atual)
    quadro.write("Final!", align="left", font=('Monaco', 11*ESCALA_TIPOGRAFIA, "bold"))
    final = estado_campeonato.get('jogo_final', {})
    nome_r = get_nome_jogador(estado_campeonato, final.get('jogador_vermelho')) if final.get('jogador_vermelho') else "—"
    nome_a = get_nome_jogador(estado_campeonato, final.get('jogador_azul')) if final.get('jogador_azul') else "—"
    quadro.goto(x_inicial + 5, y_atual - ESPACO_ENTRE_JOGOS)
    quadro.write(f"(R) {nome_r} vs (B) {nome_a}", align="left", font=('Monaco', 10*ESCALA_TIPOGRAFIA, "normal"))

    return quadro

def cria_quadro_resultados(estado_campeonato):
    #Code for creating pen for scorecard update
    quadro=t.Turtle()
    quadro.speed(0)
    quadro.color("white")
    quadro.penup()
    quadro.hideturtle()
    #quadro.goto(0,260)
    quadro.goto(0,ALTURA_JANELA/2-PADDING_PAINEL-24*ESCALA_TIPOGRAFIA)
    #quadro.write("Player A: 0\t\tPlayer B: 0 ", align="center", font=('Monaco',24,"normal"))
    quadro.write("0 : 0", align="center", font=('Monaco',24*ESCALA_TIPOGRAFIA,"normal"))
    quadro.hideturtle()
    quadro.goto(0,ALTURA_JANELA/2-PADDING_PAINEL-24*ESCALA_TIPOGRAFIA)
    #quadro.write("Jogador 1\t\t\t\tJogador 2", align="center", font=('Monaco',24,"normal"))
    quadro.write("{}\t\t\t\t{}".format(get_nome_jogador(estado_campeonato, JOGADOR_VERMELHO), get_nome_jogador(estado_campeonato, JOGADOR_AZUL)), align="center", font=('Monaco',24*ESCALA_TIPOGRAFIA,"normal"))
    

    return quadro

def cria_quadro_timer():
    quadro_timer = t.Turtle()
    quadro_timer.speed(0)
    #quadro_timer.color("white")
    quadro_timer.color((200, 200, 200))  # White color in RGB
    quadro_timer.penup()
    quadro_timer.hideturtle()
    quadro_timer.goto(0, -ALTURA_JANELA/2)
    quadro_timer.write("00:00", align="center", font=('Monaco', 92*ESCALA_TIPOGRAFIA, "normal"))
    return quadro_timer

def atualiza_power_bar(estado_jogo, jogador):
    barra = estado_jogo[f'power_bar_{jogador.split("_")[1]}']
    dur = estado_jogo['power_shot_info'][jogador]['duration']
    if estado_jogo['power_shot_info'][jogador]['pressed_time'] is not None:
        dur = min(time.time() - estado_jogo['power_shot_info'][jogador]['pressed_time'], estado_jogo['power_shot_info']['max_duration'])

    ratio = dur / estado_jogo['power_shot_info']['max_duration']
    comprimento = 40*DEFAULT_TURTLE_SCALE
    altura = 3*DEFAULT_TURTLE_SCALE
    filled = comprimento * ratio

    barra.clear()
    
    barra.goto(estado_jogo[jogador].xcor() - comprimento/2, estado_jogo[jogador].ycor() + 13*DEFAULT_TURTLE_SCALE)
    barra.pendown()
    barra.begin_fill()
    barra.forward(filled)
    barra.left(90)
    barra.forward(altura)
    barra.left(90)
    barra.forward(filled)
    barra.left(90)
    barra.forward(altura)
    barra.left(90)
    barra.end_fill()
    barra.penup()

def terminar_jogo(estado_jogo, estado_campeonato):
    '''
     Função responsável por terminar o jogo. 
    '''
    print("Adeus")

    jogo = encontrar_jogo_por_jogadores(estado_campeonato, JOGADOR_VERMELHO, JOGADOR_AZUL)
    jogo['vencedor'] = JOGADOR_VERMELHO if estado_jogo['pontuacao_jogador_vermelho'] > estado_jogo['pontuacao_jogador_azul'] else JOGADOR_AZUL if estado_jogo['pontuacao_jogador_azul'] > estado_jogo['pontuacao_jogador_vermelho'] else None


    #guardar_estado_campeonato(estado_campeonato)
    estado_jogo['janela'].bye()

def arrancar_jogo(estado_jogo):
    '''
    Função responsável por arrancar o jogo. 
    Deverá ser chamada quando o jogador pressionar a tecla Enter.
    '''
    estado_jogo['timer'] = time.time() #inicializa o timer do jogo

    estado_jogo['arrancou'] = True
    #estado_jogo['bola']['objecto'].showturtle()
    #estado_jogo['bola']['objecto'].setheading(random.randint(0, 360))
    #estado_jogo['bola']['objecto'].speed(BALL_SPEED)    

def get_formatted_time(time_inicial):
    delta = time.time() - time_inicial  # Current time in seconds (float)
    minutes = int(delta // 60) % 60
    seconds = int(delta % 60)
    milliseconds = int((delta - int(delta)) * 1000)
    #return f"{minutes:02}:{seconds:02}:{milliseconds:03}"
    return f"{minutes:02}:{seconds:02}"

def atualiza_timer(estado_jogo):
    if 'timer' in estado_jogo and estado_jogo['timer'] is not None:
        tempo_decorrido = get_formatted_time(estado_jogo['timer'])
        estado_jogo['quadro_timer'].goto(0, -ALTURA_JANELA/2)
        estado_jogo['quadro_timer'].clear()
        estado_jogo['quadro_timer'].write(f"{tempo_decorrido}", align="center", font=('Monaco', 92*ESCALA_TIPOGRAFIA, "normal"))

def setup(estado_jogo, jogar, funcoes_jogadores, estado_campeonato):
    janela = cria_janela()
    #Assign keys to play
    janela.listen()
    if jogar:
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_cima'], estado_jogo, 'jogador_vermelho') ,'w')
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_baixo'], estado_jogo, 'jogador_vermelho') ,'s')
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_esquerda'], estado_jogo, 'jogador_vermelho') ,'a')
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_direita'], estado_jogo, 'jogador_vermelho') ,'d')
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_cima'], estado_jogo, 'jogador_azul') ,'Up')
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_baixo'], estado_jogo, 'jogador_azul') ,'Down')
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_esquerda'], estado_jogo, 'jogador_azul') ,'Left')
        janela.onkeypress(functools.partial(funcoes_jogadores['jogador_direita'], estado_jogo, 'jogador_azul') ,'Right')
        # Jogador vermelho (e.g., left SHIFT)
        janela.onkeypress(functools.partial(start_power_shot,  estado_jogo, 'jogador_vermelho'), 'Shift_L')
        janela.onkeypress(functools.partial(start_power_shot,  estado_jogo, 'jogador_azul'), 'Shift_R')
        janela.onkeypress(functools.partial(terminar_jogo, estado_jogo, estado_campeonato) ,'Escape')
        janela.onkeypress(functools.partial(arrancar_jogo, estado_jogo) ,' ')

    
       
    desenha_linhas_campo()
    estado_jogo['quadro_timer'] = cria_quadro_timer() 
    estado_jogo['quadro'] =  cria_quadro_resultados(estado_campeonato)
    

    bola = criar_bola()
    jogador_vermelho = cria_jogador(-((ALTURA_JANELA / 2) + LADO_MENOR_AREA), 0, "red")
    jogador_azul = cria_jogador(((ALTURA_JANELA / 2) + LADO_MENOR_AREA), 0, "blue")
    estado_jogo['power_bar_vermelho'] = t.Turtle()
    estado_jogo['power_bar_azul'] = t.Turtle()
    for barra in [estado_jogo['power_bar_vermelho'], estado_jogo['power_bar_azul']]:
        barra.hideturtle()
        barra.penup()
        barra.color("white")

    estado_jogo['janela'] = janela
    estado_jogo['bola'] = bola
    estado_jogo['jogador_vermelho'] = jogador_vermelho
    estado_jogo['jogador_azul'] = jogador_azul
    estado_jogo['power_shot_info'] = {
        'jogador_vermelho': {'pressed_time': None, 'duration': 0},
        'jogador_azul': {'pressed_time': None, 'duration': 0},
        'max_duration': 2.0,
        'base_speed': 1,
        'max_speed': 4,
}
    


def inicia_jogo(estado_jogo):
    #estado_jogo['arrancou'] = False
    estado_jogo['var' ]['bola'] = []
    estado_jogo['var']['jogador_vermelho'] = []
    estado_jogo['var']['jogador_azul'] = []
    goto(BOLA_START_POS[0],BOLA_START_POS[1], estado_jogo['bola']['objecto'])
    
    velocidade_bola_x, velocidade_bola_y = inicia_velocidades_bola()
    estado_jogo['bola']['velocidade_bola_x'] = velocidade_bola_x
    estado_jogo['bola']['velocidade_bola_y'] = velocidade_bola_y

def update_board(estado_jogo, estado_campeonato):
    jogo = encontrar_jogo_por_jogadores(estado_campeonato, JOGADOR_VERMELHO, JOGADOR_AZUL)

    jogo['pontuacao_jogador_vermelho'] = estado_jogo['pontuacao_jogador_vermelho']
    jogo['pontuacao_jogador_azul'] = estado_jogo['pontuacao_jogador_azul']

    estado_jogo['quadro'].clear()
    #estado_jogo['quadro'].write("Player A: {}\t\tPlayer B: {} ".format(estado_jogo['pontuacao_jogador_vermelho'], estado_jogo['pontuacao_jogador_azul']),align="center",font=('Monaco',24,"normal"))
    
    estado_jogo['quadro'].write("{} : {}".format(estado_jogo['pontuacao_jogador_vermelho'], estado_jogo['pontuacao_jogador_azul']),align="center",font=('Monaco',24*ESCALA_TIPOGRAFIA,"normal"))
    
    estado_jogo['quadro'].hideturtle()
    estado_jogo['quadro'].goto(0,ALTURA_JANELA/2-PADDING_PAINEL-24*ESCALA_TIPOGRAFIA)
    estado_jogo['quadro'].write("{}\t\t\t\t{}".format(get_nome_jogador(estado_campeonato, JOGADOR_VERMELHO), get_nome_jogador(estado_campeonato, JOGADOR_AZUL)), align="center", font=('Monaco',24*ESCALA_TIPOGRAFIA,"normal"))

def encontrar_jogo_por_jogadores(estado_campeonato, jogador1_id, jogador2_id):
    for divisao, info_divisao in estado_campeonato.get('jogos', {}).items():
        for jogo in info_divisao.get('jogos', []):
            if (jogo['jogador_vermelho'] == jogador1_id and jogo['jogador_azul'] == jogador2_id) or \
               (jogo['jogador_vermelho'] == jogador2_id and jogo['jogador_azul'] == jogador1_id):
                return jogo
    return None

def movimenta_bola(estado_jogo):
    '''
    Função responsável pelo movimento da bola que deverá ser feito tendo em conta a
    posição atual da bola e a direção em xx e yy.
    '''
    new_x = estado_jogo['bola']['objecto'].xcor() + estado_jogo['bola']['velocidade_bola_x']
    new_y = estado_jogo['bola']['objecto'].ycor() + estado_jogo['bola']['velocidade_bola_y']
    new_x = max(-LARGURA_JANELA/2, min(LARGURA_JANELA/2, new_x))
    new_y = max(-ALTURA_JANELA/2, min(ALTURA_JANELA/2, new_y))
    estado_jogo['bola']['posicao_anterior'] = estado_jogo['bola']['objecto'].pos()
    #print('prev pos', estado_jogo['bola']['posicao_anterior'] )
    #print(new_x- estado_jogo['bola']['posicao_anterior'][0])
    goto(new_x, new_y, estado_jogo['bola']['objecto'])

def verifica_colisoes_ambiente(estado_jogo):
    '''
    Função responsável por verificar se há colisões com os limites do ambiente, 
    atualizando a direção da bola. Não se esqueça de considerar que nas laterais, 
    fora da zona das balizas, a bola deverá inverter a direção onde atingiu o limite.
    '''
    x, y = estado_jogo['bola']['objecto'].xcor(), estado_jogo['bola']['objecto'].ycor()
    if x-RAIO_BOLA <= -LARGURA_JANELA/2 or x+RAIO_BOLA >= LARGURA_JANELA/2:
        estado_jogo['bola']['velocidade_bola_x']*=-1
    if y-RAIO_BOLA <= -ALTURA_JANELA/2 or y+RAIO_BOLA >= ALTURA_JANELA/2:
        estado_jogo['bola']['velocidade_bola_y']*=-1

def verifica_golos(estado_jogo, estado_campeonato, verifica_golo_jogador_vermelho, verifica_golo_jogador_azul):
    
    golo_vermelho = verifica_golo_jogador_vermelho(estado_jogo)
    golo_azul = verifica_golo_jogador_azul(estado_jogo)
    if golo_vermelho or golo_azul:
        update_board(estado_jogo, estado_campeonato)
        inicia_jogo(estado_jogo)


def ressalto_bola(jogador, estado_jogo):
    ang = math.atan2(
            estado_jogo['bola']['objecto'].ycor() - estado_jogo[jogador].ycor(),
            estado_jogo['bola']['objecto'].xcor() - estado_jogo[jogador].xcor()
        )
    speed = get_power_speed(estado_jogo, jogador)
    estado_jogo['power_shot_info'][jogador]['duration'] = 0  # reset after use
    
    release_power_shot(estado_jogo, jogador)

    estado_jogo['bola']['velocidade_bola_x'] = BALL_SPEED * speed * math.cos(ang)
    estado_jogo['bola']['velocidade_bola_y'] = BALL_SPEED * speed * math.sin(ang)
    
    x_novo = estado_jogo[jogador].xcor() + (RAIO_BOLA+RAIO_JOGADOR+1) * math.cos(ang)
    y_novo = estado_jogo[jogador].ycor() + (RAIO_BOLA+RAIO_JOGADOR+1) * math.sin(ang)
    
    
    goto(x_novo,y_novo, estado_jogo['bola']['objecto'])

def verifica_toque_jogador_azul(estado_jogo):
    '''
    Função responsável por verificar se o jogador tocou na bola. 
    Sempre que um jogador toca na bola, deverá mudar a direção desta.
    '''
    if(estado_jogo['jogador_azul'].distance(estado_jogo['bola']['objecto'])<RAIO_BOLA+RAIO_JOGADOR):
        ressalto_bola('jogador_azul', estado_jogo)


def verifica_toque_jogador_vermelho(estado_jogo):
    '''
    Função responsável por verificar se o jogador tocou na bola. 
    Sempre que um jogador toca na bola, deverá mudar a direção desta.
    '''
    if(estado_jogo['jogador_vermelho'].distance(estado_jogo['bola']['objecto'])<RAIO_BOLA+RAIO_JOGADOR):
        ressalto_bola('jogador_vermelho', estado_jogo)
        
