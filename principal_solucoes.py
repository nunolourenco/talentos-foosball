from foosbal import *


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


if __name__ == '__main__':
    ##dicionario com as funcoes de movimento dos jogadores
    funcoes_jogadores = {'jogador_cima': jogador_cima, 'jogador_baixo': jogador_baixo, 'jogador_esquerda': jogador_esquerda, 'jogador_direita': jogador_direita}    
    
    #funções de inicio do jogo
    estado_jogo = init_state()
    setup(estado_jogo, True, funcoes_jogadores)
    inicia_jogo(estado_jogo)
    while True:
        estado_jogo['janela'].update() #actualiza a janela
        if estado_jogo['bola'] is not None:
            movimenta_bola(estado_jogo) #movimenta a bola

        verifica_colisoes_ambiente(estado_jogo) #verifica colisoes da bola com o ambiente (para mudar a sua direcao)
        verifica_golos(estado_jogo, verifica_golo_jogador_vermelho, verifica_golo_jogador_azul) #verifica se houve golo
        
        if estado_jogo['jogador_vermelho'] is not None:
            verifica_toque_jogador_vermelho(estado_jogo) #verifica se a bola tocou no jogador vermelho
        if estado_jogo['jogador_azul'] is not None:
            verifica_toque_jogador_azul(estado_jogo) #verifica se a bola tocou no jogador azul
