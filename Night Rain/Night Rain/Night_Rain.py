# Full updated code with independent slash and shuriken handling and animation priority

import pygame
import sys

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
GRAVITY = 0.75
JUMP_SPEED = -19
CLIMB_SPEED = 4.9
GROUND_LEVEL = HEIGHT - 300  # Floor raised higher

# Initialize
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja Animation")
clock = pygame.time.Clock()

# Load sprite sheet
sprite_sheet = pygame.image.load("Ninja_Sprite.png").convert_alpha()

# Sprite sheet grid (5 rows x 4 cols assumed, each 320x320)
TILE_WIDTH, TILE_HEIGHT = 320, 320

def get_frame(row, col):
    return sprite_sheet.subsurface(pygame.Rect((col - 1) * TILE_WIDTH, (row - 1) * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))

# Animation frames
animations = {
    "idle": [get_frame(1, 1), get_frame(1, 2)],
    "run": [get_frame(1, 3), get_frame(1, 4), get_frame(2, 1), get_frame(2, 2), get_frame(2, 3), get_frame(2, 4)],
    "jump": [get_frame(3, 1)],
    "fall": [get_frame(3, 2)],
    "climb": [get_frame(3, 3), get_frame(3, 4), get_frame(4, 1), get_frame(4, 2)],
    "dash": [get_frame(4, 3)],
    "slash": [get_frame(4, 4), get_frame(5, 1), get_frame(5, 2)],
    "shuriken": [get_frame(5, 3), get_frame(5, 4)]
}

# Animation speed per state (higher = slower)
animation_speed = {
    "idle": 22,
    "run": 5,
    "jump": 6,
    "fall": 6,
    "climb": 9.3,
    "dash": 6,
    "slash": 10,
    "shuriken": 10
}

# Character class
class Ninja:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = GROUND_LEVEL
        self.vy = 0
        self.on_ground = True
        self.facing_right = True
        self.frame_index = 0
        self.frame_timer = 0
        self.state = "idle"
        self.image = animations["idle"][0]
        self.climbing = False
        self.attacking = False
        self.throwing = False

        # Slash logic
        self.slash_timer = 0
        self.slash_cooldown_timer = 0
        self.SLASH_DURATION = len(animations["slash"]) * animation_speed["slash"]
        self.SLASH_COOLDOWN = 60  # 1 second cooldown

        # Shuriken logic
        self.shuriken_timer = 0
        self.shuriken_cooldown_timer = 0
        self.SHURIKEN_DURATION = len(animations["shuriken"]) * animation_speed["shuriken"]
        self.SHURIKEN_COOLDOWN = 60  # 1 second cooldown

        # Dash logic
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.DASH_DURATION = 12
        self.DASH_COOLDOWN = 240
        self.DASH_SPEED = 30

    def update(self, keys):
        self.frame_timer += 1
        dx = 0

        if keys[pygame.K_j] and self.dash_timer == 0 and self.dash_cooldown_timer == 0:
            self.dash_timer = self.DASH_DURATION
            self.dash_cooldown_timer = self.DASH_COOLDOWN
            self.frame_index = 0
            self.frame_timer = 0

        if self.dash_timer == 0:
            if keys[pygame.K_a]:
                dx = -7
                self.facing_right = False
            elif keys[pygame.K_d]:
                dx = 7
                self.facing_right = True

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

        if keys[pygame.K_w] and not (keys[pygame.K_a] or keys[pygame.K_d]):
            self.climbing = True
            self.vy = 0
            self.y -= CLIMB_SPEED
        else:
            self.climbing = False

        if not self.climbing and self.dash_timer == 0:
            self.vy += GRAVITY
            self.y += self.vy

        if self.y >= GROUND_LEVEL:
            self.y = GROUND_LEVEL
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.dash_timer > 0:
            self.dash_timer -= 1
            dash_direction = 1 if self.facing_right else -1
            self.x += dash_direction * self.DASH_SPEED

        self.x += dx

        # Slash logic
        if self.slash_timer > 0:
            self.slash_timer -= 1
            self.attacking = True
        elif self.slash_cooldown_timer == 0 and keys[pygame.K_k]:
            self.slash_timer = self.SLASH_DURATION
            self.slash_cooldown_timer = self.SLASH_COOLDOWN
            self.frame_index = 0
            self.frame_timer = 0
            self.attacking = True
        else:
            self.attacking = False

        # Shuriken logic
        if self.shuriken_timer > 0:
            self.shuriken_timer -= 1
            self.throwing = True
        elif self.shuriken_cooldown_timer == 0 and keys[pygame.K_l]:
            self.shuriken_timer = self.SHURIKEN_DURATION
            self.shuriken_cooldown_timer = self.SHURIKEN_COOLDOWN
            self.frame_index = 0
            self.frame_timer = 0
            self.throwing = True
        else:
            self.throwing = False

        # Set animation state with priority
        if self.attacking:
            self.state = "slash"
        elif self.throwing:
            self.state = "shuriken"
        elif self.dash_timer > 0:
            self.state = "dash"
        elif self.climbing:
            self.state = "climb"
        elif not self.on_ground:
            self.state = "jump" if self.vy < 0 else "fall"
        elif dx != 0:
            self.state = "run"
        else:
            self.state = "idle"

        # Cooldowns
        if self.slash_cooldown_timer > 0:
            self.slash_cooldown_timer -= 1
        if self.shuriken_cooldown_timer > 0:
            self.shuriken_cooldown_timer -= 1
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

        self.animate()

    def animate(self):
        frames = animations.get(self.state, animations["idle"])
        speed = animation_speed.get(self.state, 6)

        if len(frames) == 0:
            self.image = animations["idle"][0]
            return

        if self.frame_index >= len(frames):
            if self.state in ["slash", "shuriken"]:
                self.frame_index = len(frames) - 1
            else:
                self.frame_index = 0

        if self.frame_timer >= speed:
            if self.state in ["slash", "shuriken"] and self.frame_index >= len(frames) - 1:
                pass
            else:
                self.frame_index = (self.frame_index + 1) % len(frames)
                self.frame_timer = 0

        frame = frames[self.frame_index]

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# Game loop
player = Ninja()

while True:
    screen.fill((40, 40, 40))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    player.update(keys)
    player.draw(screen)

    pygame.draw.line(screen, (100, 100, 100), (0, GROUND_LEVEL + TILE_HEIGHT), (WIDTH, GROUND_LEVEL + TILE_HEIGHT), 4)

    pygame.display.flip()
    clock.tick(FPS)
