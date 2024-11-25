import pygame
import random
import sys

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE - 2  # Leave space for walls
GRID_HEIGHT = HEIGHT // GRID_SIZE - 2  # Leave space for walls
FPS = 60
BULLET_SPEED = 50  # Bullets travel at 50 pixels per second

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SMOKE_COLOR = (100, 100, 100)  # Smoke color for dead enemies

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Enemy class
class Enemy:
    def __init__(self, maze):
        self.x = random.randint(1, GRID_WIDTH - 2)
        self.y = random.randint(1, GRID_HEIGHT - 2)
        while maze[self.y][self.x] == 1:  # Ensure it doesn't spawn in a wall
            self.x = random.randint(1, GRID_WIDTH - 2)
            self.y = random.randint(1, GRID_HEIGHT - 2)
        self.alive = True
        self.teleport_time = pygame.time.get_ticks()

    def teleport(self, maze):
        self.x = random.randint(1, GRID_WIDTH - 2)
        self.y = random.randint(1, GRID_HEIGHT - 2)
        while maze[self.y][self.x] == 1:  # Ensure it doesn't teleport into a wall
            self.x = random.randint(1, GRID_WIDTH - 2)
            self.y = random.randint(1, GRID_HEIGHT - 2)

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, RED, (self.x * GRID_SIZE + GRID_SIZE + GRID_SIZE // 2,
                                               self.y * GRID_SIZE + GRID_SIZE + GRID_SIZE // 2),
                               GRID_SIZE // 2)
        else:
            # Draw smoke effect for dead enemies
            pygame.draw.circle(screen, SMOKE_COLOR, (self.x * GRID_SIZE + GRID_SIZE + GRID_SIZE // 2,
                                                       self.y * GRID_SIZE + GRID_SIZE + GRID_SIZE // 2),
                               GRID_SIZE // 4)

# Bullet class
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

    def move(self):
        self.x += self.direction[0] * BULLET_SPEED / FPS  # Move according to FPS
        self.y += self.direction[1] * BULLET_SPEED / FPS

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x * GRID_SIZE + GRID_SIZE + GRID_SIZE // 2),
                                             int(self.y * GRID_SIZE + GRID_SIZE + GRID_SIZE // 2)),
                           GRID_SIZE // 4)  # Smaller circle for bullets

# Collision detection functions
def check_collision_bullet_enemy(bullet, enemies):
    bullet_radius = 1
    for enemy in enemies:
        if enemy.alive:
            enemy_radius = 1
            # Calculate the distance between bullet and enemy center points
            dist_x = bullet.x - enemy.x
            dist_y = bullet.y - enemy.y
            distance_squared = dist_x ** 2 + dist_y ** 2
            # Compare with the combined radii squared
            if distance_squared <= (bullet_radius + enemy_radius) ** 2:
                enemy.alive = False  # Mark enemy as dead
                print("CHEESE")
                return True
    return False

def check_collision_player_enemy(player_pos, enemies):
    for enemy in enemies:
        if enemy.alive and player_pos[0] == enemy.x and player_pos[1] == enemy.y:
            return True
    return False

# Maze generation
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve(x, y):
        directions = [UP, DOWN, LEFT, RIGHT]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                maze[ny][nx] = 0
                carve(nx, ny)

    maze[1][1] = 0  # Start point
    carve(1, 1)
    maze[height - 2][width - 2] = 0  # End point
    return maze

# Draw maze
def draw_maze(screen, maze):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = BLACK if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, (x * GRID_SIZE + GRID_SIZE, y * GRID_SIZE + GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Main function
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Game by Callum Grant")
    clock = pygame.time.Clock()

    level = 1
    player_pos = [1, 1]
    end_pos = [GRID_WIDTH - 2, GRID_HEIGHT - 2]
    start_time = pygame.time.get_ticks()
    timer_duration = 30 * 1000  # 30 seconds in milliseconds
    game_over = False
    bullets = []
    enemies = [Enemy(generate_maze(GRID_WIDTH + 1, GRID_HEIGHT + 1)) for _ in range(5)]

    while True:
        # Generate maze for the current level
        maze = generate_maze(GRID_WIDTH + 1, GRID_HEIGHT + 1)
        maze[end_pos[1]][end_pos[0]] = 0  # Ensure end position is a path

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if not game_over:  # Allow movement only when game is not over
                # Player movement
                if keys[pygame.K_UP]:
                    new_pos = [player_pos[0], player_pos[1] - 1]
                    if maze[new_pos[1]][new_pos[0]] == 0:
                        player_pos[1] -= 1
                if keys[pygame.K_DOWN]:
                    new_pos = [player_pos[0], player_pos[1] + 1]
                    if maze[new_pos[1]][new_pos[0]] == 0:
                        player_pos[1] += 1
                if keys[pygame.K_LEFT]:
                    new_pos = [player_pos[0] - 1, player_pos[1]]
                    if maze[new_pos[1]][new_pos[0]] == 0:
                        player_pos[0] -= 1
                if keys[pygame.K_RIGHT]:
                    new_pos = [player_pos[0] + 1, player_pos[1]]
                    if maze[new_pos[1]][new_pos[0]] == 0:
                        player_pos[0] += 1

                # Shooting with WASD
                if keys[pygame.K_w]:
                    bullets.append(Bullet(player_pos[0], player_pos[1], UP))
                elif keys[pygame.K_a]:
                    bullets.append(Bullet(player_pos[0], player_pos[1], LEFT))
                elif keys[pygame.K_s]:
                    bullets.append(Bullet(player_pos[0], player_pos[1], DOWN))
                elif keys[pygame.K_d]:
                    bullets.append(Bullet(player_pos[0], player_pos[1], RIGHT))

            screen.fill(BLACK)

            # Draw maze
            draw_maze(screen, maze)

            # Draw player
            pygame.draw.rect(screen, GREEN, (player_pos[0] * GRID_SIZE + GRID_SIZE,
                                               player_pos[1] * GRID_SIZE + GRID_SIZE,
                                               GRID_SIZE, GRID_SIZE))

            # Draw end location
            pygame.draw.rect(screen, RED, (end_pos[0] * GRID_SIZE + GRID_SIZE,
                                            end_pos[1] * GRID_SIZE + GRID_SIZE,
                                            GRID_SIZE, GRID_SIZE))

            # Update and draw bullets
            for bullet in bullets[:]:
                bullet.move()
                bullet.draw(screen)
                if bullet.x < 0 or bullet.x >= GRID_WIDTH or bullet.y < 0 or bullet.y >= GRID_HEIGHT:
                    bullets.remove(bullet)
                if check_collision_bullet_enemy(bullet, enemies):
                    bullets.remove(bullet)  # Remove bullet if it hits an enemy

            # Move and draw enemies
            current_time = pygame.time.get_ticks()
            for enemy in enemies:
                if enemy.alive:
                    enemy.draw(screen)
                    if current_time - enemy.teleport_time >= 10000:  # Teleport every 10 seconds
                        enemy.teleport(maze)
                        enemy.teleport_time = current_time

            # Check for player and enemy collisions
            if check_collision_player_enemy(player_pos, enemies):
                game_over = True

            # Timer display
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = max(0, timer_duration - elapsed_time)
            timer_text = f"Time: {remaining_time // 1000}"
            font = pygame.font.Font(None, 36)
            timer_surface = font.render(timer_text, True, WHITE)
            screen.blit(timer_surface, (10, 10))

            # Check for game over
            if remaining_time == 0:
                game_over = True

            if game_over:
                font = pygame.font.Font(None, 74)
                text = font.render("Game Over!", True, GREEN)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

                # Restart and Quit instructions
                instructions = font.render("Press R to Restart or Q to Quit", True, BLUE)
                screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT // 2 + 50))

                # Check for restart or quit
                if keys[pygame.K_r]:
                    level = 1
                    player_pos = [1, 1]
                    end_pos = [GRID_WIDTH - 2, GRID_HEIGHT - 2]
                    start_time = pygame.time.get_ticks()  # Reset timer for next level
                    game_over = False
                    bullets.clear()  # Clear bullets for next level
                    enemies = [Enemy(generate_maze(GRID_WIDTH + 1, GRID_HEIGHT + 1)) for _ in range(5)]  # Reset enemies
                    break  # Regenerate the maze for the next level
                elif keys[pygame.K_q]:
                    pygame.quit()
                    sys.exit()

            else:
                # Draw level indicator
                level_text = f"Level: {level}"
                level_surface = font.render(level_text, True, WHITE)
                screen.blit(level_surface, (WIDTH - 150, 10))

                # Check win condition
                if player_pos == end_pos:
                    print(f"You've reached the end of level {level}!")
                    level += 1
                    player_pos = [1, 1]  # Reset player position
                    end_pos = [GRID_WIDTH - 2, GRID_HEIGHT - 2]  # Reset end position
                    start_time = pygame.time.get_ticks()  # Reset timer for next level
                    game_over = False
                    bullets.clear()  # Clear bullets for next level
                    enemies = [Enemy(generate_maze(GRID_WIDTH + 1, GRID_HEIGHT + 1)) for _ in range(5)]  # Reset enemies
                    break  # Regenerate the maze for the next level

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()

