import turtle
import random
import time

class ArcadeGame:
    def __init__(self):
        self.WINDOW_DIMENSION = 1024
        self.GRID_DIMENSION = 25
        self.BLOCK_SIZE = 32
        self.ENEMY_COUNT = 5
        self.PATH_PROBABILITY = 0.8
        self.PLAYER_SPEED = self.BLOCK_SIZE
        self.FRAME_DELAY = 100  # ms
        self.UPDATE_INTERVAL = 0.1

        self.active = True
        self.showing_intro = True
        self.animation_frame = 0
        self.enemy_step_timer = 0
        self.enemy_step_interval = 3

        self.grid = [[1] * self.GRID_DIMENSION for _ in range(self.GRID_DIMENSION)]

        self.display = self.initialize_display()
        self.load_resources()

        self.barriers = []
        self.collectibles = []
        self.ghosts = []
        self.player = None

    def initialize_display(self):
        display = turtle.Screen()
        display.setup(self.WINDOW_DIMENSION, self.WINDOW_DIMENSION)
        display.title("ARCADE ADVENTURE")
        display.tracer(0)
        return display

    def load_resources(self):
        self.player_sprites = ["pngwing.com.gif", "pngwing.com.gif"]
        self.collectible_sprites = ["dot1.gif", "dot2.gif"]
        self.ghost_sprites = ["blue-pacman.gif", "pink-pacman.gif",
                            "red-pacman.gif", "pink-pacman.gif"]
        self.end_screens = ["tryagain1.gif", "youwin.gif", "gameover.gif"]

        for sprite in self.player_sprites + self.collectible_sprites + \
                     self.ghost_sprites + self.end_screens:
            self.display.addshape(sprite)

    def configure_input(self):
        self.display.listen()
        direction_map = {
            "Left": "left",
            "Right": "right",
            "Up": "up",
            "Down": "down"
        }
        for key, direction in direction_map.items():
            self.display.onkeypress(lambda d=direction: self.update_player_direction(d), key)

    def update_player_direction(self, direction):
        if self.active:
            self.player.next_direction = direction

    def display_intro(self):
        logo = turtle.Turtle()
        logo.hideturtle()
        logo.penup()
        logo.goto(0, 0)
        self.display.addshape("logo.gif")
        logo.shape("logo.gif")
        logo.showturtle()

        play_button = turtle.Turtle()
        play_button.hideturtle()
        play_button.penup()
        play_button.goto(0, -150)
        self.display.addshape("clicktostart.gif")
        play_button.shape("clicktostart.gif")
        play_button.showturtle()

        def begin_game(*args):
            logo.hideturtle()
            play_button.hideturtle()
            self.display.bgpic("nopic")
            self.display.bgcolor("#D1EFFF")
            self.showing_intro = False

        self.display.onclick(begin_game)
        self.display.onkey(begin_game, "Up")
        self.display.onkey(begin_game, "space")

    def create_maze(self):
        self.grid = [[1] * self.GRID_DIMENSION for _ in range(self.GRID_DIMENSION)]
        moves = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        path_stack = [(1, 1)]
        explored = {(1, 1)}

        while path_stack:
            curr_x, curr_y = path_stack[-1]
            self.grid[curr_y][curr_x] = 0
            random.shuffle(moves)
            moved = False

            for dx, dy in moves:
                next_x, next_y = curr_x + dx, curr_y + dy
                if (1 <= next_x < self.GRID_DIMENSION - 1 and
                    1 <= next_y < self.GRID_DIMENSION - 1 and
                    (next_x, next_y) not in explored):
                    self.grid[curr_y + dy // 2][curr_x + dx // 2] = 0
                    self.grid[next_y][next_x] = 0
                    explored.add((next_x, next_y))
                    path_stack.append((next_x, next_y))
                    moved = True
                    break

            if not moved:
                path_stack.pop()

            if random.random() < self.PATH_PROBABILITY:
                for dx, dy in moves:
                    next_x, next_y = curr_x + dx, curr_y + dy
                    if (1 <= next_x < self.GRID_DIMENSION - 1 and
                        1 <= next_y < self.GRID_DIMENSION - 1 and
                        self.grid[next_y][next_x] == 1):
                        self.grid[curr_y + dy // 2][curr_x + dx // 2] = 0
                        self.grid[next_y][next_x] = 0
                        break

        for y in range(self.GRID_DIMENSION):
            for x in range(self.GRID_DIMENSION):
                if self.grid[y][x] == 0 and x > 1 and y > 1 and random.random() < 0.6:
                    self.grid[y][x] = 2

    def spawn_ghost(self, index):
        enemy = turtle.Turtle()
        enemy.shape(self.ghost_sprites[index])
        enemy.shapesize(0.5, 0.5)
        enemy.color("#8E6BE6")
        enemy.penup()
        enemy.speed(0)

        while True:
            x = random.randint(4, self.GRID_DIMENSION - 2)
            y = random.randint(4, self.GRID_DIMENSION - 2)
            if self.grid[y][x] == 0:
                pos_x = -384 + (x * self.BLOCK_SIZE)
                pos_y = 384 - (y * self.BLOCK_SIZE)
                enemy.goto(pos_x, pos_y)
                break
        return enemy

    def spawn_player(self):
        player = turtle.Turtle()
        player.shape(self.player_sprites[0])
        player.penup()
        player.speed(0)
        player.goto(-352, 352)
        player.current_direction = "Stop"
        player.next_direction = "Stop"
        return player

    def render_grid(self):
        for y in range(self.GRID_DIMENSION):
            for x in range(self.GRID_DIMENSION):
                pos_x = -384 + (x * self.BLOCK_SIZE)
                pos_y = 384 - (y * self.BLOCK_SIZE)

                if self.grid[y][x] == 1:
                    barrier = turtle.Turtle()
                    barrier.shape("square")
                    barrier.color("#93c1ff")
                    barrier.shapesize(stretch_wid=(self.BLOCK_SIZE-4)/20,
                                    stretch_len=(self.BLOCK_SIZE-4)/20)
                    barrier.penup()
                    barrier.goto(pos_x, pos_y)
                    self.barriers.append(barrier)

                elif self.grid[y][x] == 2:
                    item = turtle.Turtle()
                    item.shape(random.choice(self.collectible_sprites))
                    item.color("#FE696C")
                    item.shapesize(0.5, 0.5)
                    item.penup()
                    item.goto(pos_x, pos_y)
                    self.collectibles.append(item)

    def check_barrier_collision(self, x, y):
        return any(barrier.distance(x, y) < self.BLOCK_SIZE for barrier in self.barriers)

    def handle_collectibles(self):
        for item in self.collectibles[:]:
            if self.player.distance(item) < 22:
                item.hideturtle()
                self.collectibles.remove(item)

    def update_ghosts(self):
        self.enemy_step_timer += 1
        if self.enemy_step_timer < self.enemy_step_interval:
            return
        self.enemy_step_timer = 0

        for ghost in self.ghosts:
            options = [
                (ghost.xcor() + self.BLOCK_SIZE, ghost.ycor()),
                (ghost.xcor() - self.BLOCK_SIZE, ghost.ycor()),
                (ghost.xcor(), ghost.ycor() + self.BLOCK_SIZE),
                (ghost.xcor(), ghost.ycor() - self.BLOCK_SIZE)
            ]
            random.shuffle(options)
            for next_x, next_y in options:
                if not self.check_barrier_collision(next_x, next_y):
                    ghost.goto(next_x, next_y)
                    break

    def update_player(self):
        if not self.active:
            return

        x, y = self.player.xcor(), self.player.ycor()
        direction = self.player.next_direction

        if direction == "left":
            x -= self.PLAYER_SPEED
        elif direction == "right":
            x += self.PLAYER_SPEED
        elif direction == "up":
            y += self.PLAYER_SPEED
        elif direction == "down":
            y -= self.PLAYER_SPEED
        elif direction == "Stop":
            self.player.current_direction = "Stop"
            return

        if not self.check_barrier_collision(x, y):
            self.player.goto(x, y)
            self.player.current_direction = direction
        else:
            self.player.current_direction = "Stop"

    def animate_player(self):
        if self.active:
            if self.player.current_direction != "Stop":
                self.animation_frame = (self.animation_frame + 1) % len(self.player_sprites)
            else:
                self.animation_frame = 0
            self.player.shape(self.player_sprites[self.animation_frame])
            self.display.ontimer(self.animate_player, self.FRAME_DELAY)

    def check_game_state(self):
        if any(self.player.distance(ghost) < 22 for ghost in self.ghosts):
            time.sleep(1.7)
            self.display_end("Game Over!")
            return True

        if not self.collectibles:
            time.sleep(1.7)
            self.display_end("You Win!")
            return True
        return False

    def display_end(self, result):
        self.active = False
        for entity in self.collectibles + self.barriers + self.ghosts + [self.player]:
            entity.hideturtle()

        end_display = turtle.Turtle()
        end_display.hideturtle()
        end_display.penup()

        if result == "You Win!":
            end_display.goto(40, 0)
            end_display.shape("youwin.gif")
        else:
            end_display.goto(25, -100)
            end_display.shape("gameover.gif")
        end_display.showturtle()

        retry = turtle.Turtle()
        retry.penup()
        retry.goto(10, -150)
        retry.shape("tryagain1.gif")
        retry.showturtle()

        def restart(*args):
            if not self.active:
                end_display.hideturtle()
                retry.hideturtle()
                self.initialize_new_game()

        self.display.onclick(restart)
        self.display.onkey(restart, "space")

    def initialize_new_game(self):
        self.active = True
        self.display.bgpic("nopic")

        for entity in self.collectibles + self.barriers + self.ghosts + ([self.player] if self.player else []):
            entity.hideturtle()

        self.barriers.clear()
        self.collectibles.clear()
        self.ghosts.clear()

        self.create_maze()
        self.render_grid()
        self.player = self.spawn_player()
        self.configure_input()

        for i in range(self.ENEMY_COUNT):
            self.ghosts.append(self.spawn_ghost(i % len(self.ghost_sprites)))

        self.enemy_step_timer = 0
        self.animation_frame = 0
        self.animate_player()
        self.display.tracer(0)

    def start(self):
        self.display_intro()
        while self.showing_intro:
            self.display.update()
            time.sleep(0.01)

        self.create_maze()
        self.render_grid()
        self.player = self.spawn_player()
        self.configure_input()

        for i in range(self.ENEMY_COUNT):
            self.ghosts.append(self.spawn_ghost(i % len(self.ghost_sprites)))

        self.animate_player()

        while True:
            try:
                if self.active:
                    self.update_ghosts()
                    self.update_player()
                    self.handle_collectibles()
                    if self.check_game_state():
                        continue
                self.display.update()
                time.sleep(self.UPDATE_INTERVAL)
            except turtle.Terminator:
                break

if __name__ == "__main__":
    game = ArcadeGame()
    game.start()
