import pygame
import random
import math
import sys
import time
import os

# Инициализация PyGame и микшера
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
GRID_WIDTH = 10
GRID_HEIGHT = 22
CELL_SIZE = 30
SIDEBAR_WIDTH = 250
FPS = 60

# Позиция игрового поля по центру
BOARD_OFFSET_X = (SCREEN_WIDTH - SIDEBAR_WIDTH - GRID_WIDTH * CELL_SIZE) // 2 + SIDEBAR_WIDTH
BOARD_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 50, 230)

# Локации (фоны)
LOCATIONS = [
    {
        "name": "Космос",
        "bg_color": (5, 5, 25),
        "grid_color": (30, 30, 60, 150),
        "particle_color": (100, 150, 255),
        "effect_color": (0, 200, 255),
        "music_file": "jingle_bells.mp3"  # Ожидается файл в папке с игрой
    },
    {
        "name": "Пустыня",
        "bg_color": (240, 220, 150),
        "grid_color": (220, 190, 130, 150),
        "particle_color": (255, 200, 50),
        "effect_color": (255, 150, 0),
        "music_file": "mechanoids_desert.mp3"  # Ожидается файл в папке с игрой
    },
    {
        "name": "Лес",
        "bg_color": (10, 40, 20),
        "grid_color": (30, 70, 40, 150),
        "particle_color": (50, 200, 100),
        "effect_color": (100, 255, 150),
        "music_file": "factorio_forest.mp3"  # Ожидается файл в папке с игрой
    },
    {
        "name": "Вулкан",
        "bg_color": (70, 10, 5),
        "grid_color": (90, 30, 10, 150),
        "particle_color": (255, 100, 50),
        "effect_color": (255, 80, 0),
        "music_file": "lava_red.mp3"
    }
]

# Фигуры Тетриса
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Цвета фигур
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]

# Уровни сложности
LEVELS = [
    {"name": "Легкий", "fall_speed": 0.8, "score_multiplier": 1},
    {"name": "Средний", "fall_speed": 0.5, "score_multiplier": 1.5},
    {"name": "Сложный", "fall_speed": 0.15, "score_multiplier": 2},
    {"name": "Эксперт", "fall_speed": 0.1, "score_multiplier": 3}
]

class SoundManager:
    """Менеджер звуковых эффектов и музыки"""
    def __init__(self):
        self.sounds = {}
        self.current_music = None
        self.music_playing = False
        self.create_sounds()
        
    def create_sounds(self):
        """Создание звуковых эффектов программно"""
        try:
            # Звук вращения
            self.sounds['rotate'] = self.create_beep_sound(523.25, 0.1, 0.3)
            
            # Звук движения
            self.sounds['move'] = self.create_beep_sound(392, 0.05, 0.2)
            
            # Звук приземления
            self.sounds['land'] = self.create_land_sound()
            
            # Звук очистки линии
            self.sounds['clear'] = self.create_clear_sound()
            
            # Звук тетриса (4 линии)
            self.sounds['tetris'] = self.create_tetris_sound()
            
            # Звук окончания игры
            self.sounds['game_over'] = self.create_game_over_sound()
            
            # Звук смены локации
            self.sounds['change_location'] = self.create_location_change_sound()
            
            # Звук повышения уровня
            self.sounds['level_up'] = self.create_level_up_sound()
            
        except Exception as e:
            print(f"Ошибка создания звуков: {e}")
            self.sounds = {key: None for key in ['rotate', 'move', 'land', 'clear', 'tetris', 'game_over', 'change_location', 'level_up']}
    
    def create_beep_sound(self, frequency, duration, volume=0.3):
        """Создание простого звукового сигнала"""
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray(n_samples * 2)
        amplitude = 32767
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            wave = int(amplitude * math.sin(2 * math.pi * frequency * t))
            
            if i > n_samples * 0.8:
                wave = int(wave * (1 - (i - n_samples * 0.8) / (n_samples * 0.2)))
            
            buf[2*i] = wave & 0xff
            buf[2*i+1] = (wave >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(volume)
        return sound
    
    def create_land_sound(self):
        """Создание звука приземления"""
        sample_rate = 22050
        duration = 0.3
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray(n_samples * 2)
        amplitude = 32767
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            frequency = 150 * (1 - t/duration) + 80
            wave = int(amplitude * math.sin(2 * math.pi * frequency * t))
            wave = int(wave * (1 - (i/n_samples)**2))
            
            buf[2*i] = wave & 0xff
            buf[2*i+1] = (wave >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.4)
        return sound
    
    def create_clear_sound(self):
        """Создание звука очистки линии"""
        sample_rate = 22050
        duration = 0.4
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray(n_samples * 2)
        amplitude = 32767
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            frequency1 = 200 + 400 * (t/duration)
            frequency2 = 300 + 500 * (t/duration)
            wave = int(amplitude * (
                0.6 * math.sin(2 * math.pi * frequency1 * t) +
                0.4 * math.sin(2 * math.pi * frequency2 * t)
            ))
            wave = int(wave * (1 - 0.3 * (i/n_samples)))
            
            buf[2*i] = wave & 0xff
            buf[2*i+1] = (wave >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.5)
        return sound
    
    def create_tetris_sound(self):
        """Создание звука тетриса"""
        sample_rate = 22050
        duration = 0.6
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray(n_samples * 2)
        amplitude = 32767
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            freq1 = 523.25 * (1 + 0.3 * (t/duration))
            freq2 = 659.25 * (1 + 0.3 * (t/duration))
            freq3 = 783.99 * (1 + 0.3 * (t/duration))
            
            wave = int(amplitude * (
                0.4 * math.sin(2 * math.pi * freq1 * t) +
                0.35 * math.sin(2 * math.pi * freq2 * t) +
                0.25 * math.sin(2 * math.pi * freq3 * t)
            ))
            wave = int(wave * (1 - 0.5 * (i/n_samples)))
            
            buf[2*i] = wave & 0xff
            buf[2*i+1] = (wave >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.6)
        return sound
    
    def create_game_over_sound(self):
        """Создание звука окончания игры"""
        sample_rate = 22050
        duration = 1.5
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray(n_samples * 2)
        amplitude = 32767
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            frequency = 400 * math.exp(-2 * t) + 100
            vibrato = 0.05 * math.sin(2 * math.pi * 8 * t)
            wave = int(amplitude * math.sin(2 * math.pi * frequency * t * (1 + vibrato)))
            wave = int(wave * math.exp(-2 * t))
            
            buf[2*i] = wave & 0xff
            buf[2*i+1] = (wave >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.5)
        return sound
    
    def create_location_change_sound(self):
        """Создание звука смены локации"""
        sample_rate = 22050
        duration = 0.8
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray(n_samples * 2)
        amplitude = 32767
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            base_freq = 300
            sweep = 200 * math.sin(2 * math.pi * 2 * t)
            frequency = base_freq + sweep
            
            wave = int(amplitude * (
                0.5 * math.sin(2 * math.pi * frequency * t) +
                0.3 * math.sin(2 * math.pi * frequency * 2 * t) +
                0.2 * math.sin(2 * math.pi * frequency * 3 * t)
            ))
            envelope = math.exp(-((t - duration/2) ** 2) * 20)
            wave = int(wave * envelope)
            
            buf[2*i] = wave & 0xff
            buf[2*i+1] = (wave >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.4)
        return sound
    
    def create_level_up_sound(self):
        """Создание звука повышения уровня"""
        sample_rate = 22050
        duration = 0.5
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray(n_samples * 2)
        amplitude = 32767
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            notes = [523.25, 659.25, 783.99, 1046.50]
            note_index = int(t / duration * len(notes))
            if note_index >= len(notes):
                note_index = len(notes) - 1
            
            frequency = notes[note_index]
            wave = int(amplitude * math.sin(2 * math.pi * frequency * t))
            wave = int(wave * (1 - 0.7 * (t/duration)))
            
            buf[2*i] = wave & 0xff
            buf[2*i+1] = (wave >> 8) & 0xff
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.5)
        return sound
    
    def create_tetris_classic_music(self):
        """Создание классической музыки Тетриса программно"""
        melody = [
            (659, 0.15), (494, 0.15), (523, 0.15), (587, 0.15),
            (523, 0.15), (494, 0.15), (440, 0.15), (440, 0.15),
            (523, 0.15), (659, 0.15), (587, 0.15), (523, 0.15),
            (494, 0.15), (523, 0.15), (587, 0.15), (659, 0.15),
            (523, 0.15), (440, 0.15), (440, 0.15), (440, 0.15),
            (0, 0.15), (587, 0.15), (698, 0.15), (880, 0.15),
            (784, 0.15), (698, 0.15), (659, 0.15), (523, 0.15),
            (659, 0.15), (587, 0.15), (523, 0.15), (494, 0.15),
            (523, 0.15), (587, 0.15), (659, 0.15), (523, 0.15),
            (440, 0.15), (440, 0.15), (440, 0.15), (0, 0.15)
        ]
        
        return self.create_melody_sound(melody)
    
    def create_melody_sound(self, melody):
        """Создание звука из мелодии"""
        sample_rate = 22050
        total_samples = 0
        
        for _, duration in melody:
            total_samples += int(round(duration * sample_rate))
        
        buf = bytearray(total_samples * 2)
        pos = 0
        
        for frequency, duration in melody:
            n_samples = int(round(duration * sample_rate))
            amplitude = 10000
            
            for i in range(n_samples):
                t = float(i) / sample_rate
                if frequency > 0:
                    wave = int(amplitude * math.sin(2 * math.pi * frequency * t))
                else:
                    wave = 0
                
                if i < n_samples * 0.1:
                    wave = int(wave * (i / (n_samples * 0.1)))
                elif i > n_samples * 0.9:
                    wave = int(wave * (1 - (i - n_samples * 0.9) / (n_samples * 0.1)))
                
                buf[pos] = wave & 0xff
                buf[pos+1] = (wave >> 8) & 0xff
                pos += 2
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.15)
        return sound
    
    def play_music(self, location_index):
        """Воспроизведение фоновой музыки для локации"""
        if self.current_music:
            self.current_music.stop()
        
        location = LOCATIONS[location_index]
        music_file = location["music_file"]
        
        try:
            if music_file and os.path.exists(music_file):
                # Загружаем музыку из файла
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.3)  # Устанавливаем громкость
                pygame.mixer.music.play(-1)  # Зацикливаем
                self.music_playing = True
                print(f"Играет музыка из файла: {music_file}")
            else:
                # Для локации "Лава" или если файл не найден - программная музыка
                if location_index == 3:  # Лава
                    self.current_music = self.create_tetris_classic_music()
                    self.current_music.play(-1)
                    self.music_playing = True
                    print("Играет программная музыка Тетриса")
                else:
                    print(f"Файл музыки не найден: {music_file}")
                    # Создаем тихую фоновую музыку программно
                    self.current_music = self.create_tetris_classic_music()
                    self.current_music.play(-1)
                    self.music_playing = True
                    
        except Exception as e:
            print(f"Ошибка загрузки музыки: {e}")
            # В случае ошибки используем программную музыку
            self.current_music = self.create_tetris_classic_music()
            self.current_music.play(-1)
            self.music_playing = True
    
    def stop_music(self):
        """Остановка музыки"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        if self.current_music:
            self.current_music.stop()
        self.music_playing = False
    
    def pause_music(self):
        """Пауза музыки"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        self.music_playing = False
    
    def unpause_music(self):
        """Снятие с паузы музыки"""
        if not pygame.mixer.music.get_busy() and self.music_playing:
            pygame.mixer.music.unpause()
        self.music_playing = True
    
    def play(self, sound_name):
        """Воспроизведение звука по имени"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

class Particle:
    """Класс для частиц эффектов"""
    def __init__(self, x, y, color, location_effect_color):
        self.x = x
        self.y = y
        self.color = color
        self.effect_color = location_effect_color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-4, -1)
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.04)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.15
        self.life -= self.decay
        return self.life > 0
    
    def draw(self, surface):
        alpha = int(self.life * 255)
        current_color = self.color if random.random() > 0.3 else self.effect_color
        color_with_alpha = (*current_color[:3], alpha)
        rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(s, color_with_alpha, (0, 0, self.size, self.size), border_radius=self.size//2)
        surface.blit(s, rect)

class Tetris:
    """Основной класс игры Тетрис"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Тетрис - Классика с эффектами")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("arial", 24)
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        
        self.sound_manager = SoundManager()
        
        # Выбор локации и сложности
        self.location_index = 0
        self.difficulty_index = 0
        
        # Таймеры для управления
        self.move_delay = 0.12
        self.last_move_time = 0
        self.rotate_delay = 0.25
        self.last_rotate_time = 0
        self.soft_drop_delay = 0.06
        self.last_soft_drop_time = 0
        self.base_lines_per_level = 8  
        self.level_speed_increase = 0.1
        self.speed_multiplier = 1.0 
        self.reset_game()
        
        # Эффекты
        self.particles = []
        self.line_clear_effects = []
        self.level_effects = []
        
        # Фон
        self.background_stars = self.create_stars()
        
        # Меню
        self.show_menu = True
        self.menu_selection = 0
        self.menu_options = ["Новая игра", "Продолжить", "Сложность", "Выход"]
        
    def create_stars(self):
        """Создание фоновых звезд"""
        stars = []
        for _ in range(150):
            stars.append((
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.uniform(0.5, 3),
                random.uniform(0.1, 0.5)
            ))
        return stars
    
    def reset_game(self):
        """Сброс игры"""
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.board_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.current_shape = self.get_random_shape()
        self.current_color = SHAPE_COLORS[SHAPES.index(self.current_shape)]
        self.current_x = GRID_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0
        self.next_shape = self.get_random_shape()
        self.fall_speed = LEVELS[self.difficulty_index]["fall_speed"]
        self.particles = []
        self.line_clear_effects = []
        self.level_effects = []
        self.fall_time = 0
        
        if hasattr(self, 'high_score'):
            self.high_score = max(self.high_score, self.score)
        else:
            self.high_score = 0
            
        # Сброс таймеров управления
        current_time = time.time()
        self.last_move_time = current_time
        self.last_rotate_time = current_time
        self.last_soft_drop_time = current_time
        
        # Запуск музыки для текущей локации
        self.sound_manager.play_music(self.location_index)
    
    def get_random_shape(self):
        """Получение случайной фигуры"""
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return SHAPES[shape_idx]
    
    def rotate_shape(self, shape, clockwise=True):
        """Вращение фигуры"""
        if clockwise:
            return [list(row)[::-1] for row in zip(*shape)]
        else:
            return [list(row) for row in zip(*shape[::-1])]
    
    def check_collision(self, shape, x, y):
        """Проверка столкновений"""
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    
                    if (board_x < 0 or board_x >= GRID_WIDTH or 
                        board_y >= GRID_HEIGHT or 
                        (board_y >= 0 and self.board[board_y][board_x])):
                        return True
        return False
    
    def merge_shape(self):
        """Объединение фигуры с игровым полем"""
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_y = self.current_y + row_idx
                    board_x = self.current_x + col_idx
                    if board_y >= 0:
                        self.board[board_y][board_x] = 1
                        self.board_colors[board_y][board_x] = self.current_color
        
        # Эффект приземления и звук
        self.create_landing_effect()
        self.sound_manager.play('land')
        
        # Проверка заполненных линий
        self.check_lines()
        
        # Новая фигура
        self.current_shape = self.next_shape
        self.current_color = SHAPE_COLORS[SHAPES.index(self.current_shape)]
        self.current_x = GRID_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0
        self.next_shape = self.get_random_shape()
        
        # Проверка завершения игры
        if self.check_collision(self.current_shape, self.current_x, self.current_y):
            self.game_over = True
            self.sound_manager.stop_music()
            self.sound_manager.play('game_over')

    def get_lines_needed(self, target_level):
        """Сколько линий нужно для достижения target_level"""
        return self.base_lines_per_level * (target_level - 1)
    
    def check_lines(self):
        """Проверка и очистка заполненных линий"""
        lines_to_clear = []
        for row_idx in range(GRID_HEIGHT):
            if all(self.board[row_idx]):
                lines_to_clear.append(row_idx)
        
        if lines_to_clear:
            # Эффект очистки линии
            self.create_line_clear_effect(lines_to_clear)
            
            # Воспроизведение звука
            if len(lines_to_clear) == 4:
                self.sound_manager.play('tetris')
            else:
                self.sound_manager.play('clear')
            
            # Обновление счета
            self.update_score(len(lines_to_clear))
            
            # Удаление линий
            for row_idx in lines_to_clear:
                for y in range(row_idx, 0, -1):
                    self.board[y] = self.board[y-1][:]
                    self.board_colors[y] = self.board_colors[y-1][:]
                self.board[0] = [0 for _ in range(GRID_WIDTH)]
                self.board_colors[0] = [BLACK for _ in range(GRID_WIDTH)]
            
            # Обновление уровня
            self.lines_cleared += len(lines_to_clear)
            
            # Рассчитываем новый уровень на основе набранных линий
            new_level = 1
            while self.lines_cleared >= self.get_lines_needed(new_level + 1):
                new_level += 1
            
            if new_level > self.level:
                self.level = new_level
                self.sound_manager.play('level_up')
                self.create_level_up_effect()
                # Пересчитываем скорость с учетом уровня и сложности
                self.fall_speed = (
                    LEVELS[self.difficulty_index]["fall_speed"] * 
                    (1 + (self.level - 1) * self.level_speed_increase) * 
                    self.speed_multiplier
                )
    
    def update_score(self, lines_cleared):
        """Обновление счета"""
        line_points = {1: 100, 2: 300, 3: 500, 4: 800}
        base_points = line_points.get(lines_cleared, 0)
        level_multiplier = 1 + (self.level - 1) * 0.5
        difficulty_multiplier = LEVELS[self.difficulty_index]["score_multiplier"]
        
        self.score += int(base_points * level_multiplier * difficulty_multiplier)
        self.high_score = max(self.high_score, self.score)
    
    def create_landing_effect(self):
        """Создание эффекта приземления"""
        location = LOCATIONS[self.location_index]
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = self.current_x + col_idx
                    y = self.current_y + row_idx
                    screen_x = BOARD_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2
                    screen_y = BOARD_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2
                    
                    for _ in range(25):
                        self.particles.append(Particle(
                            screen_x, screen_y,
                            location["particle_color"],
                            location["effect_color"]
                        ))
    
    def create_line_clear_effect(self, lines):
        """Создание эффекта очистки линии"""
        location = LOCATIONS[self.location_index]
        for row_idx in lines:
            for x in range(GRID_WIDTH):
                screen_x = BOARD_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2
                screen_y = BOARD_OFFSET_Y + row_idx * CELL_SIZE + CELL_SIZE // 2
                
                for _ in range(20):
                    self.particles.append(Particle(
                        screen_x, screen_y,
                        location["effect_color"],
                        location["particle_color"]
                    ))
    
    def create_level_up_effect(self):
        """Создание эффекта повышения уровня"""
        location = LOCATIONS[self.location_index]
        for _ in range(150):
            x = random.randint(BOARD_OFFSET_X, BOARD_OFFSET_X + GRID_WIDTH * CELL_SIZE)
            y = random.randint(BOARD_OFFSET_Y, BOARD_OFFSET_Y + GRID_HEIGHT * CELL_SIZE)
            self.level_effects.append({
                'x': x,
                'y': y,
                'size': random.randint(8, 20),
                'color': location["effect_color"],
                'life': 1.0,
                'decay': random.uniform(0.008, 0.015)
            })
    
    def draw_board(self):
        """Отрисовка игрового поля"""
        # Фон игрового поля
        board_rect = pygame.Rect(
            BOARD_OFFSET_X - 2, 
            BOARD_OFFSET_Y - 2, 
            GRID_WIDTH * CELL_SIZE + 4, 
            GRID_HEIGHT * CELL_SIZE + 4
        )
        pygame.draw.rect(self.screen, WHITE, board_rect, 2)
        
        # Внутренний фон поля
        inner_rect = pygame.Rect(
            BOARD_OFFSET_X, 
            BOARD_OFFSET_Y, 
            GRID_WIDTH * CELL_SIZE, 
            GRID_HEIGHT * CELL_SIZE
        )
        pygame.draw.rect(self.screen, (20, 20, 30), inner_rect)
        
        # Сетка
        location = LOCATIONS[self.location_index]
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, location["grid_color"],
                           (BOARD_OFFSET_X, BOARD_OFFSET_Y + y * CELL_SIZE),
                           (BOARD_OFFSET_X + GRID_WIDTH * CELL_SIZE, BOARD_OFFSET_Y + y * CELL_SIZE),
                           1)
        
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, location["grid_color"],
                           (BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y),
                           (BOARD_OFFSET_X + x * CELL_SIZE, BOARD_OFFSET_Y + GRID_HEIGHT * CELL_SIZE),
                           1)
        
        # Закрепленные блоки
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    color = self.board_colors[y][x]
                    rect = pygame.Rect(
                        BOARD_OFFSET_X + x * CELL_SIZE + 2,
                        BOARD_OFFSET_Y + y * CELL_SIZE + 2,
                        CELL_SIZE - 4,
                        CELL_SIZE - 4
                    )
                    
                    pygame.draw.rect(self.screen, color, rect)
                    
                    pygame.draw.line(self.screen, 
                                   (min(color[0]+60, 255), min(color[1]+60, 255), min(color[2]+60, 255)),
                                   rect.topleft, rect.topright, 2)
                    pygame.draw.line(self.screen, 
                                   (min(color[0]+60, 255), min(color[1]+60, 255), min(color[2]+60, 255)),
                                   rect.topleft, rect.bottomleft, 2)
                    
                    pygame.draw.line(self.screen, 
                                   (max(color[0]-60, 0), max(color[1]-60, 0), max(color[2]-60, 0)),
                                   rect.bottomleft, rect.bottomright, 2)
                    pygame.draw.line(self.screen, 
                                   (max(color[0]-60, 0), max(color[1]-60, 0), max(color[2]-60, 0)),
                                   rect.topright, rect.bottomright, 2)
        
        # Текущая фигура
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = self.current_x + col_idx
                    y = self.current_y + row_idx
                    
                    if y >= 0:
                        rect = pygame.Rect(
                            BOARD_OFFSET_X + x * CELL_SIZE + 2,
                            BOARD_OFFSET_Y + y * CELL_SIZE + 2,
                            CELL_SIZE - 4,
                            CELL_SIZE - 4
                        )
                        
                        s = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)
                        color = (*self.current_color, 180)
                        pygame.draw.rect(s, color, (0, 0, CELL_SIZE - 4, CELL_SIZE - 4))
                        self.screen.blit(s, rect)
                        pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        # Предварительный просмотр места падения
        shadow_y = self.current_y
        while not self.check_collision(self.current_shape, self.current_x, shadow_y + 1):
            shadow_y += 1
        
        if shadow_y > self.current_y:
            for row_idx, row in enumerate(self.current_shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = self.current_x + col_idx
                        y = shadow_y + row_idx
                        
                        if y >= 0:
                            rect = pygame.Rect(
                                BOARD_OFFSET_X + x * CELL_SIZE + 2,
                                BOARD_OFFSET_Y + y * CELL_SIZE + 2,
                                CELL_SIZE - 4,
                                CELL_SIZE - 4
                            )
                            
                            s = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)
                            shadow_color = (*self.current_color[:3], 40)
                            pygame.draw.rect(s, shadow_color, (0, 0, CELL_SIZE - 4, CELL_SIZE - 4))
                            self.screen.blit(s, rect)
    
    def draw_sidebar(self):
        """Отрисовка боковой панели"""
        for i in range(SIDEBAR_WIDTH):
            alpha = i / SIDEBAR_WIDTH
            color = (
                int(20 * (1 - alpha) + 40 * alpha),
                int(20 * (1 - alpha) + 30 * alpha),
                int(30 * (1 - alpha) + 50 * alpha)
            )
            pygame.draw.line(self.screen, color, (i, 0), (i, SCREEN_HEIGHT))
        
        pygame.draw.line(self.screen, (80, 80, 100), 
                        (SIDEBAR_WIDTH, 0), 
                        (SIDEBAR_WIDTH, SCREEN_HEIGHT), 2)
        
        title_text = self.title_font.render("ТЕТРИС", True, YELLOW)
        self.screen.blit(title_text, (SIDEBAR_WIDTH//2 - title_text.get_width()//2, 20))
        
        y_offset = 100
        
        score_text = self.font.render(f"СЧЕТ: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, y_offset)); y_offset += 45
        
        high_score_text = self.small_font.render(f"РЕКОРД: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (20, y_offset)); y_offset += 35
        
        level_text = self.font.render(f"УРОВЕНЬ: {self.level}", True, GREEN)
        self.screen.blit(level_text, (20, y_offset)); y_offset += 45
        
        lines_text = self.small_font.render(f"ЛИНИЙ: {self.lines_cleared}", True, CYAN)
        self.screen.blit(lines_text, (20, y_offset)); y_offset += 35
        
        pygame.draw.line(self.screen, (60, 60, 80), (20, y_offset), (SIDEBAR_WIDTH-20, y_offset), 2)
        y_offset += 20
        
        location = LOCATIONS[self.location_index]
        location_text = self.small_font.render(f"ЛОКАЦИЯ:", True, WHITE)
        self.screen.blit(location_text, (20, y_offset)); y_offset += 25
        
        location_name = self.small_font.render(location['name'], True, location["effect_color"])
        self.screen.blit(location_name, (20, y_offset)); y_offset += 30
        
        difficulty = LEVELS[self.difficulty_index]
        difficulty_text = self.small_font.render(f"СЛОЖНОСТЬ:", True, WHITE)
        self.screen.blit(difficulty_text, (20, y_offset)); y_offset += 25
        
        diff_name = self.small_font.render(difficulty['name'], True, ORANGE)
        self.screen.blit(diff_name, (20, y_offset)); y_offset += 40
        
        next_text = self.font.render("ДАЛЬШЕ:", True, WHITE)
        self.screen.blit(next_text, (20, y_offset)); y_offset += 40
        
        next_box = pygame.Rect(SIDEBAR_WIDTH//2 - 70, y_offset, 140, 140)
        pygame.draw.rect(self.screen, (40, 40, 60), next_box)
        pygame.draw.rect(self.screen, (80, 80, 100), next_box, 2)
        
        shape_color = SHAPE_COLORS[SHAPES.index(self.next_shape)]
        shape_width = len(self.next_shape[0])
        shape_height = len(self.next_shape)
        
        start_x = SIDEBAR_WIDTH//2 - (shape_width * CELL_SIZE)//2
        start_y = y_offset + 70 - (shape_height * CELL_SIZE)//2
        
        for row_idx, row in enumerate(self.next_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        start_x + col_idx * CELL_SIZE + 2,
                        start_y + row_idx * CELL_SIZE + 2,
                        CELL_SIZE - 4,
                        CELL_SIZE - 4
                    )
                    pygame.draw.rect(self.screen, shape_color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        y_offset += 170
        
        controls_title = self.font.render("УПРАВЛЕНИЕ:", True, WHITE)
        self.screen.blit(controls_title, (20, y_offset)); y_offset += 45
        
        controls = [
            "A,D   - Движение",
            "W     - Вращение ↺",
            "SPACE - Вращение ↻",
            "SHIFT - Мгновенно вниз",
            "P     - Пауза",
            "R     - Рестарт",
            "L     - Смена локации",
            "N     - Смена сложности",
            "ESC   - Меню"
        ]
        
        for control in controls:
            control_text = self.small_font.render(control, True, (180, 180, 200))
            self.screen.blit(control_text, (30, y_offset))
            y_offset += 28
        
        version_text = self.small_font.render("", True, GRAY)
        self.screen.blit(version_text, (SIDEBAR_WIDTH//2 - version_text.get_width()//2, SCREEN_HEIGHT - 30))
    
    def draw_particles(self):
        """Отрисовка частиц"""
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
            else:
                particle.draw(self.screen)
        
        for effect in self.level_effects[:]:
            effect['life'] -= effect['decay']
            if effect['life'] <= 0:
                self.level_effects.remove(effect)
            else:
                alpha = int(effect['life'] * 255)
                color = (*effect['color'][:3], alpha)
                s = pygame.Surface((effect['size'] * 2, effect['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (effect['size'], effect['size']), effect['size'])
                self.screen.blit(s, (effect['x'] - effect['size'], effect['y'] - effect['size']))
    
    def draw_background(self):
        """Отрисовка фона"""
        location = LOCATIONS[self.location_index]
        self.screen.fill(location["bg_color"])
        
        if self.location_index == 0:
            for x, y, size, brightness in self.background_stars:
                color = (int(255 * brightness), int(255 * brightness), int(255 * brightness))
                pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))
        
        elif self.location_index == 1:
            for i in range(0, SCREEN_WIDTH, 40):
                for j in range(0, SCREEN_HEIGHT, 40):
                    color = (
                        min(255, location["bg_color"][0] + random.randint(-10, 10)),
                        min(255, location["bg_color"][1] + random.randint(-10, 10)),
                        min(255, location["bg_color"][2] + random.randint(-10, 10))
                    )
                    pygame.draw.circle(self.screen, color, (i, j), 1)
        
        elif self.location_index == 2:
            for i in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                size = random.randint(1, 3)
                color = (random.randint(30, 70), random.randint(80, 120), random.randint(30, 60))
                pygame.draw.circle(self.screen, color, (x, y), size)
    
    def draw_game_over(self):
        """Отрисовка экрана окончания игры"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = pygame.font.SysFont("arial", 72, bold=True).render("ИГРА ОКОНЧЕНА", True, RED)
        score_text = self.font.render(f"ФИНАЛЬНЫЙ СЧЕТ: {self.score}", True, YELLOW)
        level_text = self.small_font.render(f"ДОСТИГНУТ УРОВЕНЬ: {self.level}", True, GREEN)
        lines_text = self.small_font.render(f"ОЧИЩЕНО ЛИНИЙ: {self.lines_cleared}", True, CYAN)
        restart_text = self.font.render("Нажмите R для новой игры", True, WHITE)
        menu_text = self.small_font.render("ESC - Возврат в меню", True, GRAY)
        
        texts = [game_over_text, score_text, level_text, lines_text, restart_text, menu_text]
        start_y = SCREEN_HEIGHT//2 - 150
        
        for i, text in enumerate(texts):
            self.screen.blit(text, 
                           (SCREEN_WIDTH//2 - text.get_width()//2, 
                            start_y + i * 50))
    
    def draw_pause(self):
        """Отрисовка экрана паузы"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = pygame.font.SysFont("arial", 72, bold=True).render("ПАУЗА", True, YELLOW)
        continue_text = self.font.render("Нажмите P для продолжения", True, WHITE)
        menu_text = self.small_font.render("ESC - Возврат в меню", True, GRAY)
        
        self.screen.blit(pause_text,
                        (SCREEN_WIDTH//2 - pause_text.get_width()//2,
                         SCREEN_HEIGHT//2 - 100))
        self.screen.blit(continue_text,
                        (SCREEN_WIDTH//2 - continue_text.get_width()//2,
                         SCREEN_HEIGHT//2))
        self.screen.blit(menu_text,
                        (SCREEN_WIDTH//2 - menu_text.get_width()//2,
                         SCREEN_HEIGHT//2 + 60))
    
    def draw_menu(self):
        """Отрисовка главного меню"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        title = pygame.font.SysFont("arial", 72, bold=True).render("ТЕТРИС", True, YELLOW)
        subtitle = self.font.render("Классический", True, CYAN)
        
        self.screen.blit(title, 
                        (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle,
                        (SCREEN_WIDTH//2 - subtitle.get_width()//2, 180))
        
        start_y = SCREEN_HEIGHT//2 - 50
        
        for i, option in enumerate(self.menu_options):
            color = WHITE
            if i == self.menu_selection:
                color = YELLOW
                pygame.draw.rect(self.screen, (50, 50, 70, 150),
                               (SCREEN_WIDTH//2 - 150, start_y + i * 70 - 10, 300, 60),
                               border_radius=10)
            
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text,
                           (SCREEN_WIDTH//2 - option_text.get_width()//2,
                            start_y + i * 70))
        
        controls = [
            "↑/↓ - Выбор пункта",
            "ENTER - Выбрать",
            "ESC - Выход из меню"
        ]
        
        controls_y = SCREEN_HEIGHT - 120
        for control in controls:
            control_text = self.small_font.render(control, True, GRAY)
            self.screen.blit(control_text,
                           (SCREEN_WIDTH//2 - control_text.get_width()//2,
                            controls_y))
            controls_y += 30
    
    def handle_input(self):
        """Обработка ввода пользователя"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.show_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    if event.key == pygame.K_q:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            print("Музыка выключена")
                        else:
                            pygame.mixer.music.unpause()
                            print("Музыка включена")
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.handle_menu_selection()
                    elif event.key == pygame.K_ESCAPE:
                        if not self.game_over:
                            self.show_menu = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.show_menu = True
                        self.sound_manager.pause_music()
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            self.sound_manager.pause_music()
                        else:
                            self.sound_manager.unpause_music()
                    elif event.key == pygame.K_q:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            print("Музыка выключена (Q)")
                        else:
                            pygame.mixer.music.unpause()
                            print("Музыка включена (Q)")
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_l:
                        self.location_index = (self.location_index + 1) % len(LOCATIONS)
                        self.sound_manager.play('change_location')
                        self.sound_manager.play_music(self.location_index)
                    elif event.key == pygame.K_n:
                        self.difficulty_index = (self.difficulty_index + 1) % len(LEVELS)
                        self.fall_speed = LEVELS[self.difficulty_index]["fall_speed"]
                        self.sound_manager.play('level_up')
                    
                    if not self.game_over and not self.paused:
                        if event.key == pygame.K_SPACE:
                            rotated = self.rotate_shape(self.current_shape, clockwise=True)
                            if not self.check_collision(rotated, self.current_x, self.current_y):
                                self.current_shape = rotated
                                self.sound_manager.play('rotate')
                        elif event.key == pygame.K_w:
                            rotated = self.rotate_shape(self.current_shape, clockwise=False)
                            if not self.check_collision(rotated, self.current_x, self.current_y):
                                self.current_shape = rotated
                                self.sound_manager.play('rotate')
                        elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                            while not self.check_collision(self.current_shape, self.current_x, self.current_y + 1):
                                self.current_y += 1
                            self.merge_shape()
                        elif event.key == pygame.K_UP:
                            if not self.check_collision(self.current_shape, self.current_x, self.current_y + 1):
                                self.current_y += 1
                                self.sound_manager.play('move')
        
        if not self.show_menu and not self.game_over and not self.paused:
            keys = pygame.key.get_pressed()
            current_time = time.time()
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if current_time - self.last_move_time > self.move_delay:
                    if not self.check_collision(self.current_shape, self.current_x - 1, self.current_y):
                        self.current_x -= 1
                        self.sound_manager.play('move')
                        self.last_move_time = current_time
            
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if current_time - self.last_move_time > self.move_delay:
                    if not self.check_collision(self.current_shape, self.current_x + 1, self.current_y):
                        self.current_x += 1
                        self.sound_manager.play('move')
                        self.last_move_time = current_time
            
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if current_time - self.last_soft_drop_time > self.soft_drop_delay:
                    if not self.check_collision(self.current_shape, self.current_x, self.current_y + 1):
                        self.current_y += 1
                        self.fall_time = 0
                        self.last_soft_drop_time = current_time
    
    def handle_menu_selection(self):
        """Обработка выбора в меню"""
        if self.menu_selection == 0:
            self.reset_game()
            self.show_menu = False
            self.sound_manager.unpause_music()
        elif self.menu_selection == 1:
            self.show_menu = False
            if not self.game_over:
                self.sound_manager.unpause_music()
        elif self.menu_selection == 2:
            self.difficulty_index = (self.difficulty_index + 1) % len(LEVELS)
            self.fall_speed = LEVELS[self.difficulty_index]["fall_speed"]
            self.sound_manager.play('level_up')
        elif self.menu_selection == 3:
            pygame.quit()
            sys.exit()
    
    def update(self, dt):
        """Обновление игры"""
        if self.show_menu or self.game_over or self.paused:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            
            if not self.check_collision(self.current_shape, self.current_x, self.current_y + 1):
                self.current_y += 1
            else:
                self.merge_shape()
    
    def run(self):
        """Основной игровой цикл"""
        last_time = pygame.time.get_ticks()
        
        while True:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            
            self.handle_input()
            self.update(dt)
            
            self.draw_background()
            self.draw_board()
            self.draw_sidebar()
            self.draw_particles()
            
            if self.show_menu:
                self.draw_menu()
            elif self.game_over:
                self.draw_game_over()
            elif self.paused:
                self.draw_pause()
            
            pygame.display.flip()
            self.clock.tick(FPS)

# Запуск игры
if __name__ == "__main__":
    try:
        game = Tetris()
        game.run()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
