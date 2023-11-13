from enum import Enum
import pygame
import random

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Snake:
    def __init__(self, name, start_pos, snake_block, screen, color):
        self.length = 1
        self.positions = [start_pos]  # List of positions of the snake's segments
        self.snake_block = snake_block
        self.x_change = 0
        self.y_change = 0
        self.screen = screen
        self.direction = None
        self.name = name
        self.color = color
    def update_direction(self, event_key):
        if event_key in [pygame.K_LEFT, pygame.K_a] and self.direction != Direction.RIGHT:
            self.x_change = -self.snake_block
            self.y_change = 0
            self.direction = Direction.LEFT
        elif event_key in [pygame.K_RIGHT, pygame.K_d] and self.direction != Direction.LEFT:
            self.x_change = self.snake_block
            self.y_change = 0
            self.direction = Direction.RIGHT
        elif event_key in [pygame.K_UP, pygame.K_w] and self.direction != Direction.DOWN:
            self.y_change = -self.snake_block
            self.x_change = 0
            self.direction = Direction.UP
        elif event_key in [pygame.K_DOWN, pygame.K_s] and self.direction != Direction.UP:
            self.y_change = self.snake_block
            self.x_change = 0
            self.direction = Direction.DOWN

    def move(self):
        head = self.positions[-1].copy()
        head[0] += self.x_change
        head[1] += self.y_change
        self.positions.append(head)
        if len(self.positions) > self.length:
            del self.positions[0]

    def draw(self):
        for pos in self.positions:
            pygame.draw.rect(self.screen, self.color, [pos[0], pos[1], self.snake_block, self.snake_block])

    def grow(self):
        self.length += 1

    def get_head_position(self):
        return self.positions[-1]
    
    def check_self_collision(self):
        head = self.get_head_position()
        return head in self.positions[:-1]    

class GameBoard:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.player_names = ["", ""]
        self.magenta = pygame.Color('magenta')
        self.yellow = pygame.Color('yellow')
        self.cyan = pygame.Color('cyan')
        self.snake_colors = [self.yellow, self.cyan]
        self.eat_sound = pygame.mixer.Sound('snakkis/348112__matrixxx__crunch.wav')
        self.game_over_sound = pygame.mixer.Sound('snakkis/267069__brainclaim__monster-tripod-horn.wav')
        self.start_game_sound = pygame.mixer.Sound('snakkis/540162__schreibsel__snake-hissing.mp3')
        pygame.mixer.music.load('snakkis/244417__lennyboy__scaryviolins.ogg')
        self.start_game_sound.play()

    def init_game(self):
        self.winner = None
        self.snakes = [
            Snake(self.player_names[0] if self.player_names[0] else "Player 1", 
                  [self.width // 4, self.height // 2], 10, self.screen, self.snake_colors[0]),
            Snake(self.player_names[1] if self.player_names[1] else "Player 2", 
                  [3 * self.width // 4, self.height // 2], 10, self.screen, self.snake_colors[1])
        ]
        self.reposition_food()

    def main_menu(self):
        font = pygame.font.SysFont(None, 55)
        input_boxes = [pygame.Rect(100, 100, 300, 50), pygame.Rect(100, 200, 300, 50)]  # Larger boxes
        start_button = pygame.Rect(100, 300, 300, 60)  # Start button rectangle
        active = [False, False]
        done = False

        # Placeholder texts for input boxes
        placeholder_texts = ["Player1", "Player2"]

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        done = True  # Start the game when the start button is clicked
                    for i, box in enumerate(input_boxes):
                        if box.collidepoint(event.pos):
                            active[i] = True
                            self.player_names[i] = ""  # Clear the placeholder text when box is clicked
                        else:
                            active[i] = False
                if event.type == pygame.KEYDOWN:
                    for i in range(2):
                        if active[i]:
                            if event.key == pygame.K_RETURN:
                                done = True  # Start the game when Enter is pressed
                            elif event.key == pygame.K_BACKSPACE:
                                self.player_names[i] = self.player_names[i][:-1]
                            else:
                                self.player_names[i] += event.unicode

            self.screen.fill((30, 30, 30))
            for i, box in enumerate(input_boxes):
                # Display the name if active or entered, else display placeholder text
                display_text = self.player_names[i] if active[i] or self.player_names[i] else placeholder_texts[i]
                txt_surface = font.render(display_text, True, self.snake_colors[i])
                self.screen.blit(txt_surface, (box.x + 5, box.y + 5))
                pygame.draw.rect(self.screen, self.snake_colors[i], box, 2)

            # Render start button
            pygame.draw.rect(self.screen, self.magenta, start_button)  # Draw button
            start_text = font.render('Start Game', True, (255, 255, 255))
            self.screen.blit(start_text, (start_button.x + 5, start_button.y + 10))

            pygame.display.flip()

        self.init_game()  # Initialize the game with the entered names
        return True

    def run_game(self):
        self.start_time = pygame.time.get_ticks()
        pygame.mixer.music.play(loops=-1)
        game_over = False
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                elif event.type == pygame.KEYDOWN:
                    # Player 1 controls (WASD)
                    if event.key in [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]:
                        self.snakes[0].update_direction(event.key)
                    # Player 2 controls (Arrow keys)
                    elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                        self.snakes[1].update_direction(event.key)                 
            
            for i, snake in enumerate(self.snakes):
                next_position = self.get_next_position(snake.get_head_position(), snake.direction)

                # Check for collisions with other snakes
                for j, other_snake in enumerate(self.snakes):
                    if i != j and list(next_position) in other_snake.positions:
                        print(f"{snake.name} collision at {next_position} with {other_snake.name}")
                        game_over = True
                        self.winner = other_snake

                # Check for self-collision and out of bounds for each snake
                if self.is_out_of_bounds(next_position) or snake.check_self_collision():
                    print(f"{snake.name} out of bounds or self-collision at {next_position}")
                    game_over = True
                    self.winner = self.snakes[1 - i]

                if not game_over:
                    snake.move()
                    if self.is_collision(snake.get_head_position(), (self.foodx, self.foody)):
                        snake.grow()
                        self.reposition_food()                
                        self.eat_sound.play()

            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, self.magenta, [self.foodx, self.foody, self.snakes[0].snake_block, self.snakes[0].snake_block])
            for snake in self.snakes:
                snake.draw()
            pygame.display.update()
            self.clock.tick(15)
        pygame.mixer.music.stop()
        self.game_over_sound.play()
        self.game_over_screen()
        # return game_over

    def get_next_position(self, current_position, direction):
        x, y = current_position
        if direction == Direction.UP:
            y -= self.snakes[0].snake_block
        elif direction == Direction.DOWN:
            y += self.snakes[0].snake_block
        elif direction == Direction.LEFT:
            x -= self.snakes[0].snake_block
        elif direction == Direction.RIGHT:
            x += self.snakes[0].snake_block
        return (x, y)

    def is_out_of_bounds(self, position):
        x, y = position
        return x >= self.width or x < 0 or y >= self.height or y < 0

    def is_collision(self, pos1, pos2):
        return pos1[0] == pos2[0] and pos1[1] == pos2[1]

    def reposition_food(self):
        self.foodx = round(random.randrange(0, self.width - self.snakes[1].snake_block) / 10.0) * 10.0
        self.foody = round(random.randrange(0, self.height - self.snakes[1].snake_block) / 10.0) * 10.0

    def game_over_screen(self):
        font = pygame.font.SysFont(None, 55)
        game_over_text = font.render(f'Game Over - {self.winner.name} Wins!', True, self.winner.color)
        restart_text = font.render('Press R to Restart or Q to Quit', True, self.magenta)

        self.screen.blit(game_over_text, [self.width // 4 - 100, self.height // 3])
        self.screen.blit(restart_text, [self.width // 4 - 100, self.height // 2])
        pygame.display.update()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                    return  # Quit the game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting_for_input = False
                        self.init_game()  # Reset the game
                        self.run_game()   # Restart the game
                    if event.key == pygame.K_q:
                        waiting_for_input = False
                        return  # Quit the game

# Main Program
game = GameBoard(640, 480)
if game.main_menu():
    game.run_game()
pygame.quit()
