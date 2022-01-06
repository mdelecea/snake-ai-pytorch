import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.SysFont('arial', 25)
NUM_SNAKES = 4

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE = (0, 0, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
#SPEED = 60
SPEED = None

HEIGHT = 480
WIDTH = 640

class Snake:
    def __init__(self, x, y, direction = None):
        self.w, self.h = x, y
        self.head = Point(random.randint(self.w//(4*BLOCK_SIZE),3*self.w//(4*BLOCK_SIZE))*BLOCK_SIZE, random.randint(self.h//(4*BLOCK_SIZE),3*self.h//(4*BLOCK_SIZE))*BLOCK_SIZE) #randomize starting position
        self.body = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        if direction == None:
            self.direction = random.choice([Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP])
        else:
            self.direction = direction
        #randomize the starting direction of the snake

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

class SnakeGameAI:

    def __init__(self, w=WIDTH, h=HEIGHT):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.snakeList = []
        direction = random.choice([Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP])
        for i in range(NUM_SNAKES):
            self.snakeList.append(Snake(self.w, self.h, direction))

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0


    def _place_food(self):
        #x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        #y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        # randomize food location
        x = random.randint(self.w//(4*BLOCK_SIZE),3*self.w//(4*BLOCK_SIZE))*BLOCK_SIZE
        y = random.randint(self.h//(4*BLOCK_SIZE),3*self.h//(4*BLOCK_SIZE))*BLOCK_SIZE 
        self.food = Point(x, y)
        for snake in self.snakeList:
            if self.food in snake.body:
                self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        pygame.image.save(self.display, "screenshot"+str(self.frame_iteration)+".jpeg")
        # 1. collect input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        for snake in self.snakeList:
            snake._move(action)
            snake.body.insert(0, snake.head)
        
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 500*max(snake.body.__len__() for snake in self.snakeList):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        for snake in self.snakeList:
            if snake.head == self.food:
                self.score += 1
                reward = 10
                self._place_food()
            else:
                snake.body.pop()
        
        # 5. update ui and clock
        self._update_ui()
        if SPEED != None:
            self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = []
            for snake in self.snakeList:
                pt.append(snake.head)
        #else: # hits itself or others
        #    for snake in self.snakeList:
        #        if not set(pt).isdisjoint(snake.body):
        #            return True
        # hits boundary
        for p in pt:
            if p.x > self.w - BLOCK_SIZE or p.x < 0 or p.y > self.h - BLOCK_SIZE or p.y < 0:
                return True
        # hits itself or others
        #for snake in self.snakeList:
        #    if not set(pt).isdisjoint(snake.body[1:]):
        #            return True
        return False


    def _update_ui(self):
        self.display.fill(BLACK)

        for snake in self.snakeList:
            for pt in snake.body:
                pygame.draw.rect(self.display, BLUE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
