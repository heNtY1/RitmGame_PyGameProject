import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
ARROW_SIZE = 50
ARROW_SPEED = 5
FONT_SIZE = 40
BEAT_INTERVAL = 500  # Интервал между появлениями стрелок (в миллисекундах)

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
RECT_COLOR = (200, 200, 200)  # Цвет прямоугольника

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Нажми на стрелку в бит")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

# Стрелки
arrows = []
arrow_types = ['UP', 'DOWN', 'LEFT', 'RIGHT']
last_beat_time = 0


# Функция для создания новой стрелки
def create_arrow():
    arrow_type = random.choice(arrow_types)
    x_pos = random.randint(0, WIDTH - ARROW_SIZE)
    return {'type': arrow_type, 'x': x_pos, 'y': -ARROW_SIZE}


# Основной игровой цикл
def game_loop():
    score = 0
    running = True

    # Создание первой стрелки
    arrows.append(create_arrow())

    global last_beat_time

    while running:
        screen.fill(WHITE)

        # Отрисовка прямоугольника для засчитывания нажатий
        rect_y_start = 400
        rect_y_end = 600
        pygame.draw.rect(screen, RECT_COLOR, (0, rect_y_start, WIDTH, 400))

        # Проверка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if arrows and event.key == pygame.K_UP and arrows[0]['type'] == 'UP':
                    if rect_y_start < arrows[0]['y'] < rect_y_end:
                        score += 1
                        arrows.pop(0)
                elif arrows and event.key == pygame.K_DOWN and arrows[0]['type'] == 'DOWN':
                    if rect_y_start < arrows[0]['y'] < rect_y_end:
                        score += 1
                        arrows.pop(0)
                elif arrows and event.key == pygame.K_LEFT and arrows[0]['type'] == 'LEFT':
                    if rect_y_start < arrows[0]['y'] < rect_y_end:
                        score += 1
                        arrows.pop(0)
                elif arrows and event.key == pygame.K_RIGHT and arrows[0]['type'] == 'RIGHT':
                    if rect_y_start < arrows[0]['y'] < rect_y_end:
                        score += 1
                        arrows.pop(0)

        # Обновление стрелок
        for arrow in list(arrows):
            arrow['y'] += ARROW_SPEED
            if arrow['y'] > HEIGHT:
                running = False  # Игра заканчивается, если стрелка достигает низа экрана

        # Отрисовка стрелок
        for arrow in arrows:
            if arrow['type'] == 'UP':
                pygame.draw.polygon(screen, RED, [(150, arrow['y']),
                                                  (150 + ARROW_SIZE // 2, arrow['y'] + ARROW_SIZE),
                                                  (150 - ARROW_SIZE // 2, arrow['y'] + ARROW_SIZE)])
            elif arrow['type'] == 'DOWN':
                pygame.draw.polygon(screen, GREEN, [(350, arrow['y']),
                                                    (350 + ARROW_SIZE // 2, arrow['y'] - ARROW_SIZE),
                                                    (350 - ARROW_SIZE // 2, arrow['y'] - ARROW_SIZE)])
            elif arrow['type'] == 'LEFT':
                pygame.draw.polygon(screen, BLUE, [(450, arrow['y']),
                                                   (450 + ARROW_SIZE, arrow['y'] + ARROW_SIZE // 2),
                                                   (450 + ARROW_SIZE, arrow['y'] - ARROW_SIZE // 2)])
            elif arrow['type'] == 'RIGHT':
                pygame.draw.polygon(screen, PURPLE, [(650, arrow['y']),
                                                     (650 - ARROW_SIZE, arrow['y'] + ARROW_SIZE // 2),
                                                     (650 - ARROW_SIZE, arrow['y'] - ARROW_SIZE // 2)])

        # Отрисовка счета
        score_text = font.render(f'Score: {score}', True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Проверка времени для появления новых стрелок в ритме музыки
        current_time = pygame.time.get_ticks()
        if current_time - last_beat_time >= BEAT_INTERVAL:
            arrows.append(create_arrow())
            last_beat_time = current_time

        pygame.display.flip()
        clock.tick(FPS)

    print(f"Game Over! Your score: {score}")
    pygame.quit()


# Функция для отображения главного меню
def main_menu():
    # Инициализация музыки
    pygame.mixer.music.load(
        'data\\INTERWORLD — METAMORPHOSIS (www.lightaudio.ru).mp3')  # Замените на имя вашего файла с музыкой
    pygame.mixer.music.set_volume(0.5)  # Установите громкость от 0.0 до 1.0

    while True:
        screen.fill(WHITE)

        # Отображение текста "Нажми чтобы начать"
        start_text = font.render("Нажми чтобы начать", True, (0, 0, 0))
        text_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(start_text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    pygame.mixer.music.play(-1)  # Запускаем музыку в бесконечном цикле
                    game_loop()  # Запускаем игру

        pygame.display.flip()
        clock.tick(FPS)


# Главная программа
if __name__ == '__main__':
    main_menu()  # Запускаем главное меню
