import os
import random
import sys
import datetime

import librosa
import numpy as np
import pygame
from PIL import Image

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
ARROW_SIZE = 128
ARROW_SPEED = 5
FONT_SIZE = 40
BEAT_INTERVAL = 500  # Интервал между появлениями стрелок (в миллисекундах)
GRAVITY = 1
screen_rect = (0, 0, WIDTH, HEIGHT)
DELTA = datetime.timedelta(0, 0, 60)  # Регулировка частоты появления стрелок

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
RECT_COLOR = (200, 200, 200)  # Цвет прямоугольника

key_bindings = {
    'UP': pygame.K_UP,
    'DOWN': pygame.K_DOWN,
    'LEFT': pygame.K_LEFT,
    'RIGHT': pygame.K_RIGHT,
}

fixed_x_positions = {
    'UP': 150,
    'DOWN': 300,
    'LEFT': 500,
    'RIGHT': 650
}

# Стрелки
arrow_types = ['UP', 'DOWN', 'LEFT', 'RIGHT']
last_beat_time = 0

# Загрузка спрайтов стрелок
arrow_up_sprite = pygame.image.load(os.path.join('data', 'Вверх.png'))  # Убедитесь, что файл существует
arrow_down_sprite = pygame.image.load(os.path.join('data', 'Вниз.png'))
arrow_left_sprite = pygame.image.load(os.path.join('data', 'Влево.png'))
arrow_right_sprite = pygame.image.load(os.path.join('data', 'Вправо.png'))

# Измените размер спрайтов, если необходимо
arrow_up_sprite = pygame.transform.scale(arrow_up_sprite, (ARROW_SIZE, ARROW_SIZE))
arrow_down_sprite = pygame.transform.scale(arrow_down_sprite, (ARROW_SIZE, ARROW_SIZE))
arrow_left_sprite = pygame.transform.scale(arrow_left_sprite, (ARROW_SIZE, ARROW_SIZE))
arrow_right_sprite = pygame.transform.scale(arrow_right_sprite, (ARROW_SIZE, ARROW_SIZE))

# Музыка
music_tracks = [
    'moondeity-neon-blade-mp3.mp3',
    'INTERWORLD — METAMORPHOSIS (www.lightaudio.ru).mp3',
    'Весокосный год - Где-то там далеко-далеко есть земля (OST Дальнобойщики).mp3',
    'Vova_Solodkov_-_Barabulka_78505531.mp3',
    'Remzcore — Dynamite [SLOWED] (www.lightaudio.ru).mp3'
]

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Нажми на стрелку в бит")
clock = pygame.time.Clock()
font_path = os.path.join('data', 'шрифт.ttf')
font_size = 36
font = pygame.font.Font(font_path, font_size)

# Переменные для кнопки выхода
exit_button_text = font.render("Выход", True, WHITE)
exit_button_rect = exit_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
exit_click_count = 0
yes_button_text = font.render("Да", True, WHITE)
no_button_text = font.render("Нет", True, WHITE)
yes_button_rect = yes_button_text.get_rect(center=(WIDTH // 2 - 100, HEIGHT // 2 + 50))
no_button_rect = no_button_text.get_rect(center=(WIDTH // 2 + 100, HEIGHT // 2 + 50))


class Arrow(pygame.sprite.Sprite):
    def __init__(self, types):
        super().__init__(all_sprites, arrows)
        if types == 'UP':
            self.image = arrow_up_sprite
        elif types == 'DOWN':
            self.image = arrow_down_sprite
        elif types == 'LEFT':
            self.image = arrow_left_sprite
        elif types == 'RIGHT':
            self.image = arrow_right_sprite

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.type = types
        self.rect.x = fixed_x_positions[self.type]
        self.rect.y = -50

    def update(self):
        self.rect.y += ARROW_SPEED

    def get_cor(self):
        return self.rect.centerx, self.rect.centery

    def get_type(self):
        return self.type

    def delete(self):
        self.kill()


class Table(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, hight):
        super().__init__(all_sprites)
        self.image = pygame.Surface((800, hight))
        pygame.draw.rect(self.image, RECT_COLOR, (0, 0, 800, hight))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x_pos
        self.rect.y = y_pos


class FadingArrow(pygame.sprite.Sprite):
    def __init__(self, arrow_image, position):
        super().__init__(fading_arrows_group)
        self.image = arrow_image
        self.rect = self.image.get_rect(center=position)
        self.alpha = 255

    def update(self):
        self.rect.y -= 5  # Движение вверх
        self.alpha -= 25
        if self.alpha < 0:
            self.alpha = 0

        self.image.set_alpha(self.alpha)

        if self.alpha == 0:
            self.kill()


class Particle(pygame.sprite.Sprite):
    fire = [pygame.image.load(os.path.join('data', 'star.png'))]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(particles_group)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect(center=pos)  # Центрируем изображение по позиции
        self.velocity = [dx, dy]
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Удаляем партикл, если он выходит за пределы экрана
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Функция для создания частиц
def create_particles(position):
    particle_count = 10
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def load_beats(track_path):
    y, sr = librosa.load(os.path.join('data', track_path))
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    beats = times[onset_frames]
    return beats


def game_loop():
    running = True
    score = 0
    game_over = False
    dt = datetime.datetime.now()

    # Создание зоны поражения
    table_height = 80
    table = Table(0, HEIGHT - table_height, table_height)

    # Случайный выбор трека
    track_path = random.choice(music_tracks)
    beats = load_beats(track_path)
    last_beat_index = 0

    # Воспроизведение выбранного трека
    pygame.mixer.music.load(os.path.join('data', track_path))
    pygame.mixer.music.play(-1)  # Зацикливаем трек

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and not game_over:
                if arrows:
                    current_arrow = arrows.sprites()[0]
                    if event.key == key_bindings.get('UP') and current_arrow.get_type() == 'UP':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            FadingArrow(current_arrow.image.copy(), position)
                            # Создание частиц при успешном нажатии
                            create_particles(position)
                            current_arrow.delete()

                    elif event.key == key_bindings.get('DOWN') and current_arrow.get_type() == 'DOWN':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            FadingArrow(current_arrow.image.copy(), position)
                            create_particles(position)
                            current_arrow.delete()
                    elif event.key == key_bindings.get('LEFT') and current_arrow.get_type() == 'LEFT':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            FadingArrow(current_arrow.image.copy(), position)
                            create_particles(position)
                            current_arrow.delete()
                    elif event.key == key_bindings.get('RIGHT') and current_arrow.get_type() == 'RIGHT':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            FadingArrow(current_arrow.image.copy(), position)
                            create_particles(position)
                            current_arrow.delete()
        # Обновление стрелок и удаление их за пределами экрана
        arrows.update()

        for arrow in arrows:
            if arrow.rect.y > HEIGHT:
                score -= 1
                arrow.delete()
        dlt = datetime.datetime.now() - dt
        # Создание стрелок в ритме музыки
        current_time = pygame.time.get_ticks() / 1000.0
        if last_beat_index < len(beats) and current_time >= beats[last_beat_index] and dlt > DELTA:
            direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
            Arrow(direction)
            last_beat_index += 1
            dt = datetime.datetime.now()

        # Обновление fading arrows и particles
        fading_arrows_group.update()
        particles_group.update()

        # Отображение счета
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, (10, 10))

        # Проверка окончания игры
        if not arrows and not game_over:
            game_over = True

        if game_over:
            victory_text = font.render('Игра окончена!', True, (255, 0, 0))
            text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(victory_text, text_rect)
            main_menu()

        # Отрисовка всех спрайтов на экране
        all_sprites.draw(screen)
        fading_arrows_group.draw(screen)
        particles_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def load_gif(filename):
    image = Image.open(filename)
    frames = []
    try:
        while True:
            frame = image.copy()
            frame = frame.convert("RGBA")
            frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
            frames.append(frame)
            image.seek(len(frames))  # Переход к следующему кадру
    except EOFError:
        pass  # Достигнут конец GIF
    return frames


# Функция для отображения кадров GIF с изменением размера
def display_gif(frames, frame_index):
    scaled_frame = pygame.transform.scale(frames[frame_index], (WIDTH, HEIGHT))
    screen.blit(scaled_frame, (0, 0))


# Главное меню
def main_menu():
    gif_frames = load_gif(os.path.join('data', 'гоха.gif'))  # Замените 'гоха.gif' на путь к вашему GIF
    total_frames = len(gif_frames)
    frame_index = 0

    # Кнопка "Настройки управления"
    settings_button_text = font.render("Настройки управления", True, WHITE)
    settings_button_rect = settings_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    while True:
        screen.fill(WHITE)

        # Отображение текущего кадра GIF с изменением размера
        display_gif(gif_frames, frame_index)
        frame_index = (frame_index + 1) % total_frames  # Переход к следующему кадру

        # Отображение текста "Нажми чтобы начать"
        start_text = font.render("Нажми чтобы начать", True, WHITE)
        text_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(start_text, text_rect)

        # Отображение кнопки "Выход"
        screen.blit(exit_button_text, exit_button_rect)

        # Отображение кнопки "Настройки управления"
        screen.blit(settings_button_text, settings_button_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    mouse_pos = event.pos
                    if exit_button_rect.collidepoint(mouse_pos):
                        confirm_exit()  # Переход к экрану подтверждения выхода
                    elif settings_button_rect.collidepoint(mouse_pos):
                        change_key_bindings()  # Переход к экрану изменения раскладки
                    else:
                        game_loop()
                        # menu_songs()  # Запускаем игру
        try:
            pygame.display.flip()
        except pygame.error:
            pygame.quit()

        clock.tick(FPS)


# def menu_songs():
#     gif_frames = load_gif(os.path.join('data', 'гоха.gif'))  # Замените 'гоха.gif' на путь к вашему GIF
#     total_frames = len(gif_frames)
#     frame_index = 0
#
#     content = []
#     h = 20
#
#     # for i in music_tracks:
#     #     button_text = font.render(i, True, WHITE)
#     #     button_rect = button_text.get_rect(center=(WIDTH // 2, h))
#     #     content.append((button_text, button_rect))
#     #     h += 50
#
#     while True:
#         screen.fill(WHITE)
#
#         # Отображение текущего кадра GIF с изменением размера
#         display_gif(gif_frames, frame_index)
#         frame_index = (frame_index + 1) % total_frames  # Переход к следующему кадру
#         print(frame_index)
#
#         # for i in content:
#         #     screen.blit(i[0], i[1])
#
#         # for event in pygame.event.get():
#         #     if event.type == pygame.QUIT:
#         #         pygame.quit()
#         #         sys.exit()
#         #     if event.type == pygame.MOUSEBUTTONDOWN:
#         #         if event.button == 1:  # ЛКМ
#         #             mouse_pos = event.pos
#         #             for i in content:
#         #                 if i[1].collidepoint(mouse_pos):
#         #                     game_loop()  # Запускаем игру
#                 # elif event.type == pygame.KEYDOWN:
#                     # if event.key == ESCAPE:
#                     #     main_menu()


def change_key_binding(action, new_key):
    global key_bindings
    key_bindings[action] = new_key


def change_key_bindings():
    global key_bindings
    running = True
    selected_action = None  # Переменная для хранения выбранного действия
    gif_frames = load_gif(os.path.join('data', 'гоха.gif'))  # Замените 'гоха.gif' на путь к вашему GIF
    total_frames = len(gif_frames)
    frame_index = 0

    while running:
        screen.fill(WHITE)
        # Отображение текущего кадра GIF с изменением размера
        display_gif(gif_frames, frame_index)
        frame_index = (frame_index + 1) % total_frames  # Переход к следующему кадру

        # Отображение текущих назначений клавиш
        text_y = 100
        for action, key in key_bindings.items():
            key_name = pygame.key.name(key).upper()
            binding_text = font.render(f"{action}: {key_name}", True, WHITE)
            screen.blit(binding_text, (WIDTH // 2 - binding_text.get_width() // 2, text_y))
            text_y += 40

        instruction_text = font.render("Нажмите клавишу для переназначения", True, WHITE)
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, text_y + 20))

        if selected_action is not None:
            waiting_text = font.render(f"Нажмите новую клавишу для {selected_action}", True, (255, 0, 0))
            screen.blit(waiting_text, (WIDTH // 2 - waiting_text.get_width() // 2, text_y + 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if selected_action is None:
                    # Выбор действия для переназначения
                    for action in key_bindings.keys():
                        if pygame.key.get_pressed()[key_bindings[action]]:
                            selected_action = action
                            break
                else:
                    # Переназначаем выбранное действие
                    change_key_binding(selected_action, event.key)
                    print(f"Переназначено: {selected_action} на {pygame.key.name(event.key)}")
                    selected_action = None  # Сбросить выбор после переназначения

            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                running = False  # Выход из меню переназначения по нажатию ESC

        pygame.display.flip()
        clock.tick(FPS)


def confirm_exit():
    global yes_button_rect, yes_click_count
    yes_click_count = 0  # Сбрасываем счётчик при новом запросе на выход
    gif_frames = load_gif(os.path.join('data', 'гоха.gif'))  # Замените 'гоха.gif' на путь к вашему GIF
    total_frames = len(gif_frames)
    frame_index = 0

    # Перемещение кнопки "Да" в случайное место на экране
    yes_button_rect.x = random.randint(100, WIDTH - 200)
    yes_button_rect.y = random.randint(100, HEIGHT - 200)

    while True:
        screen.fill(WHITE)
        # Отображение текущего кадра GIF с изменением размера
        display_gif(gif_frames, frame_index)
        frame_index = (frame_index + 1) % total_frames  # Переход к следующему кадру

        # Отображение текста подтверждения выхода
        confirm_text = font.render("Вы точно хотите выйти?", True, WHITE)
        confirm_rect = confirm_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(confirm_text, confirm_rect)

        # Отображение кнопок "Да" и "Нет"
        screen.blit(yes_button_text, yes_button_rect)
        screen.blit(no_button_text, no_button_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if yes_button_rect.collidepoint(mouse_pos):
                    yes_click_count += 1
                    if yes_click_count >= 3:  # Проверяем, достиг ли счётчик трёх нажатий
                        pygame.quit()
                        sys.exit()
                    else:
                        # Перемещаем кнопку "Да" в новое случайное место
                        yes_button_rect.x = random.randint(100, WIDTH - 200)
                        yes_button_rect.y = random.randint(100, HEIGHT - 200)
                if no_button_rect.collidepoint(mouse_pos):
                    return  # Возвращаемся в главное меню

        pygame.display.flip()
        clock.tick(FPS)


# Главная программа
if __name__ == '__main__':
    all_sprites = pygame.sprite.Group()
    arrows = pygame.sprite.Group()
    fading_arrows_group = pygame.sprite.Group()
    particles_group = pygame.sprite.Group()
    ARR = pygame.sprite.Group()

    # Воспроизведение выбранного трека
    pygame.mixer.music.load(os.path.join('data', 'College_feat_Electric_Youth_-_A_Real_Hero_Drive.mp3'))
    pygame.mixer.music.play(-1)
    # Запуск главного меню
    main_menu()
