import pygame
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
ARROW_SIZE = 50
ARROW_SPEED = 5
FONT_SIZE = 40

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Нажми на стрелку")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

# Стрелки
arrows = []
arrow_types = ['UP', 'DOWN', 'LEFT', 'RIGHT']

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

    while running:
        screen.fill(WHITE)

        # Проверка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if arrows and event.key == pygame.K_UP and arrows[0]['type'] == 'UP':
                    score += 1
                    arrows.pop(0)
                elif arrows and event.key == pygame.K_DOWN and arrows[0]['type'] == 'DOWN':
                    score += 1
                    arrows.pop(0)
                elif arrows and event.key == pygame.K_LEFT and arrows[0]['type'] == 'LEFT':
                    score += 1
                    arrows.pop(0)
                elif arrows and event.key == pygame.K_RIGHT and arrows[0]['type'] == 'RIGHT':
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
                pygame.draw.polygon(screen, RED, [(arrow['x'], arrow['y']),
                                                    (arrow['x'] + ARROW_SIZE // 2, arrow['y'] + ARROW_SIZE),
                                                    (arrow['x'] - ARROW_SIZE // 2, arrow['y'] + ARROW_SIZE)])
            elif arrow['type'] == 'DOWN':
                pygame.draw.polygon(screen, GREEN, [(arrow['x'], arrow['y']),
                                                      (arrow['x'] + ARROW_SIZE // 2, arrow['y'] - ARROW_SIZE),
                                                      (arrow['x'] - ARROW_SIZE // 2, arrow['y'] - ARROW_SIZE)])
            elif arrow['type'] == 'LEFT':
                pygame.draw.polygon(screen, BLUE, [(arrow['x'], arrow['y']),
                                                     (arrow['x'] + ARROW_SIZE, arrow['y'] + ARROW_SIZE // 2),
                                                     (arrow['x'] + ARROW_SIZE, arrow['y'] - ARROW_SIZE // 2)])
            elif arrow['type'] == 'RIGHT':
                pygame.draw.polygon(screen, BLUE, [(arrow['x'], arrow['y']),
                                                     (arrow['x'] - ARROW_SIZE, arrow['y'] + ARROW_SIZE // 2),
                                                     (arrow['x'] - ARROW_SIZE, arrow['y'] - ARROW_SIZE // 2)])

        # Отрисовка счета
        score_text = font.render(f'Score: {score}', True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Добавление новой стрелки через определенные интервалы времени
        if len(arrows) < 5 and random.random() < 0.02:  # Вероятность появления новой стрелки
            arrows.append(create_arrow())

        pygame.display.flip()
        clock.tick(FPS)

    print(f"Game Over! Your score: {score}")
    pygame.quit()

if __name__ == '__main__':
    game_loop()