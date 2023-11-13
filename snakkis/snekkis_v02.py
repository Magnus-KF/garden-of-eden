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
        self.black = pygame.Color('black')
        self.dark_gray = (51, 51, 51)
        self.forest_green = (34, 139, 34)
        self.snake_colors = [self.yellow, self.cyan]
        self.eat_sound = pygame.mixer.Sound('snakkis/348112__matrixxx__crunch.wav')
        self.game_over_sound = pygame.mixer.Sound('snakkis/267069__brainclaim__monster-tripod-horn.wav')
        self.start_game_sound = pygame.mixer.Sound('snakkis/540162__schreibsel__snake-hissing.mp3')
        self.head_to_head_collision_sound = pygame.mixer.Sound('snakkis/346661__deleted_user_2104797__kiss_01.wav')
        pygame.mixer.music.load('snakkis/244417__lennyboy__scaryviolins.ogg')
        self.start_game_sound.play()

    def init_game(self):
        self.winner = None
        self.snakes = [
            Snake(self.player_names[0] if self.player_names[0] else "Adam", 
                  [self.width // 4, self.height // 2], 10, self.screen, self.snake_colors[0]),
            Snake(self.player_names[1] if self.player_names[1] else "Eve", 
                  [3 * self.width // 4, self.height // 2], 10, self.screen, self.snake_colors[1])
        ]
        self.reposition_food()

    def main_menu(self):
        font = pygame.font.SysFont(None, 55)
        box_width, box_height = 300, 50
        center_x_box = (self.width - box_width) // 2
        center_y_box = (self.height - box_height) // 2
        start_button_width, start_button_height = 300, 60        
        background_image = pygame.image.load("snakkis/An ouroboros consisting of two snakes, an anthropomorphic female snake and male snake biting each other's tails, colored with the complementary colors.png")
        # Define new size for the image
        new_width, new_height = 640, 640  # Adjust these values as needed for your screen

        # Resize the image
        background_image = pygame.transform.scale(background_image, (new_width, new_height))
        image_rect = background_image.get_rect()
        # Calculate position to center the image
        center_x = (self.width - image_rect.width) // 2
        center_y = (self.height - image_rect.height) // 2

        # Adjust vertical positions of the input boxes and start button
        input_box_y_start = 30  # Starting vertical position for the first input box
        input_box_spacing = 60  # Vertical spacing between the boxes and button

        input_boxes = [
            pygame.Rect(center_x_box, center_y_box - input_box_spacing, box_width, box_height),
            pygame.Rect(center_x_box, center_y_box, box_width, box_height)
        ]
        start_button = pygame.Rect(center_x_box, center_y_box +input_box_spacing, start_button_width, start_button_height)

        active = [False, False]
        done = False

        # Placeholder texts for input boxes
        placeholder_texts = ["Adam", "Eve"]

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
            self.screen.blit(background_image, (center_x, center_y))
            for i, box in enumerate(input_boxes):
                box_background = pygame.Surface((box.width, box.height))
                box_background.set_alpha(153)  # 20% opacity (51 out of 255)
                box_background.fill(self.snake_colors[i])  # Use the snake color
                self.screen.blit(box_background, (box.x, box.y))
                # Display the name if active or entered, else display placeholder text
                display_text = self.player_names[i] if active[i] or self.player_names[i] else placeholder_texts[i]
                txt_surface = font.render(display_text, True, self.dark_gray)
                txt_rect = txt_surface.get_rect(center=box.center)
                self.screen.blit(txt_surface, txt_rect.topleft)
                pygame.draw.rect(self.screen, self.snake_colors[i], box, 2)

            # Draw start button with semi-transparent background
            start_button_background = pygame.Surface((start_button.width, start_button.height))
            start_button_background.set_alpha(153)  # 40% opacity (102 out of 255)
            start_button_background.fill(self.magenta)  # Fill with a chosen color, e.g., magenta
            self.screen.blit(start_button_background, start_button.topleft)

            # Render start button text
            start_text = font.render('Start Game', True, self.black)
            start_text_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_text_rect.topleft)

            pygame.display.flip()

        self.init_game()  # Initialize the game with the entered names
        return True

    def run_game(self):
        self.start_time = pygame.time.get_ticks()
        pygame.mixer.music.play(loops=-1)
        game_over = False
        smooch = False
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

                for j, other_snake in enumerate(self.snakes):
                    if i != j:
                        # Check if next position is the head of the other snake
                        if next_position == other_snake.get_head_position():
                            print(f"Head-to-head collision between {snake.name} and {other_snake.name}")
                            game_over = True
                            # Handle head-to-head collision (e.g., playing sound, setting game over message)
                            self.head_to_head_collision_sound.play()
                            smooch = True
                        elif next_position in other_snake.positions:
                            print(f"{snake.name} collision at {next_position} with {other_snake.name}")
                            game_over = True
                            self.winner = other_snake
                            self.game_over_sound.play()


                # Check for self-collision and out of bounds for each snake
                if self.is_out_of_bounds(next_position) or snake.check_self_collision():
                    print(f"{snake.name} out of bounds or self-collision at {next_position}")
                    self.start_game_sound.play()
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
        self.game_over_screen(smooch)

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
        return [x, y]

    def is_out_of_bounds(self, position):
        x, y = position
        return x >= self.width or x < 0 or y >= self.height or y < 0

    def is_collision(self, pos1, pos2):
        return pos1[0] == pos2[0] and pos1[1] == pos2[1]

    def reposition_food(self):
        self.foodx = round(random.randrange(0, self.width - self.snakes[1].snake_block) / 10.0) * 10.0
        self.foody = round(random.randrange(0, self.height - self.snakes[1].snake_block) / 10.0) * 10.0

    def game_over_screen(self, smooch = False):
        font = pygame.font.SysFont(None, 55)
        if smooch:
            game_over_text = font.render(f'You are here forever', True, self.magenta)
        else:
            game_over_text = font.render(f'{self.winner.name} wins!', True, self.winner.color)
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
# game = GameBoard(640, 480)
game = GameBoard(640, 240)

if game.main_menu():
    game.run_game()
pygame.quit()
