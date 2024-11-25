import pygame  # Importing the Pygame library
import sys  # Importing the sys module to handle system-specific parameters
import random  # Importing the random module for random number generation
import math
# Initialize Pygame
pygame.init()

# Game window settings
WIDTH, HEIGHT = 800, 600  # Defining the width and height of the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Setting up the game screen with the specified width and height
pygame.display.set_caption("Callum's Collision Game")  # Setting the title of the game window

# Colors
WHITE = (255, 255, 255)  # RGB values for white color
RED = (255, 0, 0)  # RGB values for red color
BLUE = (0, 0, 255)  # RGB values for blue color
GREEN = (0, 255, 0)  # RGB values for green color
BLACK = (0, 0, 0)  # RGB values for black color
LIGHT_BLUE = (173, 216, 230)  # RGB values for light blue color
DARK_GRAY = (50, 50, 50)  # RGB values for dark gray color
YELLOW = (255,255,0)

# Game settings
square_size = 35  # Defining the size of the player's square
square_x = WIDTH // 2 - square_size // 2  # Initial horizontal position of the square (centered on the screen)
square_y = HEIGHT // 2 - square_size // 2  # Initial vertical position of the square (centered on the screen)
speed = 8  # Defining the speed of the player's movement
score = 0  # Initial score
lives = 25  # Initial number of lives
life_snitch = 3

# Circle settings
circle_radius = 25  # Radius of the circles
circle_1_points = 1  # Points awarded for colliding with the first circle
circle_2_points = 2  # Points awarded for colliding with the second circle
circle_3_points = 150
# Randomly placing the circles on the screen
circle_1 = pygame.Rect(random.randint(0, WIDTH - circle_radius*2), random.randint(0, HEIGHT - circle_radius*2), circle_radius*2, circle_radius*2)
circle_2 = pygame.Rect(random.randint(0, WIDTH - circle_radius*2), random.randint(0, HEIGHT - circle_radius*2), circle_radius*2, circle_radius*2)
circle_3 = pygame.Rect(random.randint(0, WIDTH - 20*2), random.randint(0, HEIGHT - 20*2), 20*2, 20*2)


# Red Circle settings (new circle)
red_circle_radius = 25  # Radius of the red circle
# Randomly placing the red circle on the screen
red_circle = pygame.Rect(random.randint(0, WIDTH - red_circle_radius*2), random.randint(0, HEIGHT - red_circle_radius*2), red_circle_radius*2, red_circle_radius*2)

# Enemy settings (triangles)
triangle_size = 50  # Defining the size of the triangles
# Randomly placing the triangles on the screen
black_triangle = pygame.Rect(random.randint(0, WIDTH - triangle_size), random.randint(0, HEIGHT - triangle_size), triangle_size, triangle_size)
blue_triangle = pygame.Rect(random.randint(0, WIDTH - triangle_size), random.randint(0, HEIGHT - triangle_size), triangle_size, triangle_size)

# Font for displaying score and lives
font = pygame.font.SysFont('Arial', 24)  # Creating a font for smaller text (score, lives)
large_font = pygame.font.SysFont('Arial', 36)  # Creating a font for larger text (game over screen, title)

# Function to draw a triangle
def draw_triangle(color, rect):
    points = [
        (rect.centerx, rect.top),  # Top point of the triangle
        (rect.left, rect.bottom),  # Bottom left point
        (rect.right, rect.bottom)  # Bottom right point
    ]
    pygame.draw.polygon(screen, color, points)  # Drawing the triangle on the screen

# Function to display the start screen
def start_screen():
    screen.fill(DARK_GRAY)  # Filling the background with dark gray color
    title_text = large_font.render("Callum's Collision Game!", True, WHITE)  # Creating the title text
    circle_text = large_font.render("Hit the circles for rewards!(watch out of triangles)", True, RED)  # Creating the instruction text
    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)  # Creating the "Start Game" button
    pygame.draw.rect(screen, BLUE, start_button)  # Drawing the start button
    start_text = font.render("Start Game", True, WHITE)  # Creating the "Start Game" button text
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))  # Displaying the title text
    screen.blit(circle_text, (WIDTH // 2 - circle_text.get_width() // 2, HEIGHT // 3))  # Displaying the instruction text
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 15))  # Displaying the start button text

    pygame.display.flip()  # Updating the screen to show the start screen

    waiting_for_start = True  # Flag to keep the start screen up
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check if the window is closed
                pygame.quit()  # Quit Pygame
                sys.exit()  # Exit the program
            if event.type == pygame.MOUSEBUTTONDOWN:  # Check if the mouse was clicked
                if start_button.collidepoint(event.pos):  # Check if the start button was clicked
                    waiting_for_start = False  # Start the game

# Function to display the game over screen
def game_over_screen(final_score,choice):
    screen.fill(DARK_GRAY)  # Filling the background with dark gray color
    # Displaying different "Game Over" messages based on score
    if choice == "yes" and final_score > 500:
        game_over_text = large_font.render("Almost as good as me", True, WHITE)
    elif choice == "yes":
        game_over_text = large_font.render("This gets a boom", True, WHITE)
    elif final_score <= 20:
        game_over_text = large_font.render("Game Over, you suck", True, WHITE)
    else:
        game_over_text = large_font.render("Game Over, you still suck", True, WHITE)
    score_text = font.render(f"Final Score: {final_score}", True, WHITE)  # Displaying the final score
    quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)  # Creating the "Quit" button
    restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)  # Creating the "Restart" button

    pygame.draw.rect(screen, RED, quit_button)  # Drawing the "Quit" button
    pygame.draw.rect(screen, BLUE, restart_button)  # Drawing the "Restart" button
    quit_text = font.render("Quit", True, WHITE)  # Creating the "Quit" button text
    restart_text = font.render("Restart", True, WHITE)  # Creating the "Restart" button text

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))  # Displaying the game over message
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))  # Displaying the final score
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 60))  # Displaying the "Quit" button text
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 130))  # Displaying the "Restart" button text

    pygame.display.flip()  # Updating the screen to show the game over screen

    waiting_for_input = True  # Flag to keep the game over screen up
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check if the window is closed
                pygame.quit()  # Quit Pygame
                sys.exit()  # Exit the program
            if event.type == pygame.MOUSEBUTTONDOWN:  # Check if the mouse was clicked
                if quit_button.collidepoint(event.pos):  # Check if the "Quit" button was clicked
                    pygame.quit()  # Quit Pygame
                    sys.exit()  # Exit the program
                if restart_button.collidepoint(event.pos):  # Check if the "Restart" button was clicked
                    waiting_for_input = False  # Restart the game


# Main game loop
def main_game():
    global square_x, square_y, score, lives, circle_1, circle_2, red_circle, black_triangle, blue_triangle, life_snitch
    square_x = WIDTH // 2 - square_size // 2  # Resetting the player's horizontal position to the center
    square_y = HEIGHT // 2 - square_size // 2  # Resetting the player's vertical position to the center
    score = 0  # Resetting the score
    lives = 25  # Resetting the lives
    life_snitch = 3
    # Randomly placing the circles and triangles
    circle_1 = pygame.Rect(random.randint(0, WIDTH - circle_radius*2), random.randint(0, HEIGHT - circle_radius*2), circle_radius*2, circle_radius*2)
    circle_2 = pygame.Rect(random.randint(0, WIDTH - circle_radius*2), random.randint(0, HEIGHT - circle_radius*2), circle_radius*2, circle_radius*2)
    circle_3 = pygame.Rect(random.randint(0, WIDTH - 20*2), random.randint(0, HEIGHT - 20*2), 20*2, 20*2)
    red_circle = pygame.Rect(random.randint(0, WIDTH - red_circle_radius*2), random.randint(0, HEIGHT - red_circle_radius*2), red_circle_radius*2, red_circle_radius*2)
    black_triangle = pygame.Rect(random.randint(0, WIDTH - triangle_size), random.randint(0, HEIGHT - triangle_size), triangle_size, triangle_size)
    blue_triangle = pygame.Rect(random.randint(0, WIDTH - triangle_size), random.randint(0, HEIGHT - triangle_size), triangle_size, triangle_size)

    # Set up the timer
    timer_duration = 10  # 10 seconds countdown
    timer_start_ticks = pygame.time.get_ticks()  # Start time in milliseconds

    # Game loop
    clock = pygame.time.Clock()  # Create a clock object to manage the frame rate
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check if the window is closed
                pygame.quit()  # Quit Pygame
                sys.exit()  # Exit the program

        # Get key presses for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  # Move the square left
            square_x -= speed
        if keys[pygame.K_RIGHT]:  # Move the square right
            square_x += speed
        if keys[pygame.K_UP]:  # Move the square up
            square_y -= speed
        if keys[pygame.K_DOWN]:  # Move the square down
            square_y += speed

        # Make sure the square stays within the screen boundaries
        square_x = max(0, min(square_x, WIDTH - square_size))  # Ensure square stays within horizontal bounds
        square_y = max(0, min(square_y, HEIGHT - square_size))  # Ensure square stays within vertical bounds
        # Create square rectangle for collision checking
        square_rect = pygame.Rect(square_x, square_y, square_size, square_size)

        # Check for collisions with circles and update score or time
        if square_rect.colliderect(circle_1):  # Check collision with circle 1
            score += circle_1_points  # Increase score
            # Reposition the circle randomly
            circle_1 = pygame.Rect(random.randint(0, WIDTH - circle_radius*2), random.randint(0, HEIGHT - circle_radius*2), circle_radius*2, circle_radius*2)

        if square_rect.colliderect(circle_2):  # Check collision with circle 2
            score += circle_2_points  # Increase score
            # Reposition the circle randomly
            circle_2 = pygame.Rect(random.randint(0, WIDTH - circle_radius*2), random.randint(0, HEIGHT - circle_radius*2), circle_radius*2, circle_radius*2)

        if square_rect.colliderect(circle_3) and remaining_time > 15:  # Check collision with circle 2
            score += circle_3_points  # Increase score
            # Reposition the circle randomly
            circle_3 = pygame.Rect(random.randint(0, WIDTH - 20*2), random.randint(0, HEIGHT - 20*2), 20*2, 20*2)
            life_snitch -= 1
            if life_snitch == 0:
                game_over_screen(score,"yes")
                main_game()

        if square_rect.colliderect(red_circle):  # Check collision with the red circle
            timer_duration += 5  # Add 5 seconds to the timer
            # Reposition the red circle randomly
            red_circle = pygame.Rect(random.randint(0, WIDTH - red_circle_radius*2), random.randint(0, HEIGHT - red_circle_radius*2), red_circle_radius*2, red_circle_radius*2)

        # Check for collisions with enemies (triangles)
        if square_rect.colliderect(black_triangle):  # Check collision with black triangle
            game_over_screen(score,"no")  # Game Over, show the Game Over screen
            main_game()  # Restart the game

        if square_rect.colliderect(blue_triangle):  # Check collision with blue triangle
            lives -= 5  # Decrease lives
            if lives <= 0:  # If lives reach zero
                game_over_screen(score,"no")  # Game Over
                main_game()  # Restart the game
            # Reposition the blue triangle randomly
            blue_triangle = pygame.Rect(random.randint(0, WIDTH - triangle_size), random.randint(0, HEIGHT - triangle_size), triangle_size, triangle_size)

        # Calculate the remaining time
        elapsed_time = (pygame.time.get_ticks() - timer_start_ticks) / 1000  # Time in seconds
        remaining_time = max(0, timer_duration - elapsed_time)  # Remaining time in seconds
        if remaining_time > 22:

            circle_3_center = circle_3.center  # Get the current position of the red circle
            player_center = (square_x + square_size // 2, square_y + square_size // 2)  # Calculate the center of the player's square

            # Calculate direction vector from red circle to player
            direction_x = player_center[0] - circle_3_center[0]
            direction_y = player_center[1] - circle_3_center[1]

            # Calculate the distance between the red circle and the player
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance != 0:  # Avoid division by zero
                # Normalize the direction vector (make it a unit vector)
                direction_x /= distance
                direction_y /= distance

                # Move the red circle by 0.75 of the player's speed in the direction of the player
                circle_3.x += direction_x * (speed * 0.6)
                circle_3.y += direction_y * (speed * 0.6)

        # If timer reaches zero, trigger Game Over screen
        if remaining_time == 0:
            game_over_screen(score,"no")  # Show the Game Over screen
            main_game()  # Restart the game

        # Clear the screen
        screen.fill(WHITE)

        # Draw the square (player)
        pygame.draw.rect(screen, RED, square_rect)

        # Draw the circles
        pygame.draw.circle(screen, BLUE, circle_1.center, circle_radius)
        pygame.draw.circle(screen, GREEN, circle_2.center, circle_radius)
        if remaining_time > 15:
           pygame.draw.circle(screen, YELLOW, circle_3.center, 20)
        pygame.draw.circle(screen, RED, red_circle.center, red_circle_radius)  # Draw the red circle

        # Draw the triangles (enemies)
        draw_triangle(BLACK, black_triangle)
        draw_triangle(LIGHT_BLUE, blue_triangle)

        # Draw the score and lives
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        lives_text = font.render(f"Health: {lives}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))  # Display score at the top-left corner
        screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))  # Display lives at the top-right corner

        # Draw the remaining time
        timer_text = font.render(f"Time Left: {int(remaining_time)}", True, (0, 0, 0))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 10))  # Display timer in the center top

        # Update the display
        pygame.display.flip()

        # Frame rate
        clock.tick(60)  # Set the frame rate to 60 frames per second

# Run the game
start_screen()  # Show the start screen first
main_game()  # Start the game
