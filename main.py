import os
import random
import sqlite3
import sys

import librosa
import pygame
from PIL import Image

NAME = input('Введите никнейм: ')
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

DIFFICULTY_SETTINGS = {
    'EASY': {'ARROW_SPEED': 3, 'BEAT_INTERVAL': 700},
    'MEDIUM': {'ARROW_SPEED': 5, 'BEAT_INTERVAL': 500},
    'HARD': {'ARROW_SPEED': 7, 'BEAT_INTERVAL': 300},
}
current_difficulty = 'MEDIUM'

# Загрузка спрайтов стрелок
arrow_up_sprite = pygame.image.load(os.path.join('data/sprite', 'Вверх.png'))  # Убедитесь, что файл существует
arrow_down_sprite = pygame.image.load(os.path.join('data/sprite', 'Вниз.png'))
arrow_left_sprite = pygame.image.load(os.path.join('data/sprite', 'Влево.png'))
arrow_right_sprite = pygame.image.load(os.path.join('data/sprite', 'Вправо.png'))

# Измените размер спрайтов, если необходимо
arrow_up_sprite = pygame.transform.scale(arrow_up_sprite, (ARROW_SIZE, ARROW_SIZE))
arrow_down_sprite = pygame.transform.scale(arrow_down_sprite, (ARROW_SIZE, ARROW_SIZE))
arrow_left_sprite = pygame.transform.scale(arrow_left_sprite, (ARROW_SIZE, ARROW_SIZE))
arrow_right_sprite = pygame.transform.scale(arrow_right_sprite, (ARROW_SIZE, ARROW_SIZE))

# Музыка
music_tracks = [
    'Moondeity - Neon-blade.mp3',
    'INTERWORLD - METAMORPHOSIS.mp3',
    'Remzcore - Dynamite.mp3',
    'Вова Солодков - Барабулька.mp3',
    'Весокосный год - Там далеко-далеко...mp3',
]
hit_sound = pygame.mixer.Sound(os.path.join('data/music', 'попал.mp3'))
miss_sound = pygame.mixer.Sound(os.path.join('data/music', 'промах.mp3'))
menu_sound = pygame.mixer.Sound(os.path.join('data/music', 'Kavinsky_feat_Lovefox_-_Nightcall.mp3'))

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Нажми на стрелку в бит")
clock = pygame.time.Clock()
font_path = os.path.join('data', 'шрифт.ttf')
font_size = 36
font = pygame.font.Font(font_path, font_size)
font2 = pygame.font.Font(font_path, 25)

# Переменные для кнопки выхода
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
    fire = [pygame.image.load(os.path.join('data/sprite', 'star.png'))]
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


def llb(track_path):
    y, sr = librosa.load(os.path.join('data/music', track_path))
    tempo, beatss = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beatss, sr=sr)
    return beat_times


def initialize_database():
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()

    # Создание таблицы, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def add_score(username, score):
    with open('data/liderboard.txt', mode='a', encoding='utf-8') as file:
        file.write(f'{username} {score}' + '\n')


def get_leaderboard():
    sps = []
    with open('data/liderboard.txt', encoding='utf-8') as file:
        text = file.readlines()
        for i in text:
            a = i[:-1].split()
            sps.append((a[0], int(a[1])))
    return sorted(sps, key=lambda x: x[1] * -1)[:3]


def game_loop(song, bets):
    global ARROW_SPEED, BEAT_INTERVAL
    ARROW_SPEED = DIFFICULTY_SETTINGS[current_difficulty]['ARROW_SPEED']
    BEAT_INTERVAL = DIFFICULTY_SETTINGS[current_difficulty]['BEAT_INTERVAL']

    running = True
    score = 0
    gif_frames = load_gif(os.path.join('data/sprite', 'Ded-flex.gif.gif'))
    total_frames = len(gif_frames)
    frame_index = 0
    arrows.clear(screen, screen)

    # Create the table
    table_height = 80
    table = Table(0, HEIGHT - table_height, table_height)

    track_path = song
    beats = bets
    last_beat_index = 0

    # Play the selected track
    menu_sound.stop()
    pygame.mixer.music.load(os.path.join('data/music', track_path))
    pygame.mixer.music.play(-1)

    while running:
        screen.fill(WHITE)
        display_gif(gif_frames, int(frame_index))
        frame_index = (frame_index + 0.5) % total_frames

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    menu_sound.play(-1)
                    main_menu()
                if arrows:
                    if event.key == key_bindings.get('UP'):
                        for curar in arrows.sprites():
                            if curar.get_type() == 'UP':
                                if pygame.sprite.collide_mask(curar, table):
                                    score += 1
                                    hit_sound.play()
                                    position = curar.get_cor()
                                    FadingArrow(curar.image.copy(), position)
                                    create_particles(position)
                                    curar.delete()
                                    break
                                elif not pygame.sprite.collide_mask(curar, table):
                                    score -= 0.5
                                    miss_sound.play()
                    elif event.key == key_bindings.get('DOWN'):
                        for curar in arrows.sprites():
                            if curar.get_type() == 'DOWN':
                                if pygame.sprite.collide_mask(curar, table):
                                    score += 1
                                    hit_sound.play()
                                    position = curar.get_cor()
                                    FadingArrow(curar.image.copy(), position)
                                    create_particles(position)
                                    curar.delete()
                                    break
                                elif not pygame.sprite.collide_mask(curar, table):
                                    score -= 0.5
                                    miss_sound.play()
                    elif event.key == key_bindings.get('LEFT'):
                        for curar in arrows.sprites():
                            if curar.get_type() == 'LEFT':
                                if pygame.sprite.collide_mask(curar, table):
                                    score += 1
                                    hit_sound.play()
                                    position = curar.get_cor()
                                    FadingArrow(curar.image.copy(), position)
                                    create_particles(position)
                                    curar.delete()
                                    break
                                elif not pygame.sprite.collide_mask(curar, table):
                                    score -= 0.5
                                    miss_sound.play()
                    elif event.key == key_bindings.get('RIGHT'):
                        for curar in arrows.sprites():
                            if curar.get_type() == 'RIGHT':
                                if pygame.sprite.collide_mask(curar, table):
                                    score += 1
                                    hit_sound.play()
                                    position = curar.get_cor()
                                    FadingArrow(curar.image.copy(), position)
                                    create_particles(position)
                                    curar.delete()
                                    break
                                elif not pygame.sprite.collide_mask(curar, table):
                                    score -= 0.5
                                    miss_sound.play()

        # Обновление стрелок и удаление их за пределами экрана
        arrows.update()

        for arrow in arrows:
            if arrow.rect.y > HEIGHT:
                score -= 1
                miss_sound.play()
                arrow.delete()
        # Создание стрелок в ритме музыки
        current_time = pygame.time.get_ticks() / 1000.0
        try:
            if beats[last_beat_index] - current_time < -0.05:
                last_beat_index += 1
            elif -0.5 <= beats[last_beat_index] - current_time <= 0.05:
                direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                Arrow(direction)
                last_beat_index += 1
        except IndexError:  # Проверка окончания игры
            pygame.mixer.music.stop()
            menu_sound.play(-1)
            add_score(NAME, score)
            victory_text = font.render('Игра окончена!', True, (255, 0, 0))
            text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(victory_text, text_rect)

        # Обновление fading arrows и particles
        fading_arrows_group.update()
        particles_group.update()

        # Отображение счета
        fontt = pygame.font.Font(None, 36)
        score_text = fontt.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        # Отрисовка всех спрайтов на экране
        all_sprites.draw(screen)
        fading_arrows_group.draw(screen)
        particles_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def load_scene(song):
    k = 1
    surf = pygame.Surface((WIDTH, WIDTH))
    surf.fill(BLACK)
    victory_text = font.render('loading...', True, (255, 0, 0))
    text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surf.set_alpha(k)
    while k != 255:
        surf.set_alpha(k)
        screen.blit(surf, (0, 0))
        screen.blit(victory_text, text_rect)
        k += 1
        pygame.display.flip()
        clock.tick(FPS)

    beats = llb(song)
    game_loop(song, beats)


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
    try:
        screen.blit(scaled_frame, (0, 0))
    except:
        pass


# Главное меню
def main_menu():
    gif_frames = load_gif(os.path.join('data/sprite', 'гоха.gif'))
    total_frames = len(gif_frames)
    frame_index = 0
    liders = get_leaderboard()

    settings_button_text = font.render("Настройки управления", True, WHITE)
    settings_button_rect = settings_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    difficulty_button_text = font.render(f"Выбор сложности: {current_difficulty}", True, WHITE)
    difficulty_button_rect = difficulty_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    exit_button_text = font.render("Выход", True, WHITE)
    exit_button_rect = exit_button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))

    liderboard_text = font2.render(f"Лидеры:  {liders[0][0]} - {liders[0][1]}  "
                                   f"{liders[1][0]} - {liders[1][1]}  "
                                   f"{liders[2][0]} - {liders[2][1]}  ", True, WHITE)
    liderboard_rect = difficulty_button_text.get_rect(topleft=(0, 0))

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
        screen.blit(difficulty_button_text, difficulty_button_rect)
        screen.blit(liderboard_text, liderboard_rect)

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
                    elif difficulty_button_rect.collidepoint(mouse_pos):
                        select_difficulty()
                    else:
                        try:
                            menu_songs()  # Запускаем игру
                        except pygame.error:
                            pygame.quit()
        try:
            pygame.display.flip()
        except pygame.error:
            pygame.quit()

        clock.tick(FPS)


def menu_songs():
    gif_frames = load_gif(os.path.join('data/sprite', 'гоха.gif'))  # Замените 'гоха.gif' на путь к вашему GIF
    total_frames = len(gif_frames)
    frame_index = 0

    content = []
    h = 40

    for song in music_tracks:
        button_text = font.render(f'* {song[:-4]}', True, WHITE)
        button_rect = button_text.get_rect(topleft=(15, h))
        content.append((button_text, button_rect, song))  # Список с text и rect кнопок
        h += 70

    while True:
        screen.fill(WHITE)
        display_gif(gif_frames, frame_index)
        frame_index = (frame_index + 1) % total_frames  # Переход к следующему кадру

        for i in content:
            screen.blit(i[0], i[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    mouse_pos = event.pos
                    for but in content:
                        if but[1].collidepoint(mouse_pos):
                            load_scene(but[2])
                            # game_loop(but[2])  # Запускаем игру
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()

        pygame.display.flip()
        clock.tick(FPS)


def change_key_binding(action, new_key):
    global key_bindings
    key_bindings[action] = new_key


def change_key_bindings():
    global key_bindings
    running = True
    selected_action = None  # Переменная для хранения выбранного действия
    gif_frames = load_gif(os.path.join('data/sprite', 'гоха.gif'))  # Замените 'гоха.gif' на путь к вашему GIF
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


def select_difficulty():
    global current_difficulty
    difficulties = list(DIFFICULTY_SETTINGS.keys())
    gif_frames = load_gif(os.path.join('data/sprite', 'гоха.gif'))
    total_frames = len(gif_frames)
    frame_index = 0

    button = []
    y_position = HEIGHT // 2 - 50
    for difficulty in difficulties:
        difficulty_text = font.render(difficulty, True, WHITE)
        difficulty_rect = difficulty_text.get_rect(center=(WIDTH // 2, y_position))
        screen.blit(difficulty_text, difficulty_rect)
        button.append((difficulty_text, difficulty_rect, difficulty))
        y_position += 50

    while True:
        screen.fill(WHITE)
        display_gif(gif_frames, frame_index)
        frame_index = (frame_index + 1) % total_frames

        for but in button:
            screen.blit(but[0], but[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = event.pos
                    for i in button:
                        if i[1].collidepoint(mouse_pos):
                            current_difficulty = i[2]
                            main_menu()

        pygame.display.flip()
        clock.tick(FPS)


def confirm_exit():
    yes_click_count = 0  # Сбрасываем счётчик при новом запросе на выход
    gif_frames = load_gif(os.path.join('data/sprite', 'гоха.gif'))  # Замените 'гоха.gif' на путь к вашему GIF
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
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
    menu_sound.play(-1)
    # Запуск главного меню
    main_menu()
