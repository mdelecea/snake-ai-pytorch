import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):

        point_l, point_r, point_u, point_d = [], [], [], []
        dir_l, dir_r, dir_u, dir_d = [], [], [], []
        for snake in game.snakeList: 
            #find point of snake
            point_l.append(Point(snake.head.x - 20, snake.head.y)) 
            point_r.append(Point(snake.head.x + 20, snake.head.y))
            point_u.append(Point(snake.head.x, snake.head.y - 20))
            point_d.append(Point(snake.head.x, snake.head.y + 20))
            #find current direction of snake
            dir_l.append(snake.direction == Direction.LEFT) 
            dir_r.append(snake.direction == Direction.RIGHT)
            dir_u.append(snake.direction == Direction.UP)
            dir_d.append(snake.direction == Direction.DOWN)
        
        danger_s = [None]*len(game.snakeList)
        danger_r = [None]*len(game.snakeList)
        danger_l = [None]*len(game.snakeList)

        for i in range(len(game.snakeList)):
            # Danger straight
            danger_s[i] = (dir_r[i] and game.is_collision(point_r)) or ...
            (dir_l[i] and game.is_collision(point_l)) or ...
            (dir_u[i] and game.is_collision(point_u)) or ...
            (dir_d[i] and game.is_collision(point_d)),

            # Danger right
            danger_r[i] = (dir_u[i] and game.is_collision(point_r)) or ...
            (dir_d[i] and game.is_collision(point_l)) or ...
            (dir_l[i] and game.is_collision(point_u)) or ...
            (dir_r[i] and game.is_collision(point_d)),

            # Danger left
            danger_l[i] = (dir_d[i] and game.is_collision(point_r)) or ...
            (dir_u[i] and game.is_collision(point_l)) or ...
            (dir_r[i] and game.is_collision(point_u)) or ...
            (dir_l[i] and game.is_collision(point_d)),
            

        # Food location
        manhat_dist = []
        food_direction = [False, False, False, False]
        for snake in game.snakeList:
            manhat_dist.append(abs(snake.head.x - game.food.x) + abs(snake.head.y - game.food.y))
        close_snake = manhat_dist.index(min(manhat_dist))
        if game.snakeList[close_snake].head.x > game.food.x: #Left
            food_direction[0] = True
        if game.snakeList[close_snake].head.x < game.food.x: #Right
            food_direction[1] = True
        if game.snakeList[close_snake].head.y < game.food.y: #Up
            food_direction[2] = True
        if game.snakeList[close_snake].head.y > game.food.y: #Down
            food_direction[3] = True

        state = [
            # Danger in direction
            True in danger_s,
            True in danger_r,
            True in danger_l,
            
            # Move direction
            dir_l[0],
            dir_r[0],
            dir_u[0],
            dir_d[0],

            # Food location
            food_direction[0],
            food_direction[1],
            food_direction[2],
            food_direction[3]
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = max(200 - self.n_games,10)
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            #if np.not_equal(state_new.all(),state_old.all()):
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()