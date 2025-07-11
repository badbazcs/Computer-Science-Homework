import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600  # multiples of 50
FPS = 60
FONT = pygame.font.SysFont(None, 48)

# colours
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
GREEN = (50, 150, 0)
RED = (200, 0, 0)
YELLOW = (255, 215, 0)
DGREEN = (55, 128, 16)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomerman")
clock = pygame.time.Clock()
fullscreen = False

# load bomb image
bomb_img = pygame.image.load("bomb_image.png")
bomb_img = pygame.transform.scale(bomb_img, (150, 150))
bomb_img_flip = pygame.transform.flip(bomb_img, True, False)

# block class with animated rigid movement
class Block:
    def __init__(self, x, y, size=50, colour=BLUE):
        self.size = size
        self.colour = colour
        self.rect = pygame.Rect(x, y, size, size)

        self.is_moving = False
        self.start_pos = self.rect.topleft
        self.target_pos = self.rect.topleft
        self.move_duration = 450  # milliseconds
        self.move_start_time = 0

    def draw(self, surface, scale_x, scale_y):
        scaled_rect = pygame.Rect(int(self.rect.x * scale_x), int(self.rect.y * scale_y), 
                                  int(self.rect.width * scale_x), int(self.rect.height * scale_y))
        pygame.draw.rect(surface, self.colour, scaled_rect)

    def update(self):
        if self.is_moving:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.move_start_time
            progress = min(elapsed / self.move_duration, 1)

            new_x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * progress
            new_y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * progress
            self.rect.topleft = (new_x, new_y)

            if progress >= 1:
                self.is_moving = False
                self.rect.topleft = self.target_pos

    def try_move(self, dx, dy, scale_x, scale_y, blocked_positions):
        if not self.is_moving:
            new_x = self.rect.x + dx * self.size
            new_y = self.rect.y + dy * self.size
            grid_x = new_x // self.size
            grid_y = new_y // self.size

            if (grid_x, grid_y) not in blocked_positions:
                self.start_pos = self.rect.topleft
                self.target_pos = (new_x, new_y)
                self.is_moving = True
                self.move_start_time = pygame.time.get_ticks()

# enemy class
class Enemy:
    def __init__(self, blocked_positions, player_pos, colour):
        self.radius = 25
        self.colour = colour
        self.pos = self.random_spawn_position(blocked_positions, player_pos)

    def random_spawn_position(self, blocked_positions, player_pos):
        grid_width = SCREEN_WIDTH // 50
        grid_height = SCREEN_HEIGHT // 50
        min_distance = 3

        while True:
            x = random.randint(0, grid_width - 1)
            y = random.randint(0, grid_height - 1)
            if (x, y) not in blocked_positions:
                distance = abs(x - player_pos[0]) + abs(y - player_pos[1])
                if distance >= min_distance:
                    return (x * 50 + 25, y * 50 + 25)

    def draw(self, surface, scale_x, scale_y):
        scaled_x = int(self.pos[0] * scale_x)
        scaled_y = int(self.pos[1] * scale_y)
        scaled_radius = int(self.radius * ((scale_x + scale_y) / 2))
        pygame.draw.circle(surface, self.colour, (scaled_x, scaled_y), scaled_radius)

# button class
class Button:
    def __init__(self, x, y, text, action, colour=GREY):
        self.rect = pygame.Rect(x, y, 300, 60)
        self.text = text
        self.action = action
        self.colour = colour

    def draw(self, surface, scale_x, scale_y):
        scaled_rect = pygame.Rect(int(self.rect.x * scale_x), int(self.rect.y * scale_y), 
                                  int(self.rect.width * scale_x), int(self.rect.height * scale_y))
        pygame.draw.rect(surface, self.colour, scaled_rect)
        text_surf = FONT.render(self.text, True, (0, 0, 0))
        surface.blit(text_surf, text_surf.get_rect(center=scaled_rect.center))

    def handle_event(self, event, scale_x, scale_y):
        mouse_pos = pygame.mouse.get_pos()
        scaled_mouse_pos = (mouse_pos[0] / scale_x, mouse_pos[1] / scale_y)

        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(scaled_mouse_pos):
            self.action()

# subroutines
def quit_game():
    pygame.quit()
    sys.exit()

def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    mode = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), mode)

# draw the grid with filled white squares near the edges
def draw_grid(surface, scale_x, scale_y, block_size):
    blocked_positions = set()

    for x in range(0, SCREEN_WIDTH // block_size):
        for y in range(0, SCREEN_HEIGHT // block_size):
            if x <= 1 or x >= SCREEN_WIDTH // block_size - 2 or y <= 1 or y >= SCREEN_HEIGHT // block_size - 2:
                pygame.draw.rect(surface, WHITE, 
                                 (int(x * block_size * scale_x), int(y * block_size * scale_y), 
                                  int(block_size * scale_x), int(block_size * scale_y)))
                blocked_positions.add((x, y))

    for x in range(0, SCREEN_WIDTH // block_size):
        for y in range(0, SCREEN_HEIGHT // block_size):
            if not (x <= 1 or x >= SCREEN_WIDTH // block_size - 2 or y <= 1 or y >= SCREEN_HEIGHT // block_size - 2):
                pygame.draw.rect(surface, WHITE, 
                                 (int(x * block_size * scale_x), int(y * block_size * scale_y), 
                                  int(block_size * scale_x), int(block_size * scale_y)), 1)

    return blocked_positions

# game screen
def game_screen(colour):
    start_x, start_y = 2, 2
    block = Block(start_x * 50, start_y * 50)
    player_grid_pos = (start_x, start_y)
    paused = False

    # Determine enemy color
    enemy_colour = GREEN if colour in (RED, YELLOW) else RED
    enemy = Enemy(set(), player_grid_pos, enemy_colour)

    def return_to_menu():
        nonlocal running
        running = False
        main_menu()

    pause_buttons = [
        Button(330, 280, "Back to Menu", return_to_menu)
    ]

    running = True
    while running:
        scale_x, scale_y = screen.get_width() / SCREEN_WIDTH, screen.get_height() / SCREEN_HEIGHT
        block_size = block.size
        screen.fill(colour)

        blocked_positions = draw_grid(screen, scale_x, scale_y, block_size)

        # Re-spawn enemy if invalid
        if (enemy.pos[0] // 50, enemy.pos[1] // 50) in blocked_positions:
            enemy = Enemy(blocked_positions, player_grid_pos, enemy_colour)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused
            elif paused:
                for btn in pause_buttons:
                    btn.handle_event(event, scale_x, scale_y)

        if not paused:
            keys = pygame.key.get_pressed()
            if not block.is_moving:
                if keys[pygame.K_LEFT]:
                    block.try_move(-1, 0, scale_x, scale_y, blocked_positions)
                elif keys[pygame.K_RIGHT]:
                    block.try_move(1, 0, scale_x, scale_y, blocked_positions)
                elif keys[pygame.K_UP]:
                    block.try_move(0, -1, scale_x, scale_y, blocked_positions)
                elif keys[pygame.K_DOWN]:
                    block.try_move(0, 1, scale_x, scale_y, blocked_positions)

        block.update()

        if paused:
            screen.fill((30, 30, 30))
            pause_text = FONT.render("Paused - Press ESC to Resume", True, WHITE)
            screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))
            for btn in pause_buttons:
                btn.draw(screen, scale_x, scale_y)
        else:
            block.draw(screen, scale_x, scale_y)
            enemy.draw(screen, scale_x, scale_y)

        pygame.display.flip()
        clock.tick(FPS)

# scene handler
def run_screen(title_text, buttons, include_bombs=False):
    while True:
        scale_x, scale_y = screen.get_width() / SCREEN_WIDTH, screen.get_height() / SCREEN_HEIGHT
        screen.fill(DGREEN)
        title = FONT.render(title_text, True, WHITE)
        screen.blit(title, title.get_rect(center=((SCREEN_WIDTH // 2)-20, 70)))

        if include_bombs:
            screen.blit(bomb_img, (50, SCREEN_HEIGHT // 2 - 80))
            screen.blit(bomb_img_flip, (SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2 - 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            for btn in buttons:
                btn.handle_event(event, scale_x, scale_y)

        for btn in buttons:
            btn.draw(screen, scale_x, scale_y)

        pygame.display.flip()
        clock.tick(FPS)

# main menu
def main_menu():
    buttons = [
        Button(330, 150, "Level Selection", level_selection),
        Button(330, 230, "Settings", settings_menu),
        Button(330, 310, "Quit", quit_game)
    ]
    run_screen("Bomerman", buttons, include_bombs=True)

# level selection
def level_selection():
    buttons = [
        Button(330, 150, "Level 1", lambda: game_screen(RED)),
        Button(330, 230, "Level 2", lambda: game_screen(YELLOW)),
        Button(330, 310, "Level 3", lambda: game_screen(GREEN)),
        Button(330, 390, "Back to Menu", main_menu)
    ]
    run_screen("Select Level", buttons)

def settings_menu():
    buttons = [
        Button(330, 200, "Toggle Fullscreen", toggle_fullscreen),
        Button(330, 280, "Back to Menu", main_menu)
    ]
    run_screen("Settings", buttons)

# start the game
main_menu()
