from intcode import IntCode
import threading
import queue
import matplotlib.pyplot as plt
import pygame
import enum
import math


class Tile(enum.Enum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4


WIDTH = 37
HEIGHT = 24

BLOCK_SIZE = 14

colors = {
    Tile.EMPTY: (0, 0, 0),
    Tile.WALL: (0, 0, 255),
    Tile.BLOCK: (255, 0, 0),
    Tile.PADDLE: (0, 255, 0),
    Tile.BALL: (0, 255, 255),
}

def load_input(filename):
    with open(filename, 'r') as f:
        return [int(s) for s in f.read().split(',')]


day13_input = load_input('day13_input.txt')

class Arcade():

    def __init__(self, program):
        self.computer = IntCode(program)
        self.clear_board()
        self.score = 0
        self.ball = (WIDTH//2, HEIGHT//2)
        self.paddle = (WIDTH//2, HEIGHT - 2)

    def update_game_state(self, loc, data):
        (x, _) = loc
        if x < 0:
            self.score = data
        else:
            tile = Tile(data)
            if tile == Tile.EMPTY:
                if loc in self.board.keys():
                    del self.board[loc] 
            else:
                self.board[loc] = tile

            if tile == Tile.BALL:
                self.ball = loc
            elif tile == Tile.PADDLE:
                self.paddle = loc

    def determine_action(self):
        ball_x = self.ball[0]
        paddle_x = self.paddle[0]
        if ball_x > paddle_x:
            return 1
        elif ball_x < paddle_x:
            return -1
        else:
            return 0

    
    def draw_screen(self):
        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0,0,639,479))
    
        for loc in self.board.keys():
            tile = self.board[loc]
            (x, y) = loc
            sx = BLOCK_SIZE * x 
            sy = BLOCK_SIZE * y
            block = pygame.Rect(sx, sy, BLOCK_SIZE, BLOCK_SIZE)
            color = colors[tile]
            pygame.draw.rect(self.screen, color, block)

        font = pygame.font.Font(pygame.font.get_default_font(), 32)
        score_text = font.render(f'{self.score:05d}', True, (255, 255, 255))
        self.screen.blit(score_text, dest = (540, 5))

        
    def update_game(self):
        while not self.computer.output.empty():
            x = self.computer.output.get(True, 1)
            y = self.computer.output.get(True, 1)
            data = self.computer.output.get(True, 1)
            self.update_game_state((x,y), data)
        action = self.determine_action()
        self.computer.input.put(action)


    def game_loop(self):
        print('game loop started')
        done = False
        clock = pygame.time.Clock()
        while not done: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            clock.tick(60)
            try:
                if not self.computer.output.empty():
                    self.update_game()
                    self.draw_screen()
                    pygame.display.flip()
            except queue.Empty:
                print('output queue empty')
                done = True
            
            if self.computer.finished and self.computer.output.empty():
                done = True
        print('game loop stopped')

    def clear_board(self):
        self.board = {}

    def start_game(self, quarters=0):
        if quarters:
            self.computer.program[0] = quarters
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clear_board()
        game = threading.Thread(target=self.computer.run)
        game.start()
        self.game_loop()
        print('game finished')
        game.join()
        print('program thread joined')
        pygame.quit()


if __name__ == '__main__':
    arcade = Arcade(day13_input)

    arcade.start_game()
    blocks = [arcade.board[l] 
        for l in arcade.board.keys() 
        if arcade.board[l] == Tile.BLOCK]
    print(f"Part1: number of blocks is {len(blocks)}")
        
        
    arcade = Arcade(day13_input)
    arcade.start_game(quarters = 2)
    print(f"Part2: max score is {arcade.score}")
