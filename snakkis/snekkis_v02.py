from enum import Enum
import pygame
import random

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Snake:
    def __init__(self, start_pos, snake_block, screen):
        self.length = 1
        self.positions = [start_pos]  # List of positions of the snake's segments
        self.snake_block = snake_block
        self.x_change = 0
        self.y_change = 0
        self.screen = screen
        self.direction = None

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
            pygame.draw.rect(self.screen, (255, 255, 255), [pos[0], pos[1], self.snake_block, self.snake_block])

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
        self.init_game()

    def init_game(self):
        self.snakes = [
            Snake([self.width // 4, self.height // 2], 10, self.screen),   # Player 1
            Snake([3 * self.width // 4, self.height // 2], 10, self.screen)  # Player 2
        ]
        self.reposition_food()

    def run_game(self):
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

            for snake in self.snakes:
                snake.move()
                if self.is_out_of_bounds(snake.get_head_position()) or snake.check_self_collision():
                    game_over = True
                if self.is_collision(snake.get_head_position(), (self.foodx, self.foody)):
                    snake.grow()
                    self.reposition_food()                    

            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (255, 0, 0), [self.foodx, self.foody, self.snakes[0].snake_block, self.snakes[0].snake_block])
            for snake in self.snakes:
                snake.draw()
            pygame.display.update()
            self.clock.tick(15)

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
        game_over_text = font.render('Game Over', True, (255, 0, 0))
        restart_text = font.render('Press R to Restart or Q to Quit', True, (255, 0, 0))

        self.screen.blit(game_over_text, [self.width // 4, self.height // 3])
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
game.run_game()
pygame.quit()
