import pygame
import os
import sys
import random
import math
import argparse
from enum import Enum

# Parse command line arguments
parser = argparse.ArgumentParser(description='Pixel Samurai Duel')
parser.add_argument('--sound', action='store_true', default=True, help='Enable sound')
parser.add_argument('--no-sound', action='store_false', dest='sound', help='Disable sound')
parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'], default='medium', help='Game difficulty')
parser.add_argument('--mode', choices=['pvp', 'pvc'], default='pvp', help='Game mode (pvp or pvc)')
args = parser.parse_args()

# Initialize Pygame and mixer for sound
pygame.init()
if args.sound:
    pygame.mixer.init()
else:
    print("Sound disabled")

# Game Settings
WIDTH, HEIGHT = 1280, 720
FPS = 60
GRAVITY = 0.8
SCROLL_SPEED = 5
PROJECTILE_SPEED = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
PURPLE = (147, 0, 211)
GOLD = (255, 215, 0)


# Game Mode enum
class GameMode(Enum):
    PLAYER_VS_PLAYER = 0
    PLAYER_VS_COMPUTER = 1


# AI Difficulty enum
class AIDifficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


# Set game mode from command line args
current_game_mode = GameMode.PLAYER_VS_COMPUTER if args.mode == 'pvc' else GameMode.PLAYER_VS_PLAYER

# Set AI difficulty from command line args
if args.difficulty == 'easy':
    ai_difficulty = AIDifficulty.EASY
elif args.difficulty == 'hard':
    ai_difficulty = AIDifficulty.HARD
else:
    ai_difficulty = AIDifficulty.MEDIUM

# Screen setup with larger resolution
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Samurai Duel")
clock = pygame.time.Clock()

# Set icon
icon_surface = pygame.Surface((32, 32))
icon_surface.fill((150, 0, 200))
pygame.draw.rect(icon_surface, (255, 50, 50), (8, 8, 16, 16))
pygame.display.set_icon(icon_surface)

# Sound enabled flag
sound_enabled = args.sound


# Load Images Function with Error Handling
def load_images(folder, scale=1.5):
    images = []
    try:
        for filename in sorted(os.listdir(folder)):
            if filename.endswith((".png", ".jpg")):
                img = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
                # Scale image to larger size
                img = pygame.transform.scale(img, (int(64 * scale), int(64 * scale)))
                images.append(img)
        if not images:
            placeholder = pygame.Surface((int(64 * scale), int(64 * scale)), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 100))
            images = [placeholder]
    except (FileNotFoundError, OSError):
        placeholder = pygame.Surface((int(64 * scale), int(64 * scale)), pygame.SRCALPHA)
        placeholder.fill((255, 0, 255, 100))
        images = [placeholder]
    return images


# Create asset directories if they don't exist
os.makedirs("assets/player1/idle", exist_ok=True)
os.makedirs("assets/player1/run", exist_ok=True)
os.makedirs("assets/player1/attack", exist_ok=True)
os.makedirs("assets/player1/jump", exist_ok=True)
os.makedirs("assets/player1/hurt", exist_ok=True)
os.makedirs("assets/player2/idle", exist_ok=True)
os.makedirs("assets/player2/run", exist_ok=True)
os.makedirs("assets/player2/attack", exist_ok=True)
os.makedirs("assets/player2/jump", exist_ok=True)
os.makedirs("assets/player2/hurt", exist_ok=True)
os.makedirs("assets/effects", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)
os.makedirs("assets/backgrounds", exist_ok=True)
os.makedirs("assets/ui", exist_ok=True)


# Create placeholder sprites if assets don't exist
def create_placeholder_sprite(color, folder, count=4, scale=1.5):
    for i in range(count):
        img = pygame.Surface((int(64 * scale), int(64 * scale)), pygame.SRCALPHA)
        img.fill((0, 0, 0, 0))
        pygame.draw.rect(img, color, (int(10 * scale), int(10 * scale), int(44 * scale), int(54 * scale)))
        pygame.draw.circle(img, color, (int(32 * scale), int(20 * scale)), int(12 * scale))
        pygame.image.save(img, os.path.join(folder, f"frame{i}.png"))


# Create placeholder effects
def create_placeholder_effects():
    # Explosion effect
    for i in range(5):
        img = pygame.Surface((128, 128), pygame.SRCALPHA)
        radius = 10 + i * 10
        pygame.draw.circle(img, (255, 200, 0, 200 - i * 40), (64, 64), radius)
        pygame.draw.circle(img, (255, 100, 0, 150 - i * 30), (64, 64), radius - 5)
        pygame.image.save(img, os.path.join("assets/effects", f"explosion{i}.png"))

    # Shield effect
    for i in range(3):
        img = pygame.Surface((128, 128), pygame.SRCALPHA)
        radius = 40 - i * 3
        pygame.draw.circle(img, (100, 200, 255, 150 - i * 40), (64, 64), radius)
        pygame.image.save(img, os.path.join("assets/effects", f"shield{i}.png"))

    # UI elements
    sound_on = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(sound_on, (200, 200, 200), (16, 16), 12)
    pygame.draw.circle(sound_on, (50, 50, 50), (16, 16), 8)
    pygame.image.save(sound_on, os.path.join("assets/ui", "sound_on.png"))

    sound_off = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(sound_off, (200, 200, 200), (16, 16), 12)
    pygame.draw.line(sound_off, (255, 50, 50), (8, 8), (24, 24), 3)
    pygame.image.save(sound_off, os.path.join("assets/ui", "sound_off.png"))


# Check if assets exist and create placeholders if needed
if not os.listdir("assets/player1/idle"):
    create_placeholder_sprite((255, 0, 0, 200), "assets/player1/idle")
if not os.listdir("assets/player1/run"):
    create_placeholder_sprite((255, 0, 0, 200), "assets/player1/run")
if not os.listdir("assets/player1/attack"):
    create_placeholder_sprite((255, 0, 0, 200), "assets/player1/attack")
if not os.listdir("assets/player1/jump"):
    create_placeholder_sprite((255, 0, 0, 200), "assets/player1/jump", 1)
if not os.listdir("assets/player1/hurt"):
    create_placeholder_sprite((255, 0, 0, 200), "assets/player1/hurt", 1)

if not os.listdir("assets/player2/idle"):
    create_placeholder_sprite((0, 0, 255, 200), "assets/player2/idle")
if not os.listdir("assets/player2/run"):
    create_placeholder_sprite((0, 0, 255, 200), "assets/player2/run")
if not os.listdir("assets/player2/attack"):
    create_placeholder_sprite((0, 0, 255, 200), "assets/player2/attack")
if not os.listdir("assets/player2/jump"):
    create_placeholder_sprite((0, 0, 255, 200), "assets/player2/jump", 1)
if not os.listdir("assets/player2/hurt"):
    create_placeholder_sprite((0, 0, 255, 200), "assets/player2/hurt", 1)

if not os.listdir("assets/effects"):
    create_placeholder_effects()

# Create generic background image if none exists
if not os.listdir("assets/backgrounds"):
    background = pygame.Surface((WIDTH * 2, HEIGHT))
    # Create a more interesting background with parallax layers

    # Sky layer
    for y in range(0, HEIGHT, 4):
        color_value = max(50, 150 - y // 3)
        color = (color_value, color_value + 50, 255)
        pygame.draw.line(background, color, (0, y), (WIDTH * 2, y), 4)

    # Far mountains
    for x in range(0, WIDTH * 2, 200):
        height = random.randint(100, 200)
        points = [(x, HEIGHT - height)]
        for i in range(5):
            points.append((x + (i + 1) * 40, HEIGHT - height + random.randint(-30, 30)))
        points.append((x + 200, HEIGHT - height))
        points.append((x + 200, HEIGHT))
        points.append((x, HEIGHT))
        pygame.draw.polygon(background, (80, 80, 100), points)

    # Near hills
    for x in range(-50, WIDTH * 2, 150):
        height = random.randint(60, 120)
        points = [(x, HEIGHT - height)]
        for i in range(4):
            points.append((x + (i + 1) * 50, HEIGHT - height + random.randint(-25, 25)))
        points.append((x + 200, HEIGHT - height))
        points.append((x + 200, HEIGHT))
        points.append((x, HEIGHT))
        pygame.draw.polygon(background, (30, 100, 30), points)

    # Ground
    pygame.draw.rect(background, (50, 150, 50), (0, HEIGHT - 50, WIDTH * 2, 50))

    # Add some details to the ground
    for x in range(0, WIDTH * 2, 8):
        height = random.randint(2, 6)
        pygame.draw.line(background, (30, 120, 30), (x, HEIGHT - 50), (x, HEIGHT - 50 + height), 2)

    pygame.image.save(background, os.path.join("assets/backgrounds", "background.png"))

# Load Player Sprites
try:
    player1_idle = load_images("assets/player1/idle")
    player1_run = load_images("assets/player1/run")
    player1_attack = load_images("assets/player1/attack")
    player1_jump = load_images("assets/player1/jump")
    player1_hurt = load_images("assets/player1/hurt")

    player2_idle = load_images("assets/player2/idle")
    player2_run = load_images("assets/player2/run")
    player2_attack = load_images("assets/player2/attack")
    player2_jump = load_images("assets/player2/jump")
    player2_hurt = load_images("assets/player2/hurt")

    explosion_imgs = load_images("assets/effects", scale=2.0)
    shield_imgs = load_images("assets/effects", scale=2.0)

    # Load UI elements
    try:
        sound_on_img = pygame.image.load(os.path.join("assets/ui", "sound_on.png")).convert_alpha()
        sound_off_img = pygame.image.load(os.path.join("assets/ui", "sound_off.png")).convert_alpha()
    except:
        sound_on_img = pygame.Surface((32, 32), pygame.SRCALPHA)
        sound_off_img = pygame.Surface((32, 32), pygame.SRCALPHA)
except Exception as e:
    print(f"Error loading images: {e}")
    placeholder = pygame.Surface((96, 96), pygame.SRCALPHA)
    placeholder.fill((255, 0, 255, 100))
    player1_idle = player1_run = player1_attack = player1_jump = player1_hurt = [placeholder]
    player2_idle = player2_run = player2_attack = player2_jump = player2_hurt = [placeholder]
    explosion_imgs = shield_imgs = [placeholder]
    sound_on_img = sound_off_img = pygame.Surface((32, 32), pygame.SRCALPHA)

# Load Background
try:
    background_img = pygame.image.load(os.path.join("assets/backgrounds", "background.png")).convert()
except:
    # Create pixel art background
    background_img = pygame.Surface((WIDTH * 2, HEIGHT))
    for x in range(0, WIDTH * 2, 32):
        for y in range(0, HEIGHT, 32):
            color = (100, 150, 255) if y < HEIGHT - 100 else (50, 100, 50)
            pygame.draw.rect(background_img, color, (x, y, 32, 32))
            pygame.draw.rect(background_img, (color[0] - 20, color[1] - 20, color[2] - 20), (x, y, 32, 32), 1)

background_rect = background_img.get_rect(topleft=(0, 0))
bg_scroll = 0

# Try to load sound effects or use empty sounds
try:
    jump_sound = pygame.mixer.Sound("assets/sounds/jump.mp3")
    attack_sound = pygame.mixer.Sound("assets/sounds/hit.mp3")
    hit_sound = pygame.mixer.Sound("assets/sounds/hit.mp3")
    menu_select_sound = pygame.mixer.Sound("assets/sounds/menu_select.mp3")
    block_sound = pygame.mixer.Sound("assets/sounds/block.mp3")
    land_sound = pygame.mixer.Sound("assets/sounds/land.mp3")
    defeat_sound = pygame.mixer.Sound("assets/sounds/defeat.mp3")
    music = pygame.mixer.Sound("assets/sounds/background_music.mp3")
except:
    # Create placeholder silent sounds
    jump_sound = pygame.mixer.Sound(buffer=bytearray(24))
    attack_sound = pygame.mixer.Sound(buffer=bytearray(24))
    hit_sound = pygame.mixer.Sound(buffer=bytearray(24))
    menu_select_sound = pygame.mixer.Sound(buffer=bytearray(24))
    block_sound = pygame.mixer.Sound(buffer=bytearray(24))
    land_sound = pygame.mixer.Sound(buffer=bytearray(24))
    defeat_sound = pygame.mixer.Sound(buffer=bytearray(24))
    music = pygame.mixer.Sound(buffer=bytearray(24))

# Set volume
jump_sound.set_volume(0.5)
attack_sound.set_volume(0.7)
hit_sound.set_volume(0.8)
menu_select_sound.set_volume(0.6)
block_sound.set_volume(0.5)
land_sound.set_volume(0.5)
defeat_sound.set_volume(0.8)
music.set_volume(0.4)

# Start music loop if sound is enabled
if sound_enabled:
    music.play(-1)  # Loop indefinitely


# Effects class for visual effects
class Effect(pygame.sprite.Sprite):
    def __init__(self, x, y, images, animation_speed=0.2):
        super().__init__()
        self.images = images
        self.index = 0
        self.animation_speed = animation_speed
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.completed = False

    def update(self, scroll):
        self.index += self.animation_speed
        if self.index >= len(self.images):
            self.completed = True
            self.kill()
        else:
            self.image = self.images[int(self.index)]
            self.rect.x -= scroll

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="normal"):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.platform_type = platform_type

        if platform_type == "normal":
            base_color = GREEN
            detail_color = (0, 200, 0)
            border_color = (0, 100, 0)
        elif platform_type == "stone":
            base_color = (120, 120, 120)
            detail_color = (150, 150, 150)
            border_color = (80, 80, 80)
        elif platform_type == "ice":
            base_color = (200, 240, 255)
            detail_color = (220, 250, 255)
            border_color = (180, 210, 230)
        elif platform_type == "lava":
            base_color = (200, 80, 10)
            detail_color = (255, 100, 20)
            border_color = (100, 40, 0)
        else:
            base_color = GREEN
            detail_color = (0, 200, 0)
            border_color = (0, 100, 0)

        self.image.fill(base_color)

        # Add pixel art texture to platforms
        for px in range(0, width, 8):
            for py in range(0, height, 8):
                if random.random() > 0.5:
                    pygame.draw.rect(self.image, detail_color, (px, py, 4, 4))

        pygame.draw.rect(self.image, border_color, (0, 0, width, height), 3)
        self.rect = self.image.get_rect(topleft=(x, y))

        # Special platform properties
        self.is_damaging = platform_type == "lava"
        self.damage = 1 if self.is_damaging else 0
        self.is_slippery = platform_type == "ice"
        self.slip_factor = 0.95 if self.is_slippery else 0.8

    def update(self, scroll):
        self.rect.x -= scroll

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

        # Add effects for special platforms
        if self.is_damaging and random.random() < 0.1:
            x = random.randint(self.rect.left, self.rect.right)
            y = self.rect.top - 5
            particles.append(Particle(x, y, (255, 100, 0), speed=2))


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)

        # Different visuals based on powerup type
        if powerup_type == "health":
            color = (255, 50, 50)  # Red
            pygame.draw.rect(self.image, color, (5, 5, 20, 20))
            pygame.draw.rect(self.image, (255, 255, 255), (12, 8, 6, 14))
            pygame.draw.rect(self.image, (255, 255, 255), (8, 12, 14, 6))
        elif powerup_type == "shield":
            color = (50, 150, 255)  # Blue
            pygame.draw.circle(self.image, color, (15, 15), 12)
            pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 8, 3)
        elif powerup_type == "speed":
            color = (50, 255, 50)  # Green
            pygame.draw.polygon(self.image, color, [(5, 20), (15, 5), (25, 20)])
            pygame.draw.line(self.image, (255, 255, 255), (15, 8), (15, 25), 3)
        else:  # "special"
            color = (255, 215, 0)  # Gold
            pygame.draw.circle(self.image, color, (15, 15), 12)
            pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 6)

        self.rect = self.image.get_rect(center=(x, y))
        self.float_offset = 0
        self.float_speed = 0.1
        self.float_direction = 1
        self.original_y = y

    def update(self, scroll):
        # Floating animation
        self.float_offset += self.float_speed * self.float_direction
        if abs(self.float_offset) > 5:
            self.float_direction *= -1

        self.rect.y = self.original_y + self.float_offset
        self.rect.x -= scroll

        # Create sparkle particles occasionally
        if random.random() < 0.05:
            x = self.rect.centerx + random.randint(-10, 10)
            y = self.rect.centery + random.randint(-10, 10)
            color = (255, 255, 200) if self.powerup_type == "special" else (255, 255, 255)
            particles.append(Particle(x, y, color, speed=0.5))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def apply_effect(self, player):
        if self.powerup_type == "health":
            player.health = min(100, player.health + 20)
            return "Health +20"
        elif self.powerup_type == "shield":
            player.shield_active = True
            player.shield_time = 300  # 5 seconds at 60 FPS
            return "Shield Activated"
        elif self.powerup_type == "speed":
            player.speed_boost = True
            player.speed_boost_time = 300  # 5 seconds
            player.speed = player.base_speed * 1.5
            return "Speed Boost"
        elif self.powerup_type == "special":
            player.special_meter = player.max_special
            player.special_ready = True
            return "Special Attack Ready!"


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing_right, owner, power=1.0, projectile_type="normal"):
        super().__init__()
        self.projectile_type = projectile_type
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)

        # Different visuals based on projectile type
        if projectile_type == "normal":
            # Regular projectile
            pygame.draw.ellipse(self.image, (255, 200, 0), (0, 0, 20, 10))
            pygame.draw.ellipse(self.image, (255, 150, 0), (2, 2, 16, 6))
        elif projectile_type == "special":
            # Special attack projectile
            pygame.draw.ellipse(self.image, (100, 100, 255), (0, 0, 20, 10))
            pygame.draw.ellipse(self.image, (150, 150, 255), (2, 2, 16, 6))
            # Add glow effect
            glow = pygame.Surface((30, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (100, 100, 255, 100), (0, 0, 30, 20))
            self.image = glow

        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = facing_right
        self.speed = PROJECTILE_SPEED * (1.2 if projectile_type == "special" else 1.0)
        self.original_x = x
        self.owner = owner  # To track who fired the projectile
        self.damage = int(10 * power) if projectile_type == "normal" else int(15 * power)

        # Trail effect variables
        self.trail_timer = 0

    def update(self, scroll):
        self.rect.x += self.speed if self.facing_right else -self.speed
        self.rect.x -= scroll

        # Create trail particles
        self.trail_timer += 1
        if self.trail_timer >= 3:  # Create trail every few frames
            self.trail_timer = 0
            trail_color = (255, 150, 0) if self.projectile_type == "normal" else (100, 100, 255)
            particles.append(Particle(self.rect.centerx, self.rect.centery, trail_color, speed=0.5))

        if abs(self.rect.x - self.original_x) > WIDTH:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class Samurai(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, idle_imgs, run_imgs, attack_imgs, jump_imgs, hurt_imgs, player_name="Player",
                 is_ai=False):
        super().__init__()
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.base_speed = 6
        self.speed = self.base_speed
        self.health = 100
        self.score = 0
        self.controls = controls
        self.player_name = player_name
        self.idle_imgs = idle_imgs
        self.run_imgs = run_imgs
        self.attack_imgs = attack_imgs
        self.jump_imgs = jump_imgs
        self.hurt_imgs = hurt_imgs
        self.current_imgs = idle_imgs
        self.index = 0
        self.image = self.current_imgs[0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        # Character state
        self.attacking = False
        self.is_attacking = False
        self.facing_right = True
        self.on_ground = False
        self.jump_power = -16
        self.is_jumping = False
        self.is_hurting = False
        self.hurt_timer = 0
        self.attack_cooldown = 25
        self.current_attack_cooldown = 0
        self.projectiles = pygame.sprite.Group()
        self.special_meter = 0
        self.max_special = 100
        self.special_ready = False
        self.combo_count = 0
        self.last_hit_time = 0

        # Powerup effects
        self.shield_active = False
        self.shield_time = 0
        self.speed_boost = False
        self.speed_boost_time = 0

        # AI variables
        self.is_ai = is_ai
        self.ai_timer = 0
        self.ai_action_time = 0
        self.ai_target = None
        self.ai_difficulty = ai_difficulty
        self.ai_state = "idle"
        self.ai_jump_timer = 0
        self.ai_platform_awareness = 0.5  # How well AI avoids falling

        # Set AI difficulty factors
        if self.is_ai:
            if ai_difficulty == AIDifficulty.EASY:
                self.ai_platform_awareness = 0.3
                self.ai_reaction_time = 1.5  # Slower
                self.ai_accuracy = 0.6  # Less accurate
                self.ai_aggression = 0.4  # Less aggressive
            elif ai_difficulty == AIDifficulty.MEDIUM:
                self.ai_platform_awareness = 0.7
                self.ai_reaction_time = 1.0  # Normal
                self.ai_accuracy = 0.8  # Moderately accurate
                self.ai_aggression = 0.7  # Moderately aggressive
            else:  # HARD
                self.ai_platform_awareness = 0.9
                self.ai_reaction_time = 0.5  # Fast reactions
                self.ai_accuracy = 0.95  # Very accurate
                self.ai_aggression = 0.9  # Very aggressive

        # Animation speeds
        self.animation_speed = {
            'idle': 0.15,
            'run': 0.2,
            'attack': 0.3,
            'jump': 0.2,
            'hurt': 0.25
        }

        # Stats tracking
        self.hits_landed = 0
        self.damage_dealt = 0
        self.jumps_made = 0
        self.specials_used = 0

    def handle_keys(self, keys, effects_group):
        if self.health <= 0:
            return

        self.vel_x = 0
        if not self.is_attacking and not self.is_hurting:
            if keys[self.controls['left']]:
                self.vel_x = -self.speed
                self.facing_right = False
                self.current_imgs = self.run_imgs
                self.current_animation_speed = self.animation_speed['run']
            elif keys[self.controls['right']]:
                self.vel_x = self.speed
                self.facing_right = True
                self.current_imgs = self.run_imgs
                self.current_animation_speed = self.animation_speed['run']
            else:
                self.current_imgs = self.idle_imgs
                self.current_animation_speed = self.animation_speed['idle']

            if keys[self.controls['jump']] and self.on_ground and not self.is_jumping:
                self.vel_y = self.jump_power
                self.is_jumping = True
                self.on_ground = False
                self.current_imgs = self.jump_imgs
                self.current_animation_speed = self.animation_speed['jump']
                self.jumps_made += 1
                if sound_enabled:
                    jump_sound.play()

            if keys[self.controls['attack']] and self.current_attack_cooldown == 0:
                self.attacking = True
                self.is_attacking = True
                self.current_imgs = self.attack_imgs
                self.current_animation_speed = self.animation_speed['attack']
                self.index = 0
                self.current_attack_cooldown = self.attack_cooldown

                # Regular attack
                projectile_x = self.rect.centerx + (40 if self.facing_right else -40)
                projectile_y = self.rect.centery
                projectile = Projectile(projectile_x, projectile_y, self.facing_right, self)
                self.projectiles.add(projectile)
                all_sprites.add(projectile)
                if sound_enabled:
                    attack_sound.play()

                # Add small flash effect at projectile spawn point
                flash = Effect(projectile_x, projectile_y, explosion_imgs[:3], 0.3)
                effects_group.add(flash)

            # Special attack logic
            if keys[self.controls['special']] and self.special_meter >= self.max_special:
                self.attacking = True
                self.is_attacking = True
                self.current_imgs = self.attack_imgs
                self.current_animation_speed = self.animation_speed['attack'] * 1.5
                self.index = 0
                self.special_meter = 0
                self.special_ready = False
                self.specials_used += 1

                # Triple projectile special attack
                for i in range(-1, 2):
                    projectile_x = self.rect.centerx + (40 if self.facing_right else -40)
                    projectile_y = self.rect.centery + i * 20
                    projectile = Projectile(projectile_x, projectile_y, self.facing_right, self, power=1.5,
                                            projectile_type="special")
                    self.projectiles.add(projectile)
                    all_sprites.add(projectile)

                # Add large flash effect for special attack
                flash = Effect(self.rect.centerx + (50 if self.facing_right else -50),
                               self.rect.centery, explosion_imgs, 0.2)
                effects_group.add(flash)
                if sound_enabled:
                    attack_sound.play()

    def ai_action(self, target, effects_group, platforms):
        """AI control logic for CPU opponent"""
        if self.health <= 0 or not self.ai_target:
            return

        self.ai_timer += 1

        reaction_time = int(60 * self.ai_reaction_time)  # How often AI makes decisions

        # Only make decisions periodically to simulate human reaction time
        if self.ai_timer >= reaction_time:
            self.ai_timer = 0
            self.ai_action_time = random.randint(10, 20)

            # Determine relative position to target
            target_distance = abs(self.rect.centerx - target.rect.centerx)
            target_on_left = target.rect.centerx < self.rect.centerx

            # Check if about to fall off platform
            about_to_fall = True
            for platform in platforms:
                # Check if there's a platform below and ahead in the direction we're moving
                look_ahead = 50 * (-1 if target_on_left else 1)
                test_point = (self.rect.centerx + look_ahead, self.rect.bottom + 10)

                if platform.rect.collidepoint(test_point):
                    about_to_fall = False
                    break

            # AI awareness check - harder difficulties are more aware of platforms
            if about_to_fall and random.random() < self.ai_platform_awareness:
                # If about to fall off and aware, reverse direction briefly
                self.vel_x = self.speed * (1 if target_on_left else -1)
                self.facing_right = target_on_left
                self.ai_state = "evading"
                self.current_imgs = self.run_imgs
                self.current_animation_speed = self.animation_speed['run']
                return

            # Simple state machine for AI behavior based on distance and aggression
            if target_distance > 300:
                # Far away - move toward player
                self.ai_state = "approaching"
                self.vel_x = -self.speed if target_on_left else self.speed
                self.facing_right = not target_on_left
                self.current_imgs = self.run_imgs
                self.current_animation_speed = self.animation_speed['run']

                # Occasionally jump to traverse platforms
                if random.random() < 0.1 * self.ai_aggression and self.on_ground:
                    self.vel_y = self.jump_power
                    self.is_jumping = True
                    self.on_ground = False
                    self.current_imgs = self.jump_imgs
                    self.current_animation_speed = self.animation_speed['jump']
                    self.jumps_made += 1
                    if sound_enabled:
                        jump_sound.play()

            elif target_distance > 150:
                # Medium distance - attack or move based on aggression
                if random.random() < 0.6 * self.ai_aggression and self.current_attack_cooldown == 0:
                    self.ai_state = "attacking"
                    # Attack
                    self.attacking = True
                    self.is_attacking = True
                    self.current_imgs = self.attack_imgs
                    self.current_animation_speed = self.animation_speed['attack']
                    self.index = 0
                    self.current_attack_cooldown = self.attack_cooldown

                    # Fire projectile
                    projectile_x = self.rect.centerx + (40 if self.facing_right else -40)
                    projectile_y = self.rect.centery
                    projectile = Projectile(projectile_x, projectile_y, self.facing_right, self)
                    self.projectiles.add(projectile)
                    all_sprites.add(projectile)
                    if sound_enabled:
                        attack_sound.play()

                    # Add effect
                    flash = Effect(projectile_x, projectile_y, explosion_imgs[:3], 0.3)
                    effects_group.add(flash)
                else:
                    self.ai_state = "positioning"
                    # Move toward player
                    self.vel_x = -self.speed if target_on_left else self.speed
                    self.facing_right = not target_on_left
                    self.current_imgs = self.run_imgs
                    self.current_animation_speed = self.animation_speed['run']
            else:
                # Close range - attack, use special, or dodge based on situation
                dodge_chance = 0.3 * (1 - self.ai_aggression)  # Less aggressive AI dodges more

                if random.random() < dodge_chance:
                    self.ai_state = "dodging"
                    # Dodge (move away)
                    self.vel_x = self.speed if target_on_left else -self.speed
                    self.facing_right = target_on_left

                    # Maybe jump while dodging
                    if random.random() < 0.4 and self.on_ground:
                        self.vel_y = self.jump_power
                        self.is_jumping = True
                        self.on_ground = False
                        self.jumps_made += 1
                        if sound_enabled:
                            jump_sound.play()

                elif self.special_meter >= self.max_special and random.random() < 0.8 * self.ai_accuracy:
                    self.ai_state = "special_attack"
                    # Use special attack if available
                    self.attacking = True
                    self.is_attacking = True
                    self.current_imgs = self.attack_imgs
                    self.current_animation_speed = self.animation_speed['attack'] * 1.5
                    self.index = 0
                    self.special_meter = 0
                    self.special_ready = False
                    self.specials_used += 1

                    # Triple projectile special attack
                    for i in range(-1, 2):
                        projectile_x = self.rect.centerx + (40 if self.facing_right else -40)
                        projectile_y = self.rect.centery + i * 20
                        projectile = Projectile(projectile_x, projectile_y, self.facing_right, self, power=1.5,
                                                projectile_type="special")
                        self.projectiles.add(projectile)
                        all_sprites.add(projectile)

                    # Add effect
                    flash = Effect(self.rect.centerx + (50 if self.facing_right else -50),
                                   self.rect.centery, explosion_imgs, 0.2)
                    effects_group.add(flash)
                    if sound_enabled:
                        attack_sound.play()

                elif self.current_attack_cooldown == 0 and random.random() < 0.7 * self.ai_accuracy:
                    self.ai_state = "attacking"
                    # Regular attack
                    self.attacking = True
                    self.is_attacking = True
                    self.current_imgs = self.attack_imgs
                    self.current_animation_speed = self.animation_speed['attack']
                    self.index = 0
                    self.current_attack_cooldown = self.attack_cooldown

                    # Fire projectile
                    projectile_x = self.rect.centerx + (40 if self.facing_right else -40)
                    projectile_y = self.rect.centery
                    projectile = Projectile(projectile_x, projectile_y, self.facing_right, self)
                    self.projectiles.add(projectile)
                    all_sprites.add(projectile)
                    if sound_enabled:
                        attack_sound.play()

                    # Add effect
                    flash = Effect(projectile_x, projectile_y, explosion_imgs[:3], 0.3)
                    effects_group.add(flash)
                else:
                    # Just move or idle
                    if random.random() < 0.5:
                        self.ai_state = "repositioning"
                        # Move randomly
                        direction = 1 if random.random() < 0.5 else -1
                        self.vel_x = self.speed * direction
                        self.facing_right = direction > 0
                        self.current_imgs = self.run_imgs
                        self.current_animation_speed = self.animation_speed['run']

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

    def update(self, scroll):
        # AI logic if this is a CPU player
        if self.is_ai and self.ai_target:
            self.ai_action(self.ai_target, effects, platforms)

        # Movement and position updates
        if not self.is_hurting:
            self.x += self.vel_x
            self.y += self.vel_y

            # Keep player within screen bounds
            self.x = max(0, min(self.x, WIDTH - self.rect.width))
            self.y = max(0, min(self.y, HEIGHT - self.rect.height))

        # Animation handling
        if hasattr(self, 'current_animation_speed'):
            self.index += self.current_animation_speed
        else:
            self.index += 0.2  # Default animation speed

        if self.is_attacking:
            if self.index >= len(self.current_imgs):
                self.index = 0
                self.is_attacking = False
                self.attacking = False
                self.current_imgs = self.idle_imgs
                self.current_animation_speed = self.animation_speed['idle']
        elif self.is_jumping:
            if self.index >= len(self.current_imgs):
                self.index = 0
                if self.vel_y > 0:
                    self.current_imgs = self.idle_imgs
                    self.current_animation_speed = self.animation_speed['idle']
                    self.is_jumping = False
        elif self.is_hurting:
            if self.index >= len(self.current_imgs):
                self.index = 0
                self.is_hurting = False
                self.current_animation_speed = self.animation_speed['idle']

        if not self.is_attacking and not self.is_jumping and not self.is_hurting:
            if self.vel_x != 0:
                self.current_imgs = self.run_imgs
                self.current_animation_speed = self.animation_speed['run']
            else:
                self.current_imgs = self.idle_imgs
                self.current_animation_speed = self.animation_speed['idle']

        # Decrease attack cooldown
        if self.current_attack_cooldown > 0:
            self.current_attack_cooldown -= 1

        # Decrease combo counter over time
        if self.combo_count > 0 and pygame.time.get_ticks() - self.last_hit_time > 2000:
            self.combo_count = 0

        # Update powerup timers
        if self.shield_active:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield_active = False

        if self.speed_boost:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed_boost = False
                self.speed = self.base_speed

        # Update image based on animation frame
        if self.current_imgs and len(self.current_imgs) > 0:
            self.image = self.current_imgs[int(self.index) % len(self.current_imgs)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(topleft=(int(self.x - scroll), int(self.y)))

        # Update projectiles
        self.projectiles.update(scroll)

        # Special meter charge - gradually increase over time when not at max
        if self.special_meter < self.max_special:
            self.special_meter += 0.1
            if self.special_meter >= self.max_special and not self.special_ready:
                self.special_ready = True
                # Visual indicator when special is ready
                flash = Effect(self.rect.centerx, self.rect.centery - 30, shield_imgs, 0.2)
                effects.add(flash)

    def draw(self, surface):
        # Draw shield effect if active
        if self.shield_active:
            shield_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surf, (100, 200, 255, 100), shield_surf.get_rect())
            surface.blit(shield_surf, (self.rect.x - 10, self.rect.y - 10))

        # Draw speed boost effect if active
        if self.speed_boost:
            for i in range(3):
                offset = random.randint(-5, 5)
                alpha = random.randint(50, 150)
                ghost = self.image.copy()
                ghost.set_alpha(alpha)
                surface.blit(ghost, (self.rect.x - 10 + offset, self.rect.y + offset))

        # Draw character
        surface.blit(self.image, self.rect.topleft)

        # Draw name above character
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(self.player_name, True, WHITE)
        name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.top - 30))
        pygame.draw.rect(surface, (0, 0, 0, 128),
                         (name_rect.x - 5, name_rect.y - 5, name_rect.width + 10, name_rect.height + 10))
        surface.blit(name_text, name_rect)

        # Draw health bar background
        pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y - 20, 50, 10))

        # Draw health bar with gradient color
        health_width = max(0, (self.health / 100) * 50)
        health_color = (
            min(255, (100 - self.health) * 5.1),  # Red component
            min(255, self.health * 2.55),  # Green component
            0  # Blue component
        )
        pygame.draw.rect(surface, health_color, (self.rect.x, self.rect.y - 20, health_width, 10))

        # Draw special attack meter below health bar
        special_width = (self.special_meter / self.max_special) * 50
        special_color = BLUE if not self.special_ready else GOLD
        pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y - 10, 50, 5))
        pygame.draw.rect(surface, special_color, (self.rect.x, self.rect.y - 10, special_width, 5))

        # Draw combo counter if active
        if self.combo_count > 1:
            combo_font = pygame.font.Font(None, 28)
            combo_text = combo_font.render(f"{self.combo_count}x Combo!", True, GOLD)
            combo_rect = combo_text.get_rect(center=(self.rect.centerx, self.rect.top - 50))
            surface.blit(combo_text, combo_rect)

        # Draw AI state for debugging if this is an AI player
        if self.is_ai and DEBUG_MODE:
            ai_font = pygame.font.Font(None, 20)
            ai_text = ai_font.render(f"AI: {self.ai_state}", True, WHITE)
            surface.blit(ai_text, (self.rect.x, self.rect.y - 40))

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

    def handle_collision(self, platforms):
        collided = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Check primarily for landing on top of platform
                if self.vel_y > 0 and self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.y = self.rect.y
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                    collided = True

                    # Check for damaging platforms
                    if platform.is_damaging and pygame.time.get_ticks() % 30 == 0:
                        self.take_damage(platform.damage)
                        create_particles(self.rect.centerx, self.rect.bottom, 5, (255, 100, 0))

                    # Apply slippery effect
                    if platform.is_slippery:
                        # Reduce deceleration on ice
                        if abs(self.vel_x) > 0:
                            self.vel_x *= platform.slip_factor

                    # Play landing sound
                    if not self.is_ai and abs(self.vel_y) > 5 and sound_enabled:
                        land_sound.play()

        if not collided:
            self.on_ground = False

    def take_damage(self, amount, hit_by=None):
        # Check for shield protection
        if self.shield_active:
            if sound_enabled:
                block_sound.play()
            # Create shield impact effect
            shield_effect = Effect(self.rect.centerx, self.rect.centery, shield_imgs, 0.2)
            effects.add(shield_effect)
            return

        if not self.is_hurting and self.health > 0:
            self.health = max(0, self.health - amount)
            self.is_hurting = True
            self.hurt_timer = pygame.time.get_ticks()
            self.index = 0
            self.current_imgs = self.hurt_imgs
            self.current_animation_speed = self.animation_speed['hurt']
            if sound_enabled:
                hit_sound.play()

            # If hit by an opponent, increase their combo and special meter
            if hit_by and isinstance(hit_by, Samurai):
                hit_by.hits_landed += 1
                hit_by.damage_dealt += amount
                hit_by.combo_count += 1
                hit_by.last_hit_time = pygame.time.get_ticks()
                hit_by.special_meter = min(hit_by.max_special, hit_by.special_meter + 10)

            # Play defeat sound when health reaches 0
            if self.health <= 0 and sound_enabled:
                defeat_sound.play()


# Custom Button class for menus
class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 255), hover_color=(150, 150, 255), text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color

        # Draw button with pixel art style
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (color[0] * 0.8, color[1] * 0.8, color[2] * 0.8), self.rect, 4)

        # Add lighting effect
        light_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width - 8, 10)
        pygame.draw.rect(surface, (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50)),
                         light_rect)

        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click


# Particle system for visual effects
class Particle:
    def __init__(self, x, y, color, speed=1):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.life = random.randint(20, 60)
        self.max_life = self.life
        self.vel_x = random.uniform(-2, 2) * speed
        self.vel_y = random.uniform(-4, -1) * speed

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.1  # Gravity
        self.life -= 1
        self.size = max(1, self.size * (self.life / self.max_life))

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


# Cloud class for background decoration
class Cloud:
    def __init__(self):
        self.width = random.randint(100, 200)
        self.height = random.randint(50, 100)
        self.x = random.randint(-self.width, WIDTH + self.width)
        self.y = random.randint(50, HEIGHT // 3)
        self.speed = random.uniform(0.2, 0.8)
        self.color = (255, 255, 255, random.randint(100, 180))

    def update(self):
        self.x += self.speed
        if self.x > WIDTH + self.width:
            self.x = -self.width

    def draw(self, surface):
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(s, self.color, (0, 0, self.width, self.height))
        surface.blit(s, (int(self.x), int(self.y)))


# Toggle button for on/off settings
class ToggleButton:
    def __init__(self, x, y, width, height, text, is_on=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_on = is_on
        self.font = pygame.font.Font(None, 28)

    def draw(self, surface):
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(midright=(self.rect.x - 10, self.rect.centery))
        surface.blit(text_surface, text_rect)

        # Draw toggle background
        bg_color = (80, 80, 80)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.rect.height // 2)

        # Draw toggle indicator
        if self.is_on:
            indicator_color = (100, 255, 100)
            indicator_rect = pygame.Rect(self.rect.x + self.rect.width // 2, self.rect.y + 2,
                                         self.rect.width // 2 - 4, self.rect.height - 4)
        else:
            indicator_color = (255, 100, 100)
            indicator_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                         self.rect.width // 2 - 4, self.rect.height - 4)

        pygame.draw.rect(surface, indicator_color, indicator_rect, border_radius=indicator_rect.height // 2)

        # Draw text on indicator
        status_text = "ON" if self.is_on else "OFF"
        status_surface = self.font.render(status_text, True, BLACK)
        status_rect = status_surface.get_rect(center=indicator_rect.center)
        surface.blit(status_surface, status_rect)

    def is_clicked(self, mouse_pos, mouse_click):
        if self.rect.collidepoint(mouse_pos) and mouse_click:
            self.is_on = not self.is_on
            return True
        return False


# Game States
MAIN_MENU = 0
GAME_MODE_SELECT = 1
CHARACTER_SELECT = 2
PLAYING = 3
GAME_OVER = 4
PAUSE_MENU = 5
OPTIONS_MENU = 6
current_game_state = MAIN_MENU

# Debug mode flag
DEBUG_MODE = False

# Sprite Groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
effects = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player1_group = pygame.sprite.GroupSingle()
player2_group = pygame.sprite.GroupSingle()
particles = []
clouds = []

# Create some clouds for the background
for _ in range(10):
    clouds.append(Cloud())

# Controls with added special attack button
controls1 = {
    'left': pygame.K_a,
    'right': pygame.K_d,
    'jump': pygame.K_w,
    'attack': pygame.K_SPACE,
    'special': pygame.K_s
}

controls2 = {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'jump': pygame.K_UP,
    'attack': pygame.K_RETURN,
    'special': pygame.K_DOWN
}

# Players
player1 = Samurai(100, HEIGHT - 100, controls1, player1_idle, player1_run, player1_attack, player1_jump, player1_hurt,
                  "Samurai Red")
player2 = Samurai(700, HEIGHT - 100, controls2, player2_idle, player2_run, player2_attack, player2_jump, player2_hurt,
                  "Samurai Blue")
player1_group.add(player1)
player2_group.add(player2)
all_sprites.add(player1, player2)

# Expanded platform layout with different types
platform_data = [
    (0, HEIGHT - 30, WIDTH * 2, 30, "normal"),  # Ground
    (200, HEIGHT - 150, 150, 20, "stone"),  # Platform 1
    (500, HEIGHT - 200, 100, 20, "normal"),  # Platform 2
    (700, HEIGHT - 250, 120, 20, "stone"),  # Platform 3
    (300, HEIGHT - 300, 140, 20, "normal"),  # Platform 4
    (100, HEIGHT - 400, 80, 20, "ice"),  # High platform
    (900, HEIGHT - 350, 90, 20, "normal"),  # Far platform
    (400, HEIGHT - 450, 60, 20, "stone"),  # Highest platform
]

# Add lava platforms based on difficulty
if ai_difficulty == AIDifficulty.HARD:
    platform_data.extend([
        (600, HEIGHT - 120, 100, 10, "lava"),
        (250, HEIGHT - 250, 80, 10, "lava")
    ])

for x, y, w, h, platform_type in platform_data:
    platform = Platform(x, y, w, h, platform_type)
    platforms.add(platform)
    all_sprites.add(platform)

# Font
title_font = pygame.font.Font(None, 80)
heading_font = pygame.font.Font(None, 60)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


def create_particles(x, y, count=10, color=(255, 255, 0), speed=1):
    for _ in range(count):
        particles.append(Particle(x, y, color, speed))


def draw_text(surface, text, font, x, y, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def draw_pixelated_text(surface, text, font, x, y, color, shadow_color=None):
    # Create main text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    # Create shadow if a shadow color is provided
    if shadow_color:
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect(center=(x + 3, y + 3))
        surface.blit(shadow_surface, shadow_rect)

    # Draw the main text
    surface.blit(text_surface, text_rect)


def spawn_powerup():
    # Random chance to spawn a powerup
    if random.random() < 0.01:  # 1% chance each frame
        # Choose a random location above platforms
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 200)

        # Choose a powerup type
        powerup_types = ["health", "shield", "speed", "special"]
        weights = [0.4, 0.3, 0.2, 0.1]  # Weighted probabilities
        powerup_type = random.choices(powerup_types, weights=weights)[0]

        powerup = PowerUp(x, y, powerup_type)
        powerups.add(powerup)
        all_sprites.add(powerup)


def show_main_menu():
    # Create menu buttons
    start_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60, "Start Game", (100, 50, 200), (150, 100, 250))
    options_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 60, "Options", (100, 50, 200), (150, 100, 250))
    quit_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 120, 300, 60, "Quit", (100, 50, 200), (150, 100, 250))

    # Background with parallax scrolling elements
    menu_bg_offset = 0

    running = True
    while running:
        # Clear screen with a dark blue background
        screen.fill((20, 20, 50))

        # Draw scrolling background elements
        menu_bg_offset = (menu_bg_offset + 0.5) % WIDTH

        # Draw clouds
        for cloud in clouds:
            cloud.update()
            cloud.draw(screen)

        # Draw mountains in the background with parallax effect
        for i in range(3):
            pygame.draw.rect(screen, (40 + i * 20, 40 + i * 10, 60 + i * 15),
                             (0, HEIGHT - 300 + i * 100, WIDTH, 300 - i * 100))

            # Add mountain silhouettes
            for x in range(-100 + int(menu_bg_offset * (0.2 + i * 0.1)) % 300, WIDTH, 300):
                height = 100 + i * 30
                points = [(x, HEIGHT - 300 + i * 100),
                          (x + 50, HEIGHT - 300 - height + i * 100),
                          (x + 100, HEIGHT - 300 - height // 2 + i * 100),
                          (x + 150, HEIGHT - 300 - height // 1.5 + i * 100),
                          (x + 200, HEIGHT - 300 + i * 100)]
                pygame.draw.polygon(screen, (30 + i * 10, 30 + i * 5, 50 + i * 10), points)

        # Create starry background
        for _ in range(5):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT // 2)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

        # Draw title with pixel style and shadow
        draw_pixelated_text(screen, "PIXEL SAMURAI DUEL", title_font, WIDTH // 2, HEIGHT // 4,
                            (255, 255, 255), (100, 0, 150))

        # Draw subtitle
        draw_pixelated_text(screen, "A Two-Player Battle for Pixel Glory!", font, WIDTH // 2, HEIGHT // 4 + 70,
                            (200, 200, 255))

        # Get mouse position and button state
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Toggle debug mode with F3
                if event.key == pygame.K_F3:
                    global DEBUG_MODE
                    DEBUG_MODE = not DEBUG_MODE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Check button interactions
        start_button.check_hover(mouse_pos)
        options_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        if start_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return GAME_MODE_SELECT
        if options_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return OPTIONS_MENU
        if quit_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            pygame.quit()
            sys.exit()

        # Draw buttons
        start_button.draw(screen)
        options_button.draw(screen)
        quit_button.draw(screen)

        # Draw sound toggle
        sound_img = sound_on_img if sound_enabled else sound_off_img
        screen.blit(sound_img, (WIDTH - 50, 30))

        # Draw version and credits
        draw_text(screen, "v1.0.0", small_font, WIDTH - 50, HEIGHT - 30, (150, 150, 150))
        draw_text(screen, "© 2023 Pixel Samurai Studios", small_font, WIDTH // 2, HEIGHT - 30, (150, 150, 150))

        # Add visual effects - particles at the bottom
        if random.random() < 0.1:
            create_particles(random.randint(0, WIDTH), HEIGHT - 10,
                             color=(random.randint(100, 255), random.randint(50, 150), random.randint(150, 255)))

        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
            else:
                particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return MAIN_MENU


def show_options_menu():
    global sound_enabled, current_game_mode, ai_difficulty

    # Create menu buttons
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 60, "Back", (100, 50, 100), (150, 70, 120))

    # Create toggle buttons
    sound_toggle = ToggleButton(WIDTH // 2 + 100, HEIGHT // 3, 100, 40, "Sound:", sound_enabled)

    # Create difficulty selection
    difficulty_options = ["Easy", "Medium", "Hard"]
    difficulty_buttons = []

    for i, diff in enumerate(difficulty_options):
        btn_x = WIDTH // 2 - 150 + i * 150
        btn_y = HEIGHT // 2
        color = (100, 255, 100) if i == 0 else (255, 255, 100) if i == 1 else (255, 100, 100)
        hover_color = (150, 255, 150) if i == 0 else (255, 255, 150) if i == 1 else (255, 150, 150)
        btn = Button(btn_x, btn_y, 120, 50, diff, color, hover_color)
        difficulty_buttons.append(btn)

    # Currently selected difficulty
    current_difficulty = 1  # Medium by default
    if ai_difficulty == AIDifficulty.EASY:
        current_difficulty = 0
    elif ai_difficulty == AIDifficulty.HARD:
        current_difficulty = 2

    running = True
    while running:
        # Draw background with gradients
        screen.fill((30, 30, 60))

        # Draw decorative elements
        for y in range(0, HEIGHT, 20):
            color_value = 40 + (y % 40) // 20 * 20
            pygame.draw.line(screen, (color_value, color_value, color_value + 30),
                             (0, y), (WIDTH, y), 1)

        # Draw title
        draw_pixelated_text(screen, "OPTIONS", heading_font, WIDTH // 2, 100, WHITE, (100, 0, 100))

        # Draw sound toggle section
        draw_text(screen, "Game Settings", font, WIDTH // 2, HEIGHT // 3 - 60, (200, 200, 255))
        pygame.draw.line(screen, (100, 100, 200), (WIDTH // 4, HEIGHT // 3 - 30),
                         (WIDTH * 3 // 4, HEIGHT // 3 - 30), 2)

        # Draw difficulty section
        draw_text(screen, "AI Difficulty", font, WIDTH // 2, HEIGHT // 2 - 60, (200, 200, 255))
        pygame.draw.line(screen, (100, 100, 200), (WIDTH // 4, HEIGHT // 2 - 30),
                         (WIDTH * 3 // 4, HEIGHT // 2 - 30), 2)

        # Get mouse position and button state
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MAIN_MENU
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Handle button interactions
        back_button.check_hover(mouse_pos)

        if back_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return MAIN_MENU

        # Handle sound toggle
        if sound_toggle.is_clicked(mouse_pos, mouse_clicked):
            sound_enabled = sound_toggle.is_on
            if sound_enabled:
                music.play(-1)
            else:
                pygame.mixer.stop()

        # Handle difficulty buttons
        for i, btn in enumerate(difficulty_buttons):
            btn.check_hover(mouse_pos)
            if btn.is_clicked(mouse_pos, mouse_clicked):
                current_difficulty = i
                if i == 0:
                    ai_difficulty = AIDifficulty.EASY
                elif i == 1:
                    ai_difficulty = AIDifficulty.MEDIUM
                else:
                    ai_difficulty = AIDifficulty.HARD
                if sound_enabled:
                    menu_select_sound.play()

        # Draw all elements
        sound_toggle.draw(screen)
        back_button.draw(screen)

        # Draw difficulty buttons with highlight for selected one
        for i, btn in enumerate(difficulty_buttons):
            # Draw with extra highlight if selected
            if i == current_difficulty:
                highlight_rect = pygame.Rect(btn.rect.x - 5, btn.rect.y - 5,
                                             btn.rect.width + 10, btn.rect.height + 10)
                pygame.draw.rect(screen, (255, 255, 255), highlight_rect, 3, border_radius=5)
            btn.draw(screen)

        # Draw difficulty description
        difficulty_desc = ""
        if current_difficulty == 0:
            difficulty_desc = "Easy: AI moves slower and attacks less frequently"
        elif current_difficulty == 1:
            difficulty_desc = "Medium: AI has balanced movement and attack patterns"
        else:
            difficulty_desc = "Hard: AI moves faster, attacks more accurately and aggressively"

        draw_text(screen, difficulty_desc, small_font, WIDTH // 2, HEIGHT // 2 + 80, (200, 200, 200))

        # Add visual effects
        if random.random() < 0.05:
            create_particles(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                             color=(random.randint(100, 200), random.randint(100, 200), random.randint(200, 255)),
                             speed=0.5)

        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
            else:
                particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return MAIN_MENU


def show_game_mode_select():
    """Show screen to select game mode: PvP or PvComputer"""
    global current_game_mode, ai_difficulty

    pvp_button = Button(WIDTH // 2 - 200, HEIGHT // 2 - 50, 400, 70,
                        "Player vs Player", (100, 50, 200), (150, 100, 250))
    pvc_button = Button(WIDTH // 2 - 200, HEIGHT // 2 + 50, 400, 70,
                        "Player vs Computer", (100, 50, 200), (150, 100, 250))
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50,
                         "Back", (150, 50, 50), (200, 100, 100))

    # AI difficulty selection buttons (only shown when PvC is selected)
    easy_button = Button(WIDTH // 2 - 300, HEIGHT // 2 + 150, 180, 50, "Easy", (50, 150, 50), (100, 200, 100))
    medium_button = Button(WIDTH // 2 - 90, HEIGHT // 2 + 150, 180, 50, "Medium", (150, 150, 50), (200, 200, 100))
    hard_button = Button(WIDTH // 2 + 120, HEIGHT // 2 + 150, 180, 50, "Hard", (150, 50, 50), (200, 100, 100))

    # Animation variables
    title_bounce = 0
    bounce_dir = 1

    show_difficulty = False

    running = True
    while running:
        # Background
        screen.fill((20, 30, 60))

        # Animated background elements
        for i in range(30):
            y_pos = (i * 25 + pygame.time.get_ticks() // 50) % HEIGHT
            color_value = 40 + (i % 3) * 20
            pygame.draw.line(screen, (color_value, color_value, color_value + 40),
                             (0, y_pos), (WIDTH, y_pos), 2)

        # Title animation
        title_bounce += 0.1 * bounce_dir
        if abs(title_bounce) > 5:
            bounce_dir *= -1

        # Draw title with bounce effect
        draw_pixelated_text(screen, "SELECT GAME MODE", heading_font,
                            WIDTH // 2, HEIGHT // 4 + title_bounce,
                            (255, 255, 255), (100, 0, 150))

        # Get mouse position and button state
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MAIN_MENU
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Check button interactions
        pvp_button.check_hover(mouse_pos)
        pvc_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)

        if show_difficulty:
            easy_button.check_hover(mouse_pos)
            medium_button.check_hover(mouse_pos)
            hard_button.check_hover(mouse_pos)

            if easy_button.is_clicked(mouse_pos, mouse_clicked):
                if sound_enabled:
                    menu_select_sound.play()
                ai_difficulty = AIDifficulty.EASY
                return CHARACTER_SELECT
            if medium_button.is_clicked(mouse_pos, mouse_clicked):
                if sound_enabled:
                    menu_select_sound.play()
                ai_difficulty = AIDifficulty.MEDIUM
                return CHARACTER_SELECT
            if hard_button.is_clicked(mouse_pos, mouse_clicked):
                if sound_enabled:
                    menu_select_sound.play()
                ai_difficulty = AIDifficulty.HARD
                return CHARACTER_SELECT

        if pvp_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            current_game_mode = GameMode.PLAYER_VS_PLAYER
            return CHARACTER_SELECT

        if pvc_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            current_game_mode = GameMode.PLAYER_VS_COMPUTER
            show_difficulty = True

        if back_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return MAIN_MENU

        # Draw buttons
        pvp_button.draw(screen)
        pvc_button.draw(screen)
        back_button.draw(screen)

        # Draw difficulty buttons if needed
        if show_difficulty:
            pygame.draw.rect(screen, (0, 0, 0, 150), (WIDTH // 2 - 320, HEIGHT // 2 + 130, 640, 80), border_radius=10)
            draw_text(screen, "Select Difficulty:", font, WIDTH // 2, HEIGHT // 2 + 120, WHITE)
            easy_button.draw(screen)
            medium_button.draw(screen)
            hard_button.draw(screen)

            # Show difficulty descriptions on hover
            if easy_button.hovered:
                draw_text(screen, "Easy: Slower AI with less accuracy", small_font,
                          WIDTH // 2, HEIGHT - 150, (200, 255, 200))
            elif medium_button.hovered:
                draw_text(screen, "Medium: Balanced AI difficulty", small_font,
                          WIDTH // 2, HEIGHT - 150, (255, 255, 200))
            elif hard_button.hovered:
                draw_text(screen, "Hard: Fast, aggressive AI with high accuracy", small_font,
                          WIDTH // 2, HEIGHT - 150, (255, 200, 200))
        else:
            # Mode descriptions on hover
            if pvp_button.hovered:
                draw_text(screen, "Battle against a friend in two-player mode", small_font,
                          WIDTH // 2, HEIGHT - 150, (200, 200, 255))
            elif pvc_button.hovered:
                draw_text(screen, "Battle against the computer with adjustable difficulty", small_font,
                          WIDTH // 2, HEIGHT - 150, (200, 200, 255))
            else:
                draw_text(screen, "Choose your game mode", small_font, WIDTH // 2, HEIGHT - 150, (200, 200, 255))

        # Add visual effects
        if random.random() < 0.05:
            create_particles(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                             color=(random.randint(100, 200), random.randint(100, 200), random.randint(200, 255)),
                             speed=0.5)

        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
            else:
                particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return MAIN_MENU


def show_character_select():
    # Simple character selection screen
    player1_ready = False
    player2_ready = False

    # Character options - could be expanded with more characters and stats
    characters = [
        {"name": "Red Samurai", "health": 100, "speed": 6, "power": 8, "color": (255, 50, 50)},
        {"name": "Blue Ninja", "health": 80, "speed": 8, "power": 6, "color": (50, 50, 255)},
        {"name": "Green Ronin", "health": 120, "speed": 5, "power": 9, "color": (50, 200, 50)},
    ]

    p1_selection = 0
    p2_selection = 1

    running = True
    while running:
        # Draw background
        screen.fill((30, 30, 60))

        # Draw title
        draw_pixelated_text(screen, "CHARACTER SELECT", heading_font, WIDTH // 2, 70, WHITE, (100, 0, 100))

        # Player 1 selection
        p1_x = WIDTH // 4
        draw_text(screen, "PLAYER 1", font, p1_x, 150, (255, 100, 100))

        # Character display area for Player 1
        pygame.draw.rect(screen, (50, 50, 80), (p1_x - 120, 180, 240, 300))
        pygame.draw.rect(screen, characters[p1_selection]["color"], (p1_x - 100, 200, 200, 200))
        draw_text(screen, characters[p1_selection]["name"], font, p1_x, 430, WHITE)

        # Stats for Player 1's character
        draw_text(screen, f"Health: {characters[p1_selection]['health']}", small_font, p1_x, 470, WHITE)
        draw_text(screen, f"Speed: {characters[p1_selection]['speed']}", small_font, p1_x, 500, WHITE)
        draw_text(screen, f"Power: {characters[p1_selection]['power']}", small_font, p1_x, 530, WHITE)

        # Selection arrows
        if not player1_ready:
            draw_text(screen, "<", font, p1_x - 140, 300, WHITE)
            draw_text(screen, ">", font, p1_x + 140, 300, WHITE)
            draw_text(screen, "Press W to select", small_font, p1_x, 570, (200, 200, 200))
        else:
            draw_text(screen, "READY!", font, p1_x, 570, (100, 255, 100))

        # For PvP mode, show Player 2 selection
        if current_game_mode == GameMode.PLAYER_VS_PLAYER:
            p2_x = WIDTH * 3 // 4
            draw_text(screen, "PLAYER 2", font, p2_x, 150, (100, 100, 255))

            # Character display area for Player 2
            pygame.draw.rect(screen, (50, 50, 80), (p2_x - 120, 180, 240, 300))
            pygame.draw.rect(screen, characters[p2_selection]["color"], (p2_x - 100, 200, 200, 200))
            draw_text(screen, characters[p2_selection]["name"], font, p2_x, 430, WHITE)

            # Stats for Player 2's character
            draw_text(screen, f"Health: {characters[p2_selection]['health']}", small_font, p2_x, 470, WHITE)
            draw_text(screen, f"Speed: {characters[p2_selection]['speed']}", small_font, p2_x, 500, WHITE)
            draw_text(screen, f"Power: {characters[p2_selection]['power']}", small_font, p2_x, 530, WHITE)

            # Selection arrows
            if not player2_ready:
                draw_text(screen, "<", font, p2_x - 140, 300, WHITE)
                draw_text(screen, ">", font, p2_x + 140, 300, WHITE)
                draw_text(screen, "Press Up Arrow to select", small_font, p2_x, 570, (200, 200, 200))
            else:
                draw_text(screen, "READY!", font, p2_x, 570, (100, 255, 100))
        else:
            # For PvC mode, show CPU selection
            p2_x = WIDTH * 3 // 4
            draw_text(screen, "COMPUTER", font, p2_x, 150, (100, 100, 255))

            # CPU uses a random character
            cpu_selection = (p1_selection + 1) % len(characters)  # Ensure different from player

            # Character display area for CPU
            pygame.draw.rect(screen, (50, 50, 80), (p2_x - 120, 180, 240, 300))
            pygame.draw.rect(screen, characters[cpu_selection]["color"], (p2_x - 100, 200, 200, 200))
            draw_text(screen, characters[cpu_selection]["name"], font, p2_x, 430, WHITE)

            # Stats for CPU's character
            draw_text(screen, f"Health: {characters[cpu_selection]['health']}", small_font, p2_x, 470, WHITE)
            draw_text(screen, f"Speed: {characters[cpu_selection]['speed']}", small_font, p2_x, 500, WHITE)
            draw_text(screen, f"Power: {characters[cpu_selection]['power']}", small_font, p2_x, 530, WHITE)

            # Show AI difficulty
            ai_difficulty_text = f"AI Difficulty: {ai_difficulty.name}"
            draw_text(screen, ai_difficulty_text, small_font, p2_x, 600, (150, 200, 255))

            draw_text(screen, "CPU OPPONENT", font, p2_x, 570, (100, 180, 255))
            player2_ready = True  # CPU is always ready
            p2_selection = cpu_selection

        # Bottom instructions
        if current_game_mode == GameMode.PLAYER_VS_PLAYER:
            if player1_ready and player2_ready:
                draw_text(screen, "Press SPACE to start the battle!", font, WIDTH // 2, HEIGHT - 100, (255, 255, 0))
            else:
                draw_text(screen, "Both players must select their characters", font, WIDTH // 2, HEIGHT - 100,
                          (200, 200, 200))
        else:
            if player1_ready:
                draw_text(screen, "Press SPACE to start the battle!", font, WIDTH // 2, HEIGHT - 100, (255, 255, 0))
            else:
                draw_text(screen, "Select your character", font, WIDTH // 2, HEIGHT - 100, (200, 200, 200))

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GAME_MODE_SELECT

                # Player 1 controls
                if not player1_ready:
                    if event.key == pygame.K_a:  # Left
                        p1_selection = (p1_selection - 1) % len(characters)
                        if sound_enabled:
                            menu_select_sound.play()
                    elif event.key == pygame.K_d:  # Right
                        p1_selection = (p1_selection + 1) % len(characters)
                        if sound_enabled:
                            menu_select_sound.play()
                    elif event.key == pygame.K_w:  # Select
                        player1_ready = True
                        if sound_enabled:
                            menu_select_sound.play()
                elif event.key == pygame.K_s:  # Cancel selection
                    player1_ready = False

                # Player 2 controls (only in PvP mode)
                if current_game_mode == GameMode.PLAYER_VS_PLAYER and not player2_ready:
                    if event.key == pygame.K_LEFT:
                        p2_selection = (p2_selection - 1) % len(characters)
                        if sound_enabled:
                            menu_select_sound.play()
                    elif event.key == pygame.K_RIGHT:
                        p2_selection = (p2_selection + 1) % len(characters)
                        if sound_enabled:
                            menu_select_sound.play()
                    elif event.key == pygame.K_UP:
                        player2_ready = True
                        if sound_enabled:
                            menu_select_sound.play()
                elif event.key == pygame.K_DOWN and current_game_mode == GameMode.PLAYER_VS_PLAYER:
                    player2_ready = False

                # Start game when ready
                if ((current_game_mode == GameMode.PLAYER_VS_PLAYER and player1_ready and player2_ready) or
                    (
                            current_game_mode == GameMode.PLAYER_VS_COMPUTER and player1_ready)) and event.key == pygame.K_SPACE:
                    # Apply character stats before starting
                    global player1, player2
                    player1.player_name = characters[p1_selection]["name"]
                    player2.player_name = characters[p2_selection]["name"]

                    # Set player 2 as AI if in PvC mode
                    if current_game_mode == GameMode.PLAYER_VS_COMPUTER:
                        player2.is_ai = True
                        player2.ai_target = player1
                        player2.ai_difficulty = ai_difficulty
                    else:
                        player2.is_ai = False
                        player2.ai_target = None

                    reset_game()
                    return PLAYING

        # Add some visual flair - random particles
        if random.random() < 0.05:
            x = random.choice([p1_x, p2_x])
            create_particles(x, 200, color=characters[p1_selection if x == p1_x else p2_selection]["color"])

        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
            else:
                particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return GAME_MODE_SELECT


def show_game_stats(player1, player2):
    """Show game statistics at the end of a match"""
    stats_surface = pygame.Surface((WIDTH - 200, HEIGHT - 200), pygame.SRCALPHA)
    stats_surface.fill((0, 0, 50, 230))

    stats_rect = stats_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Draw border
    pygame.draw.rect(stats_surface, (100, 100, 255), (0, 0, stats_rect.width, stats_rect.height), 4, border_radius=10)

    # Draw title
    draw_text(stats_surface, "MATCH STATISTICS", heading_font, stats_rect.width // 2, 40, WHITE)

    # Draw line separator
    pygame.draw.line(stats_surface, (100, 100, 255), (50, 80), (stats_rect.width - 50, 80), 2)

    # Column headers
    draw_text(stats_surface, "Stat", font, stats_rect.width // 4, 120, (200, 200, 255))
    draw_text(stats_surface, player1.player_name, font, stats_rect.width // 2, 120, (255, 100, 100))
    draw_text(stats_surface, player2.player_name, font, stats_rect.width * 3 // 4, 120, (100, 100, 255))

    # Draw stats rows
    stats_data = [
        ("Health Remaining", f"{player1.health}%", f"{player2.health}%"),
        ("Hits Landed", str(player1.hits_landed), str(player2.hits_landed)),
        ("Damage Dealt", str(player1.damage_dealt), str(player2.damage_dealt)),
        ("Jumps Made", str(player1.jumps_made), str(player2.jumps_made)),
        ("Special Attacks", str(player1.specials_used), str(player2.specials_used))
    ]

    for i, (label, p1_val, p2_val) in enumerate(stats_data):
        y_pos = 170 + i * 50
        draw_text(stats_surface, label, font, stats_rect.width // 4, y_pos, WHITE)
        draw_text(stats_surface, p1_val, font, stats_rect.width // 2, y_pos, WHITE)
        draw_text(stats_surface, p2_val, font, stats_rect.width * 3 // 4, y_pos, WHITE)

    # Draw press any key message
    draw_text(stats_surface, "Press any key to continue", small_font, stats_rect.width // 2, stats_rect.height - 40,
              (200, 200, 200))

    # Draw to screen
    screen.blit(stats_surface, stats_rect.topleft)
    pygame.display.flip()

    # Wait for keypress
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                if sound_enabled:
                    menu_select_sound.play()


def show_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    winner = "Player 1" if player2.health <= 0 else "Player 2"
    winner_name = player1.player_name if player2.health <= 0 else player2.player_name
    loser = player2 if player2.health <= 0 else player1

    # Show match statistics first
    show_game_stats(player1, player2)

    # Clear screen for victory screen
    screen.blit(overlay, (0, 0))

    # Victory announcement with special effects
    draw_pixelated_text(screen, f"{winner} Wins!", heading_font, WIDTH // 2, HEIGHT // 3 - 40,
                        (255, 255, 0), (150, 100, 0))
    draw_pixelated_text(screen, winner_name, font, WIDTH // 2, HEIGHT // 3 + 20, WHITE)

    # Create buttons
    rematch_button = Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "Rematch", (100, 50, 200), (150, 100, 250))
    menu_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, "Main Menu", (100, 50, 200), (150, 100, 250))
    quit_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 160, 300, 60, "Quit", (100, 50, 200), (150, 100, 250))

    # Victory particles
    for _ in range(50):
        create_particles(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2),
                         color=(255, 215, 0), speed=0.5)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MAIN_MENU
                elif event.key == pygame.K_SPACE:
                    reset_game()
                    return PLAYING
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Check button interactions
        rematch_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        if rematch_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            reset_game()
            return PLAYING
        if menu_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return MAIN_MENU
        if quit_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            pygame.quit()
            sys.exit()

        # Draw buttons
        rematch_button.draw(screen)
        menu_button.draw(screen)
        quit_button.draw(screen)

        # Continue creating victory particles
        if random.random() < 0.1:
            create_particles(random.randint(WIDTH // 3, 2 * WIDTH // 3),
                             HEIGHT // 3, color=(255, 215, 0))

        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
            else:
                particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return MAIN_MENU


def show_pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))

    draw_pixelated_text(screen, "PAUSED", heading_font, WIDTH // 2, HEIGHT // 3, WHITE, (100, 0, 100))

    # Create buttons
    resume_button = Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "Resume", (100, 50, 200), (150, 100, 250))
    options_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, "Options", (100, 50, 200), (150, 100, 250))
    menu_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 160, 300, 60, "Main Menu", (100, 50, 200), (150, 100, 250))

    # Create sound toggle
    sound_toggle = ToggleButton(WIDTH // 2 + 100, HEIGHT // 2 + 240, 100, 40, "Sound:", sound_enabled)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    return PLAYING
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Check button interactions
        resume_button.check_hover(mouse_pos)
        options_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)

        if resume_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return PLAYING

        if options_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return OPTIONS_MENU

        if menu_button.is_clicked(mouse_pos, mouse_clicked):
            if sound_enabled:
                menu_select_sound.play()
            return MAIN_MENU



        # Draw buttons
        resume_button.draw(screen)
        options_button.draw(screen)
        menu_button.draw(screen)
        sound_toggle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return PLAYING


def reset_game():
    global all_sprites, platforms, player1, player2, player1_group, player2_group, effects, powerups, bg_scroll, particles

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    effects = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # Create players based on game mode
    player1 = Samurai(100, HEIGHT - 100, controls1, player1_idle, player1_run, player1_attack, player1_jump,
                      player1_hurt, player1.player_name)

    if current_game_mode == GameMode.PLAYER_VS_COMPUTER:
        player2 = Samurai(700, HEIGHT - 100, controls2, player2_idle, player2_run, player2_attack, player2_jump,
                          player2_hurt, player2.player_name, is_ai=True)
        player2.ai_target = player1
        player2.ai_difficulty = ai_difficulty
    else:
        player2 = Samurai(700, HEIGHT - 100, controls2, player2_idle, player2_run, player2_attack, player2_jump,
                          player2_hurt, player2.player_name, is_ai=False)

    player1_group = pygame.sprite.GroupSingle(player1)
    player2_group = pygame.sprite.GroupSingle(player2)
    all_sprites.add(player1, player2)
    particles = []

    # Add lava platforms based on difficulty
    platform_data_adjusted = platform_data.copy()

    if ai_difficulty == AIDifficulty.HARD:
        platform_data_adjusted.extend([
            (600, HEIGHT - 120, 100, 10, "lava"),
            (250, HEIGHT - 250, 80, 10, "lava")
        ])

    for x, y, w, h, platform_type in platform_data_adjusted:
        platform = Platform(x, y, w, h, platform_type)
        platforms.add(platform)
        all_sprites.add(platform)

    bg_scroll = 0


# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and current_game_state == PLAYING:
                current_game_state = PAUSE_MENU
            elif event.key == pygame.K_p and current_game_state == PLAYING:
                current_game_state = PAUSE_MENU

            # Toggle sound with M key
            elif event.key == pygame.K_m:
                sound_enabled = not sound_enabled
                if sound_enabled:
                    music.play(-1)
                else:
                    pygame.mixer.stop()

            # Toggle debug mode with F3
            elif event.key == pygame.K_F3:
                DEBUG_MODE = not DEBUG_MODE

    keys = pygame.key.get_pressed()

    if current_game_state == MAIN_MENU:
        current_game_state = show_main_menu()

    elif current_game_state == OPTIONS_MENU:
        current_game_state = show_options_menu()

    elif current_game_state == GAME_MODE_SELECT:
        current_game_state = show_game_mode_select()

    elif current_game_state == CHARACTER_SELECT:
        current_game_state = show_character_select()

    elif current_game_state == PLAYING:
        # Handle Player Input and Actions
        player1.handle_keys(keys, effects)
        player1.apply_gravity()
        player1.handle_collision(platforms)

        if not player2.is_ai:  # Only process keyboard input for player 2 if not AI
            player2.handle_keys(keys, effects)
        player2.apply_gravity()
        player2.handle_collision(platforms)

        # Background Scrolling
        bg_scroll = (bg_scroll + 1) % background_rect.width

        # Random powerup spawning
        spawn_powerup()

        # Update Sprites
        all_sprites.update(0)
        effects.update(0)
        powerups.update(0)

        # Projectile Collisions for player 1
        for projectile in player1.projectiles:
            if pygame.sprite.spritecollide(projectile, player2_group, False):
                player2.take_damage(projectile.damage, player1)
                projectile.kill()
                # Create hit effect
                hit_effect = Effect(projectile.rect.centerx, projectile.rect.centery, explosion_imgs, 0.3)
                effects.add(hit_effect)
                # Create particles
                create_particles(projectile.rect.centerx, projectile.rect.centery, 15, (255, 200, 0))

        # Projectile Collisions for player 2
        for projectile in player2.projectiles:
            if pygame.sprite.spritecollide(projectile, player1_group, False):
                player1.take_damage(projectile.damage, player2)
                projectile.kill()
                # Create hit effect
                hit_effect = Effect(projectile.rect.centerx, projectile.rect.centery, explosion_imgs, 0.3)
                effects.add(hit_effect)
                # Create particles
                create_particles(projectile.rect.centerx, projectile.rect.centery, 15, (255, 200, 0))

        # Powerup collisions
        for powerup in pygame.sprite.spritecollide(player1, powerups, True):
            message = powerup.apply_effect(player1)
            # Create effect
            create_particles(powerup.rect.centerx, powerup.rect.centery, 20, (255, 255, 200))
            if sound_enabled:
                menu_select_sound.play()

        for powerup in pygame.sprite.spritecollide(player2, powerups, True):
            message = powerup.apply_effect(player2)
            # Create effect
            create_particles(powerup.rect.centerx, powerup.rect.centery, 20, (255, 255, 200))
            if sound_enabled:
                menu_select_sound.play()

        # Check for game over condition
        if player1.health <= 0 or player2.health <= 0:
            current_game_state = GAME_OVER

        # Draw everything
        screen.blit(background_img, (-bg_scroll, 0))
        screen.blit(background_img, (-bg_scroll + background_rect.width, 0))

        for cloud in clouds:
            cloud.update()
            cloud.draw(screen)

        for entity in all_sprites:
            entity.draw(screen)

        for effect in effects:
            effect.draw(screen)

        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
            else:
                particle.draw(screen)

        # Draw UI elements
        # Player 1 info panel
        pygame.draw.rect(screen, (0, 0, 0, 150), (10, 10, 250, 80), border_radius=5)
        draw_text(screen, player1.player_name, font, 135, 25, (255, 100, 100))
        draw_text(screen, f"Health: {player1.health}", font, 135, 55, WHITE)
        pygame.draw.rect(screen, (50, 50, 80), (10, 80, 250, 15), border_radius=3)
        special_width = (player1.special_meter / player1.max_special) * 250
        special_color = BLUE if not player1.special_ready else GOLD
        pygame.draw.rect(screen, special_color, (10, 80, special_width, 15), border_radius=3)

        # Player 2 info panel
        pygame.draw.rect(screen, (0, 0, 0, 150), (WIDTH - 260, 10, 250, 80), border_radius=5)
        draw_text(screen, player2.player_name, font, WIDTH - 135, 25, (100, 100, 255))
        draw_text(screen, f"Health: {player2.health}", font, WIDTH - 135, 55, WHITE)
        pygame.draw.rect(screen, (50, 50, 80), (WIDTH - 260, 80, 250, 15), border_radius=3)
        special_width = (player2.special_meter / player2.max_special) * 250
        special_color = BLUE if not player2.special_ready else GOLD
        pygame.draw.rect(screen, special_color, (WIDTH - 260, 80, special_width, 15), border_radius=3)

        # Round/Mode indicator
        pygame.draw.rect(screen, (0, 0, 0, 150), (WIDTH // 2 - 100, 10, 200, 40), border_radius=5)
        if current_game_mode == GameMode.PLAYER_VS_PLAYER:
            mode_text = "PvP Battle"
        else:
            mode_text = f"PvC ({ai_difficulty.name})"
        draw_text(screen, mode_text, font, WIDTH // 2, 30, WHITE)

        # Sound icon in corner
        sound_img = sound_on_img if sound_enabled else sound_off_img
        screen.blit(sound_img, (WIDTH - 50, HEIGHT - 50))

        # Debug info if enabled
        if DEBUG_MODE:
            debug_text = [
                f"FPS: {int(clock.get_fps())}",
                f"P1: {player1.ai_state if player1.is_ai else 'Human'}",
                f"P2: {player2.ai_state if player2.is_ai else 'Human'}",
                f"Particles: {len(particles)}",
                f"Powerups: {len(powerups)}"
            ]

            for i, text in enumerate(debug_text):
                debug_surf = small_font.render(text, True, WHITE)
                screen.blit(debug_surf, (10, HEIGHT - 120 + i * 20))

    elif current_game_state == GAME_OVER:
        current_game_state = show_game_over()

    elif current_game_state == PAUSE_MENU:
        current_game_state = show_pause_menu()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
