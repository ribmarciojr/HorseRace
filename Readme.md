# Horse Race
## Visão Geral
Este é um jogo de corrida de cavalos baseado em texto, implementado em Python utilizando multithread. O jogo simula uma corrida onde múltiplos cavalos (representados por threads) competem em uma pista (um mapa em formato de grade). Os cavalos se movem em direção à linha de chegada, evitando obstáculos. A velocidade de cada cavalo é modificada por fatores aleatórios, tornando a corrida imprevisível.

## Como Jogar

### Requisitos
Python 3.10.x
Execução
Para iniciar o jogo, execute o seguinte comando:

### Execução

- Linux

``` 
python3 horse_race.py 
```

- Windows

``` 
python horse_race.py 
```


## Funcionalidades

### Multithread: 
- Cada cavalo é representado por uma thread que se move de forma independente na pista. 

### Sincronização: 
- O jogo utiliza semáforos, barreiras e variáveis de condição para sincronizar os movimentos dos cavalos e gerenciar o acesso aos recursos compartilhados.
### Modificadores de Velocidade Aleatórios: 
- A velocidade de cada cavalo é modificada dinamicamente por fatores aleatórios durante a corrida.
### Gestão de Obstáculos: 
- A pista contém obstáculos que os cavalos devem contornar.
### Resultados da Corrida: 
- O jogo exibe a classificação final dos cavalos ao término da corrida.

