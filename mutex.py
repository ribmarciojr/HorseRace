from threading import Lock, current_thread
from time import sleep
import os
from concurrent.futures import ThreadPoolExecutor



ACTIVE_THREADS = 5


def generate_template_map(length, height, validPosition="|"):
    mapa = []
    for i in range(height):
        linha = []
        for j in range(length):
            if i == 0:
                linha.append("=")
                continue
            linha.append(validPosition)
        mapa.append(linha)

    return mapa


def generate_lock_positions(length, height, validPosition="|"):
    mapa = []
    for i in range(height):
        linha = []
        for j in range(length):
            if i == 0:
                linha.append(Lock())
                continue
            linha.append(Lock())
        mapa.append(linha)

    return mapa

positions_lock = generate_lock_positions(6, 10)

def print_mapa(mapa):
    row_quantities = len(mapa)

    for i in range(row_quantities):
        row_length = len(mapa[0]) 

        for j in range(row_length):
            last_position = len(mapa[0]) - 1
            
            if j == last_position:
                print(mapa[i][j], end="\n")
                continue

            print(mapa[i][j], end=" ")

""" Recebe o mapa e a quantidade de primeiras linhas que 
não terão obstáculos, em seguida, insere obstáculos em
posições pares, para colunas ímpares e posições impares
para colunas pares;
"""
def create_obstacles(mapa, non_obstacle_on_first=1):
    row_quantities = len(mapa)

    for i in range(row_quantities):
        row_length = len(mapa[0]) 
        
        if (i >= (row_quantities - non_obstacle_on_first)) or i == 0:
            continue

        for j in range(row_length):
            
            if (i % 2) == 0 and (j % 2) != 0:
                mapa[i][j] = "0"
            
            if (i % 2) != 0 and (j % 2) == 0:
                mapa[i][j] = "0"

    return mapa

def free_position(mapa,x, y, validPosition="|"):
    positions_lock[x][y].release()
    mapa[x][y] = validPosition

def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def update_screen(mapa):
    limpar_tela()
    print_mapa(mapa)
    return
position_lock = Lock()

ganhadores  = []

def walk_horse(mapa, init_position):
    positionY = init_position
    
    horse_name = "R" + str(init_position)

    positions_lock[len(mapa) - 1][positionY].acquire()
    mapa[len(mapa) - 1][positionY] = horse_name
    update_screen(mapa)
 
    for i in range((len(mapa) - 1), 0, -1): 
        
        while True:
            
            if i > 0 and (mapa[i - 1][positionY] == "|" or mapa[i - 1][positionY] == "="):
                free_position(mapa, i, positionY)
                positions_lock[i - 1][positionY].acquire()
                mapa[i - 1][positionY] = horse_name
                update_screen(mapa)
                
                sleep(2)
                break

            if i > 0 and positionY > 0 and (mapa[i - 1][positionY - 1] == "|" or mapa[i - 1][positionY - 1] == "="):
                free_position(mapa, i, positionY)
                positions_lock[i - 1][positionY - 1].acquire()
                mapa[i - 1][positionY - 1] = horse_name
                positionY -= 1
                update_screen(mapa)
                
                sleep(2)
                break
            if i > 0 and positionY < (len(mapa[0]) - 1) and (mapa[i - 1][positionY + 1] == "|" or mapa[i - 1][positionY + 1] == "="):
                free_position(mapa, i, positionY)
                positions_lock[i - 1][positionY + 1].acquire()
                mapa[i - 1][positionY + 1] = horse_name
                positionY += 1
                update_screen(mapa)
                
                sleep(2)
                break
            # Caso já existam threads segurando o recurso na esquerda e na direita, finaliza nessa posição, evitando deadlock;
            if i == 1 and positionY > 0 and (mapa[i - 1][positionY - 1] not in ["=", "|"]) and positionY < (len(mapa[0]) - 1) and (mapa[i - 1][positionY + 1] not in ["=", "|"]):
                break
            
            sleep(1)
    ganhadores.append(horse_name)

def boot_app():
    template_map = generate_template_map(length=6, height=10)

    final_map = create_obstacles(template_map)
    
    with ThreadPoolExecutor(max_workers=ACTIVE_THREADS) as executor:
        for i in range(ACTIVE_THREADS):
            executor.submit(walk_horse, final_map, i)
    
    for i in range(len(ganhadores)):
        print(f"{i + 1}° lugar: {ganhadores[i]}")

    return


if __name__ == "__main__":
    boot_app()
