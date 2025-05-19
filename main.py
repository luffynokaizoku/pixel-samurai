import pygame
import os
import sys
import random
import math

# Initialize Pygame and mixer for sound
pygame.init()
pygame.mixer.init()

# Game Settings
WIDTH, HEIGHT = 1280, 720  # Increased resolution
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

# Screen setup with larger resolution
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Samurai Duel")
clock = pygame.time.Clock()


# Load Images Function with Error Handling
def load_images(folder, scale=1.5):  # Increased scale for larger sprites
    images = []
    try:
        for filename in sorted(os.listdir(folder)):
            if filename.endswith((".png", ".jpg")):
                img = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
                # Scale image to larger size (96x96 pixels)
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
except Exception as e:
    print(f"Error loading images: {e}")
    placeholder = pygame.Surface((96, 96), pygame.SRCALPHA)
    placeholder.fill((255, 0, 255, 100))
    player1_idle = player1_run = player1_attack = player1_jump = player1_hurt = [placeholder]
    player2_idle = player2_run = player2_attack = player2_jump = player2_hurt = [placeholder]
    explosion_imgs = [placeholder]

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
    jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
    attack_sound = pygame.mixer.Sound("assets/sounds/attack.wav")
    hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
    menu_select_sound = pygame.mixer.Sound("assets/sounds/menu_select.wav")
except:
    # Create placeholder silent sounds
    jump_sound = pygame.mixer.Sound(buffer=bytearray(24))
    attack_sound = pygame.mixer.Sound(buffer=bytearray(24))
    hit_sound = pygame.mixer.Sound(buffer=bytearray(24))
    menu_select_sound = pygame.mixer.Sound(buffer=bytearray(24))

# Set volume
jump_sound.set_volume(0.5)
attack_sound.set_volume(0.7)
hit_sound.set_volume(0.8)
menu_select_sound.set_volume(0.6)


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

    def update(self, scroll):
        self.rect.x -= scroll

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing_right, owner):
        super().__init__()
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)
        # Create pixel art projectile
        pygame.draw.ellipse(self.image, (255, 200, 0), (0, 0, 20, 10))
        pygame.draw.ellipse(self.image, (255, 150, 0), (2, 2, 16, 6))
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = facing_right
        self.speed = PROJECTILE_SPEED
        self.original_x = x
        self.owner = owner  # To track who fired the projectile

    def update(self, scroll):
        self.rect.x += self.speed if self.facing_right else -self.speed
        self.rect.x -= scroll
        if abs(self.rect.x - self.original_x) > WIDTH:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class Samurai(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, idle_imgs, run_imgs, attack_imgs, jump_imgs, hurt_imgs, player_name="Player"):
        super().__init__()
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 6  # Slightly increased speed
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
        self.attacking = False
        self.is_attacking = False
        self.facing_right = True
        self.on_ground = False
        self.jump_power = -16
        self.is_jumping = False
        self.is_hurting = False
        self.hurt_timer = 0
        self.attack_cooldown = 25  # Slightly faster cooldown
        self.current_attack_cooldown = 0
        self.projectiles = pygame.sprite.Group()
        self.special_meter = 0  # New special attack meter
        self.max_special = 100
        self.special_ready = False
        self.combo_count = 0
        self.last_hit_time = 0

        # Animation speeds
        self.animation_speed = {
            'idle': 0.15,
            'run': 0.2,
            'attack': 0.3,
            'jump': 0.2,
            'hurt': 0.25
        }

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

                # Triple projectile special attack
                for i in range(-1, 2):
                    projectile_x = self.rect.centerx + (40 if self.facing_right else -40)
                    projectile_y = self.rect.centery + i * 20
                    projectile = Projectile(projectile_x, projectile_y, self.facing_right, self)
                    self.projectiles.add(projectile)
                    all_sprites.add(projectile)

                # Add large flash effect for special attack
                flash = Effect(self.rect.centerx + (50 if self.facing_right else -50),
                               self.rect.centery, explosion_imgs, 0.2)
                effects_group.add(flash)
                attack_sound.play()

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

    def update(self, scroll):
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
                # Sound or visual effect could be added here when special is ready

    def draw(self, surface):
        # Draw character
        surface.blit(self.image, self.rect.topleft)

        # Draw name above character
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(self.player_name, True, WHITE)
        name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.top - 30))
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

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

    def handle_collision(self, platforms):
        collided = False
        for platform in platforms:
            if self.vel_y > 0 and self.rect.colliderect(platform.rect):
                self.rect.bottom = platform.rect.top
                self.y = self.rect.y
                self.vel_y = 0
                self.on_ground = True
                self.is_jumping = False
                collided = True
        if not collided:
            self.on_ground = False

    def take_damage(self, amount, hit_by=None):
        if not self.is_hurting and self.health > 0:
            self.health = max(0, self.health - amount)
            self.is_hurting = True
            self.hurt_timer = pygame.time.get_ticks()
            self.index = 0
            self.current_imgs = self.hurt_imgs
            self.current_animation_speed = self.animation_speed['hurt']
            hit_sound.play()

            # If hit by an opponent, increase their combo and special meter
            if hit_by and isinstance(hit_by, Samurai):
                hit_by.combo_count += 1
                hit_by.last_hit_time = pygame.time.get_ticks()
                hit_by.special_meter = min(hit_by.max_special, hit_by.special_meter + 10)


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


# Game States
MAIN_MENU = 0
CHARACTER_SELECT = 1
PLAYING = 2
GAME_OVER = 3
PAUSE_MENU = 4
current_game_state = MAIN_MENU

# Sprite Groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
effects = pygame.sprite.Group()
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


def show_main_menu():
    # Create menu buttons
    start_button = Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "Start Game", (100, 50, 200), (150, 100, 250))
    options_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, "Options", (100, 50, 200), (150, 100, 250))
    quit_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 160, 300, 60, "Quit", (100, 50, 200), (150, 100, 250))

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Check button interactions
        start_button.check_hover(mouse_pos)
        options_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        if start_button.is_clicked(mouse_pos, mouse_clicked):
            menu_select_sound.play()
            return CHARACTER_SELECT
        if options_button.is_clicked(mouse_pos, mouse_clicked):
            menu_select_sound.play()
            # Options menu could be implemented here
            pass
        if quit_button.is_clicked(mouse_pos, mouse_clicked):
            menu_select_sound.play()
            pygame.quit()
            sys.exit()

        # Draw buttons
        start_button.draw(screen)
        options_button.draw(screen)
        quit_button.draw(screen)

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

        # Player 2 selection
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

        # Bottom instructions
        if player1_ready and player2_ready:
            draw_text(screen, "Press SPACE to start the battle!", font, WIDTH // 2, HEIGHT - 100, (255, 255, 0))
        else:
            draw_text(screen, "Both players must select their characters", font, WIDTH // 2, HEIGHT - 100,
                      (200, 200, 200))

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MAIN_MENU

                # Player 1 controls
                if not player1_ready:
                    if event.key == pygame.K_a:  # Left
                        p1_selection = (p1_selection - 1) % len(characters)
                        menu_select_sound.play()
                    elif event.key == pygame.K_d:  # Right
                        p1_selection = (p1_selection + 1) % len(characters)
                        menu_select_sound.play()
                    elif event.key == pygame.K_w:  # Select
                        player1_ready = True
                        menu_select_sound.play()
                elif event.key == pygame.K_s:  # Cancel selection
                    player1_ready = False

                # Player 2 controls
                if not player2_ready:
                    if event.key == pygame.K_LEFT:
                        p2_selection = (p2_selection - 1) % len(characters)
                        menu_select_sound.play()
                    elif event.key == pygame.K_RIGHT:
                        p2_selection = (p2_selection + 1) % len(characters)
                        menu_select_sound.play()
                    elif event.key == pygame.K_UP:
                        player2_ready = True
                        menu_select_sound.play()
                elif event.key == pygame.K_DOWN:
                    player2_ready = False

                # Start game when both ready
                if player1_ready and player2_ready and event.key == pygame.K_SPACE:
                    # Could apply character stats here before starting the game
                    player1.player_name = characters[p1_selection]["name"]
                    player2.player_name = characters[p2_selection]["name"]
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

    return MAIN_MENU


def show_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    winner = "Player 1" if player2.health <= 0 else "Player 2"
    winner_name = player1.player_name if player2.health <= 0 else player2.player_name

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
            menu_select_sound.play()
            reset_game()
            return PLAYING
        if menu_button.is_clicked(mouse_pos, mouse_clicked):
            menu_select_sound.play()
            return MAIN_MENU
        if quit_button.is_clicked(mouse_pos, mouse_clicked):
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
    menu_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, "Main Menu", (100, 50, 200), (150, 100, 250))
    quit_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 160, 300, 60, "Quit", (100, 50, 200), (150, 100, 250))

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
                    return PLAYING
                elif event.key == pygame.K_p:
                    return PLAYING
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True

        # Check button interactions
        resume_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        if resume_button.is_clicked(mouse_pos, mouse_clicked):
            menu_select_sound.play()
            return PLAYING
        if menu_button.is_clicked(mouse_pos, mouse_clicked):
            menu_select_sound.play()
            return MAIN_MENU
        if quit_button.is_clicked(mouse_pos, mouse_clicked):
            menu_select_sound.play()
            pygame.quit()
            sys.exit()

        # Draw buttons
        resume_button.draw(screen)
        menu_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return PLAYING


def reset_game():
    global all_sprites, platforms, player1, player2, player1_group, player2_group, effects, bg_scroll, particles

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    effects = pygame.sprite.Group()
    player1 = Samurai(100, HEIGHT - 100, controls1, player1_idle, player1_run, player1_attack, player1_jump,
                      player1_hurt, player1.player_name)
    player2 = Samurai(700, HEIGHT - 100, controls2, player2_idle, player2_run, player2_attack, player2_jump,
                      player2_hurt, player2.player_name)
    player1_group = pygame.sprite.GroupSingle(player1)
    player2_group = pygame.sprite.GroupSingle(player2)
    all_sprites.add(player1, player2)
    particles = []

    for x, y, w, h, platform_type in platform_data:
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

    keys = pygame.key.get_pressed()

    if current_game_state == MAIN_MENU:
        current_game_state = show_main_menu()

    elif current_game_state == CHARACTER_SELECT:
        current_game_state = show_character_select()

    elif current_game_state == PLAYING:
        # Handle Player Input and Actions
        player1.handle_keys(keys, effects)
        player1.apply_gravity()
        player1.handle_collision(platforms)

        player2.handle_keys(keys, effects)
        player2.apply_gravity()
        player2.handle_collision(platforms)

        # Background Scrolling
        bg_scroll = (bg_scroll + 1) % background_rect.width

        # Update Sprites
        all_sprites.update(0)
        effects.update(0)

        # Projectile Collisions
        for projectile in player1.projectiles:
            if pygame.sprite.spritecollide(projectile, player2_group, False):
                player2.take_damage(10, player1)
                projectile.kill()
                # Create hit effect
                hit_effect = Effect(projectile.rect.centerx, projectile.rect.centery, explosion_imgs, 0.3)
                effects.add(hit_effect)
                # Create particles
                create_particles(projectile.rect.centerx, projectile.rect.centery, 15, (255, 200, 0))

        for projectile in player2.projectiles:
            if pygame.sprite.spritecollide(projectile, player1_group, False):
                player1.take_damage(10, player2)
                projectile.kill()
                # Create hit effect
                hit_effect = Effect(projectile.rect.centerx, projectile.rect.centery, explosion_imgs, 0.3)
                effects.add(hit_effect)
                # Create particles
                create_particles(projectile.rect.centerx, projectile.rect.centery, 15, (255, 200, 0))

        # Check for Game Over
        if player1.health <= 0 or player2.health <= 0:
            current_game_state = GAME_OVER

        # Draw Background
        screen.blit(background_img, (-bg_scroll, 0))
        screen.blit(background_img, (-bg_scroll + background_rect.width, 0))

        # Draw clouds
        for cloud in clouds:
            cloud.update()
            cloud.draw(screen)

        # Draw Sprites
        for entity in all_sprites:
            entity.draw(screen)

        # Draw effects
        for effect in effects:
            effect.draw(screen)

        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
            else:
                particle.draw(screen)

        # Draw UI
        # Player 1 info
        pygame.draw.rect(screen, (0, 0, 0, 150), (10, 10, 250, 80), border_radius=5)
        draw_text(screen, player1.player_name, font, 135, 25, (255, 100, 100))
        draw_text(screen, f"Health: {player1.health}", font, 135, 55, WHITE)

        # Special meter for Player 1
        pygame.draw.rect(screen, (50, 50, 80), (10, 80, 250, 15), border_radius=3)
        special_width = (player1.special_meter / player1.max_special) * 250
        special_color = BLUE if not player1.special_ready else GOLD
        pygame.draw.rect(screen, special_color, (10, 80, special_width, 15), border_radius=3)

        # Player 2 info
        pygame.draw.rect(screen, (0, 0, 0, 150), (WIDTH - 260, 10, 250, 80), border_radius=5)
        draw_text(screen, player2.player_name, font, WIDTH - 135, 25, (100, 100, 255))
        draw_text(screen, f"Health: {player2.health}", font, WIDTH - 135, 55, WHITE)

        # Special meter for Player 2
        pygame.draw.rect(screen, (50, 50, 80), (WIDTH - 260, 80, 250, 15), border_radius=3)
        special_width = (player2.special_meter / player2.max_special) * 250
        special_color = BLUE if not player2.special_ready else GOLD
        pygame.draw.rect(screen, special_color, (WIDTH - 260, 80, special_width, 15), border_radius=3)

        # Timer and round info
        pygame.draw.rect(screen, (0, 0, 0, 150), (WIDTH // 2 - 75, 10, 150, 40), border_radius=5)
        draw_text(screen, "Round 1", font, WIDTH // 2, 30, WHITE)

    elif current_game_state == GAME_OVER:
        current_game_state = show_game_over()

    elif current_game_state == PAUSE_MENU:
        current_game_state = show_pause_menu()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()