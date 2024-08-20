from threading import Thread, Lock, Condition
from time import sleep
import os
from concurrent.futures import ThreadPoolExecutor
import random
from queue import Queue

# Classe Barreira implementa um mecanismo de sincronização que permite que um número específico de threads
# aguarde até que todas as threads esperem no mesmo ponto, momento em que todas são liberadas para continuar.
class Barreira:
    def __init__(self, n):
        self.n = n
        self.count = 0
        self.condition = Condition()

    def esperar(self):
        with self.condition:
            self.count += 1
            if self.count == self.n:
                self.count = 0
                self.condition.notify_all()
            else:
                self.condition.wait()


# Classe Semaforo implementa um semáforo que controla o acesso a um recurso compartilhado.
# Ele permite um número limitado de threads acessar o recurso simultaneamente.
class Semaforo:
    def __init__(self, valor_inicial=1):
        self.valor = valor_inicial
        self.lock = Lock()
        self.condicao = Condition(self.lock)

    def adquirir(self):
        with self.condicao:
            while self.valor == 0:
                self.condicao.wait()
            self.valor -= 1

    def liberar(self):
        with self.condicao:
            self.valor += 1
            self.condicao.notify()

# Classe Mapa representa o tabuleiro da corrida, incluindo a criação do mapa e a gestão de obstáculos.
# Também controla as posições onde os semáforos estão colocados para sincronização de acesso.
class Mapa:
    def __init__(self, length, height, validPosition="|"):
        self.mapa = self._generate_template_map(length, height, validPosition)
        self.positions_lock = self._generate_semaphore_positions(length, height)

    def _generate_template_map(self, length, height, validPosition):
        mapa = []
        for i in range(height):
            linha = []
            for j in range(length):
                if i == 0:
                    linha.append("=")
                else:
                    linha.append(validPosition)
            mapa.append(linha)
        return mapa

    def _generate_semaphore_positions(self, length, height):
        return [[Semaforo() for _ in range(length)] for _ in range(height)]

    def create_obstacles(self, non_obstacle_on_first=1):
        row_quantities = len(self.mapa)
        for i in range(row_quantities):
            row_length = len(self.mapa[0])
            if (i >= (row_quantities - non_obstacle_on_first)) or i == 0:
                continue
            for j in range(row_length):
                if (i % 2) == 0 and (j % 2) != 0:
                    self.mapa[i][j] = "0"
                if (i % 2) != 0 and (j % 2) == 0:
                    self.mapa[i][j] = "0"
        return self.mapa

    def free_position(self, x, y, validPosition="|"):
        self.positions_lock[x][y].liberar()
        self.mapa[x][y] = validPosition

    def print_mapa(self):
        for row in self.mapa:
            print(" ".join(row))
    
    def update_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_mapa()


# Classe Corrida gerencia a lógica da corrida de cavalos, incluindo a movimentação dos cavalos e a geração de modificadores de velocidade.
# Também coordena o consumo e produção de modificadores de velocidade e mantém o placar.
class Corrida:
    def __init__(self, mapa, active_threads=6):
        self.mapa = mapa
        self.active_threads = active_threads
        self.barreira = Barreira(active_threads + 1)
        self.ganhadores = []
        self.consumer_buffer = Queue(active_threads)
        self.buffer = Queue(50)
        self.condicao = Condition()

    def consume_modifier_buffer(self):
        while True:
            with self.condicao:
                while self.buffer.empty():
                    self.condicao.wait()
                item = self.buffer.get()
                self.condicao.notify_all()
            return item

    #Executa em thread à parte!
    def generate_speed_modifier(self):
        while True:
            modifier = random.uniform(0, 2)
            with self.condicao:
                while self.buffer.full():
                    self.condicao.wait()
                self.buffer.put(modifier)
                self.condicao.notify_all()

    def walk_horse(self, init_position):
        positionY = init_position
        horse_name = "R" + str(init_position)

        self.mapa.positions_lock[len(self.mapa.mapa) - 1][positionY].adquirir()
        self.mapa.mapa[len(self.mapa.mapa) - 1][positionY] = horse_name
        self.mapa.update_screen()

        for i in range((len(self.mapa.mapa) - 1), 0, -1): 
            while True:   
                if i > 0 and (self.mapa.mapa[i - 1][positionY] == "|" or self.mapa.mapa[i - 1][positionY] == "="):
                    self.mapa.free_position(i, positionY)
                    self.mapa.positions_lock[i - 1][positionY].adquirir()
                    self.mapa.mapa[i - 1][positionY] = horse_name
                    self.mapa.update_screen()
                    sleep(2 * self.consume_modifier_buffer())
                    break

                if i > 0 and positionY > 0 and (self.mapa.mapa[i - 1][positionY - 1] == "|" or self.mapa.mapa[i - 1][positionY - 1] == "="):
                    self.mapa.free_position(i, positionY)
                    self.mapa.positions_lock[i - 1][positionY - 1].adquirir()
                    self.mapa.mapa[i - 1][positionY - 1] = horse_name
                    positionY -= 1
                    self.mapa.update_screen()
                    sleep(2 * self.consume_modifier_buffer())
                    break

                if i > 0 and positionY < (len(self.mapa.mapa[0]) - 1) and (self.mapa.mapa[i - 1][positionY + 1] == "|" or self.mapa.mapa[i - 1][positionY + 1] == "="):
                    self.mapa.free_position(i, positionY)
                    self.mapa.positions_lock[i - 1][positionY + 1].adquirir()
                    self.mapa.mapa[i - 1][positionY + 1] = horse_name
                    positionY += 1
                    self.mapa.update_screen()
                    sleep(2 * self.consume_modifier_buffer())
                    break

                if i <= 2 and positionY > 0 and (self.mapa.mapa[i - 1][positionY - 1] not in ["=", "|"]) and positionY < (len(self.mapa.mapa[0]) - 1) and (self.mapa.mapa[i - 1][positionY + 1] not in ["=", "|"]):
                    break

                sleep(1)
        with self.condicao:
            self.consumer_buffer.put(horse_name)
            self.ganhadores.append(horse_name)
            self.condicao.notify()
        self.barreira.esperar()

    def mostrar_placar(self):
        self.barreira.esperar()
        print("========= Placar da Corrida =========")   
        for i, ganhador in enumerate(self.ganhadores):
            print(f"{i + 1}° lugar: {ganhador}")

    def iniciar_corrida(self):
        final_map = self.mapa.create_obstacles()
        
        with ThreadPoolExecutor(max_workers=self.active_threads + 2) as executor:
            executor.submit(self.generate_speed_modifier)
            for i in range(self.active_threads):
                executor.submit(self.walk_horse, i + 2)
            executor.submit(self.mostrar_placar)

def main():
    mapa = Mapa(length=15, height=10)
    corrida = Corrida(mapa, active_threads=6)
    corrida.iniciar_corrida()

if __name__ == "__main__":
    main()
