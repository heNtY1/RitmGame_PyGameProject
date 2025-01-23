import pygame
import random
import sys
import os
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

# Стрелки
arrows = []
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
    'Vova_Solodkov_-_Barabulka_78505531.mp3'
]


def play_random_music():
    track = random.choice(music_tracks)  # Выбираем случайный трек
    pygame.mixer.music.load(os.path.join('data', track))  # Загружаем трек
    pygame.mixer.music.play(-1)  # Воспроизводим в бесконечном цикле


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
    def __init__(self, type, x_pos, y_pos):
        super().__init__(all_sprites, ARR)
        if type == 'UP':
            self.image = arrow_up_sprite
        elif type == 'DOWN':
            self.image = arrow_down_sprite
        elif type == 'LEFT':
            self.image = arrow_left_sprite
        elif type == 'RIGHT':
            self.image = arrow_right_sprite
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.type = type
        self.rect.x = x_pos
        self.rect.y = y_pos

    def get_y(self, n=0):
        self.rect.y += n
        return self.rect.y

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
        super().__init__()
        self.image = arrow_image
        self.rect = self.image.get_rect(center=position)
        self.alpha = 255  # Полная непрозрачность

    def update(self):
        # Перемещение стрелки вверх
        self.rect.y -= 5  # Скорость движения вверх
        self.alpha -= 25
        if self.alpha < 0:
            self.alpha = 0

        self.image.set_alpha(self.alpha)

        # Удаляем спрайт, если он стал полностью прозрачным
        if self.alpha == 0:
            self.kill()


class Particle(pygame.sprite.Sprite):
    fire = [pygame.image.load(os.path.join('data', 'star.png'))]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__()
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


# Функция для создания новой стрелки
def create_arrow():
    arrow_type = random.choice(arrow_types)
    x_pos = random.randint(0, WIDTH - ARROW_SIZE)
    arrow = Arrow(arrow_type, x_pos, -ARROW_SIZE)
    return arrow



def game_loop():
    score = 0
    running = True
    game_over = False
    rect_y_start, rect_y_hight = 500, 100
    table = Table(0, 500, rect_y_hight)
    arrows.append(create_arrow())

    global last_beat_time

    fading_arrows_group = pygame.sprite.Group()
    particles_group = pygame.sprite.Group()  # Группа для партиклов

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and not game_over:
                if arrows:
                    current_arrow = arrows[0]
                    if event.key == key_bindings.get('UP') and current_arrow.get_type() == 'UP':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            fading_arrow = FadingArrow(current_arrow.image.copy(), position)
                            fading_arrows_group.add(fading_arrow)

                            for _ in range(10):
                                dx = random.uniform(-2, 2)
                                dy = random.uniform(-5, -2)
                                particle = Particle(position, dx, dy)
                                particles_group.add(particle)

                            current_arrow.delete()
                            arrows.pop(0)
                    elif event.key == key_bindings.get('DOWN') and current_arrow.get_type() == 'DOWN':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            fading_arrow = FadingArrow(current_arrow.image.copy(), position)
                            fading_arrows_group.add(fading_arrow)

                            for _ in range(10):
                                dx = random.uniform(-2, 2)
                                dy = random.uniform(-5, -2)
                                particle = Particle(position, dx, dy)
                                particles_group.add(particle)

                            current_arrow.delete()
                            arrows.pop(0)
                    elif event.key == key_bindings.get('LEFT') and current_arrow.get_type() == 'LEFT':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            fading_arrow = FadingArrow(current_arrow.image.copy(), position)
                            fading_arrows_group.add(fading_arrow)

                            for _ in range(10):
                                dx = random.uniform(-2, 2)
                                dy = random.uniform(-5, -2)
                                particle = Particle(position, dx, dy)
                                particles_group.add(particle)

                            current_arrow.delete()
                            arrows.pop(0)
                    elif event.key == key_bindings.get('RIGHT') and current_arrow.get_type() == 'RIGHT':
                        if pygame.sprite.collide_mask(current_arrow, table):
                            score += 1
                            position = current_arrow.get_cor()
                            fading_arrow = FadingArrow(current_arrow.image.copy(), position)
                            fading_arrows_group.add(fading_arrow)


                            for _ in range(10):
                                dx = random.uniform(-2, 2)
                                dy = random.uniform(-5, -2)
                                particle = Particle(position, dx, dy)
                                particles_group.add(particle)

                            current_arrow.delete()
                            arrows.pop(0)
                    else:
                        score -= 0.5

        for i in list(arrows):
            i.get_y(ARROW_SPEED)
            if i.get_y() > HEIGHT:
                score -= 1
                arrows.remove(i)

        fading_arrows_group.update()
        particles_group.update()  # Обновление партиклов

        score_text = font.render(f'Score: {score}', True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        current_time = pygame.time.get_ticks()
        if current_time - last_beat_time >= BEAT_INTERVAL:
            arrows.append(create_arrow())
            last_beat_time = current_time

        if not arrows and not game_over:
            game_over = True

        if game_over:
            victory_text = font.render('Вы победили!', True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(victory_text, text_rect)

        all_sprites.update()
        all_sprites.draw(screen)

        fading_arrows_group.draw(screen)
        particles_group.draw(screen)  # Отрисовка партиклов

        pygame.display.flip()
        clock.tick(FPS)

    print(f"Game Over! Your score: {score}")
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
                        play_random_music()  # Запускаем случайную музыку
                        game_loop()  # Запускаем игру
        try:
            pygame.display.flip()
        except pygame.error:
            print('')
            pygame.quit()

        clock.tick(FPS)


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
    ARR = pygame.sprite.Group()
    main_menu()  # Запускаем главное меню
