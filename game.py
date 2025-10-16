import sys
import pygame
import random
import json
from pygame.locals import *

pygame.init()

# Configurações básicas
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroid Runner")

# Carregar fundo
background = pygame.image.load("data/fundo.png")

# Inicializa o mixer de áudio para música
pygame.mixer.init()

# Lista de trilhas sonoras
musicas = ["musicas/trilha2.mp3", "musicas/trilha3.mp3"]
musica_atual = random.choice(musicas)  # Escolhe uma música inicial

def tocar_musica():
    global musica_atual
    pygame.mixer.music.load(musica_atual)
    pygame.mixer.music.play(-1)  # -1 faz a música tocar em loop

def trocar_musica():
    global musica_atual
    nova_musica = musica_atual
    while nova_musica == musica_atual:  # Garante que a nova música seja diferente
        nova_musica = random.choice(musicas)
    musica_atual = nova_musica
    pygame.mixer.music.load(musica_atual)
    pygame.mixer.music.play(-1)

# Chama a música ao iniciar o jogo
tocar_musica()

# Carregar fonte personalizada
def carregar_fonte(tamanho):
    try:
        return pygame.font.Font("fontes/fonte_menu.ttf", tamanho)
    except:
        return pygame.font.SysFont("comicsansms", tamanho, True, False)

fonte = carregar_fonte(30)

# Carregar scoreboard
SCOREBOARD_FILE = "scoreboard/scoreboard.json"

def carregar_scoreboard():
    try:
        with open(SCOREBOARD_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def salvar_scoreboard(scoreboard):
    with open(SCOREBOARD_FILE, "w") as file:
        json.dump(scoreboard, file)

scoreboard = carregar_scoreboard()

# Variável de pontos e nome do jogador
pontos = 0
player_name = ""

# Definição do jogador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("data/foguete.png")
        self.surf = pygame.transform.scale(self.surf, (70, 70))
        self.rect = self.surf.get_rect(center=(100, SCREEN_HEIGHT // 2))
        self.mask = pygame.mask.from_surface(self.surf)

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -4)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 4)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-4, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(4, 0)
        
        self.rect.clamp_ip(screen.get_rect())

# Definição dos inimigos (asteroides)
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("data/asteroide.png")
        self.surf = pygame.transform.scale(self.surf, (70, 70))
        self.rect = self.surf.get_rect(center=(random.randint(820, 900), random.randint(0, SCREEN_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.surf)
        self.speed = random.uniform(3, 5)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

# Exibir mensagens
def exibir_mensagem(msg, tamanho, pos):
    fonte = carregar_fonte(tamanho)
    texto = fonte.render(msg, True, (255, 255, 255))
    screen.blit(texto, pos)

# Configuração do timer para aumentar a dificuldade
ADDENEMY = pygame.USEREVENT + 1
INCREASE_DIFFICULTY = pygame.USEREVENT + 2
spawn_rate = 500  # Começa com um asteroide a cada 500ms

pygame.time.set_timer(ADDENEMY, spawn_rate)
pygame.time.set_timer(INCREASE_DIFFICULTY, 10000)  # A cada 10 segundos

# Função principal do jogo
def main():
    global pontos, scoreboard, player_name, spawn_rate
    pontos = 0 
    running = True
    game_over = False

    player = Player()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    while running:
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                menu_inicial()
            if event.type == KEYDOWN and event.key == K_r and game_over:
                main()
            if event.type == ADDENEMY and not game_over:
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)
            if event.type == KEYDOWN and event.key == K_m:
                trocar_musica()  # Troca a música ao pressionar "M"
            if event.type == INCREASE_DIFFICULTY:
                spawn_rate = max(200, spawn_rate - 50)  # Diminui intervalo, mínimo de 200ms
                pygame.time.set_timer(ADDENEMY, spawn_rate)  # Atualiza taxa de spawn

        if not game_over:
            pressed_keys = pygame.key.get_pressed()
            player.update(pressed_keys)
            enemies.update()

            if pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask):
                game_over = True
                player.kill()
                scoreboard.append({"name": player_name, "score": pontos})
                scoreboard = sorted(scoreboard, key=lambda x: x["score"], reverse=True)[:10]
                salvar_scoreboard(scoreboard)

        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        if not game_over:
            pontos += 1
        exibir_mensagem(f"Pontos: {pontos}", 30, (650, 20))

        if game_over:
            exibir_mensagem("GAME OVER", 100, (160, 200))
            exibir_mensagem("Pressione R para reiniciar ou ESC para menu", 30, (130, 300))

        pygame.display.flip()

# Menu inicial
def menu_inicial():
    global player_name
    player_name = ""
    menu_running = True
    while menu_running:
        screen.fill((0, 0, 0))
        exibir_mensagem("Asteroid Runner", 100, (70, 100))
        exibir_mensagem("Digite seu nome: " + player_name, 25, (200, 250))
        exibir_mensagem("Pressione ENTER para jogar", 25, (200, 300))
        exibir_mensagem("Pressione L para leaderboard", 25, (200, 350))
        exibir_mensagem("Pressione ESC para sair", 25, (200, 400))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and player_name:
                    main()
                elif event.key == K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == K_l:
                    leaderboard()
                elif event.unicode.isalnum() and len(player_name) < 10:
                    player_name += event.unicode

        pygame.display.flip()

# Leaderboard com rolagem usando o scroll do mouse
def leaderboard():
    scroll_offset = 0
    leaderboard_running = True

    # Filtra as 10 maiores pontuações
    scoreboard_display = sorted(scoreboard, key=lambda x: x["score"], reverse=True)[:10]

    # Ajuste para exibição correta
    line_height = 30  # Altura de cada linha
    screen_height = 600  # Altura da tela
    max_scroll = max(0, len(scoreboard_display) * line_height - screen_height)  # Ajusta o limite inferior da rolagem

    while leaderboard_running:
        screen.fill((0, 0, 0))
        exibir_mensagem("Leaderboard", 80, (190, 50))

        # Exibe a tabela fixa com as 10 maiores pontuações
        for i, entry in enumerate(scoreboard_display):
            pos_y = 150 + (i * line_height) - scroll_offset
            if 150 <= pos_y <= screen_height - line_height:  # Exibe apenas as entradas visíveis
                exibir_mensagem(f"{i+1}. {entry['name']} - {entry['score']}", 30, (250, pos_y))

        exibir_mensagem("Pressione ESC para voltar", 30, (230, 500))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                leaderboard_running = False

        pygame.display.flip()

menu_inicial()
