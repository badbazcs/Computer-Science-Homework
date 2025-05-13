import pygame
import sys

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
FPS = 60
FONT = pygame.font.SysFont(None, 48)

# Colors
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
GREEN = (50, 150, 0)
RED = (200, 0, 0)
YELLOW = (255, 215, 0)
DGREEN = (55, 128, 16)
BLUE = (0, 0, 255)

# Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomerman")
clock = pygame.time.Clock()
fullscreen = False

# Load bomb image
bomb_img = pygame.image.load("bomb_image.png")
bomb_img = pygame.transform.scale(bomb_img, (150, 150))
bomb_img_flip = pygame.transform.flip(bomb_img, True, False)

# Block class
class Block:
    def __init__(self, x, y, size=50, color=BLUE):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Button class
class Button:
    def __init__(self, x, y, text, action, colour=GREY):
        self.rect = pygame.Rect(x, y, 300, 60)
        self.text = text
        self.action = action
        self.colour = colour

    def draw(self, surface):
        pygame.draw.rect(surface, self.colour, self.rect)
        text_surf = FONT.render(self.text, True, (0, 0, 0))
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()

# Subroutines
def quit_game():
    pygame.quit()
    sys.exit()

def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    mode = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), mode)

# Scenes
def main_menu():
    buttons = [
        Button(330, 150, "Level Selection", level_selection),
        Button(330, 230, "Settings", settings_menu),
        Button(330, 310, "Quit", quit_game)
    ]
    run_screen("Bomerman", buttons, include_bombs=True)

def level_selection():
    buttons = [
        Button(330, 150, "Level 1", lambda: game_screen(RED), RED),
        Button(330, 230, "Level 2", lambda: game_screen(YELLOW), YELLOW),
        Button(330, 310, "Level 3", lambda: game_screen(GREEN), GREEN),
        Button(330, 390, "Back to Menu", main_menu)
    ]
    run_screen("Select Level", buttons)

def settings_menu():
    buttons = [
        Button(330, 200, "Toggle Fullscreen", toggle_fullscreen),
        Button(330, 280, "Back to Menu", main_menu)
    ]
    run_screen("Settings", buttons)

def game_screen(colour):
    block = Block(10, 10)  # Spawn block in top-left
    paused = False

    # Pause menu button
    def return_to_menu():
        nonlocal running
        running = False
        main_menu()

    pause_buttons = [
        Button(330, 280, "Back to Menu", return_to_menu)
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused
            elif paused:
                for btn in pause_buttons:
                    btn.handle_event(event)

        if paused:
            screen.fill((30, 30, 30))
            pause_text = FONT.render("Paused - Press ESC to Resume", True, WHITE)
            screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, 150)))

            for btn in pause_buttons:
                btn.draw(screen)
        else:
            screen.fill(colour)
            block.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

# Scene handler
def run_screen(title_text, buttons, include_bombs=False):
    while True:
        screen.fill(DGREEN)
        title = FONT.render(title_text, True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 70)))

        if include_bombs:
            screen.blit(bomb_img, (50, SCREEN_HEIGHT // 2 - 80))
            screen.blit(bomb_img_flip, (SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2 - 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            for btn in buttons:
                btn.handle_event(event)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

# Start the game
main_menu()
