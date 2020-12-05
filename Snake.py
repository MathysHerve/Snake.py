from enum import Enum, auto
import random
import pygame


class Apple:
    current_apple = []

    def __init__(self, x, y, grid, color=(219, 30, 9), width=10, height=10):
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height
        self.grid = grid
        Apple.current_apple.append(self)

    @classmethod
    def spawn_apple(cls, grid, width=10, height=10):
        """
        Places apple on a random available coordinate

        :param grid: the Holder
        :param width: width of the apple
        :param height: height of the apple
        :return: Apple object
        """
        coords = [s.get_coordinates() for s in Snake.current_snake]
        taken_grid_coords = [grid.coord_to_grid(coord[0], coord[1]) for coord in coords]
        available_grid = [grid_coord for grid_coord in grid._grid_coords if grid_coord not in taken_grid_coords]

        rand_col, rand_row = random.choice(available_grid)
        rand_x, rand_y = grid.get_center_of_grid(rand_col, rand_row)

        rand_x = rand_x - width / 2
        rand_y = rand_y - height / 2
        return Apple(rand_x, rand_y, grid)

    def to_rect(self):
        # Returns a Rect with location and size information
        return pygame.Rect(self.get_coordinates(), self.get_dimensions())

    def get_color(self):
        """Returns Color"""
        return self.color

    def get_coordinates(self):
        """Returns Apple's coordinates"""
        return self.x, self.y

    def get_dimensions(self):
        """Returns Apple's width"""
        return self.width, self.height


class Snake:
    current_snake = []  # List of Snake objects (Essentially the whole Snake is in here)
    turn_queue = []  # All of the turns for the head only.

    class Decorators:
        @classmethod
        def queue(cls, func):
            def wrapper(cls, direction):
                if cls == Snake.current_snake[-1]:
                    func(cls, direction)
                else:
                    cls.queue.append([cls.get_coordinates(), direction])
                    func(cls, direction)

            return wrapper

    class Directions(Enum):
        # An attempt at Enum lol
        NORTH = auto()
        EAST = auto()
        SOUTH = auto()
        WEST = auto()

    def __init__(self, x, y, grid, direction=Directions.EAST, speed=2, width=25, height=25, color=(0, 140, 255),
                 idle=False, dead=False):
        # initialize arguments
        self.x = x
        self.y = y
        self.grid = grid
        self.direction = direction
        self.speed = speed
        self.width = width
        self.height = height
        self.color = color
        self.idle = idle
        self.dead = dead

        # Handling idle
        self.idle_pixels = 0
        self.max_idle_pixels = 0

        # Misc
        self._length = len(Snake.current_snake)

        self._directions_loop = [Snake.Directions.NORTH, Snake.Directions.EAST,
                                 Snake.Directions.SOUTH, Snake.Directions.WEST]
        self.queue = []

        # add to current snake
        self._position = len(self.current_snake)
        Snake.current_snake.append(self)
        if self is not Snake.current_snake[0]:
            self.idle_snake(self.width)

    # ==============================================================================
    #                     Simple blocks to keep the code clean
    # ==============================================================================

    def __str__(self):
        """Method to define how a Snake is printed to the Console."""
        return '<Snake at position:' + str(self._position) + '>'

    def to_rect(self):
        """Converts the Snake object into a Rect object"""
        # Returns a Rect with location and size information
        return pygame.Rect(self.get_coordinates(), self.get_dimensions())

    def get_color(self):
        """Returns Color"""
        return self.color

    def get_coordinates(self):
        """Returns Snake's coordinates"""
        return [self.x, self.y]

    def get_direction(self):
        """Returns current direction"""
        return self.direction

    def get_dimensions(self):
        """Returns Snake's width, height"""
        return self.width, self.height

    # ==============================================================================
    #                             Increasing Length
    # ==============================================================================

    def add_length(self):
        """Appends SnakeBody to the current snake for drawing."""
        tail = self
        x, y = tail.get_coordinates()
        adjust = 0
        add_length_commands = {
            Snake.Directions.NORTH: lambda: Snake(x, y + adjust, self.grid,
                                                  speed=self.speed,
                                                  direction=tail.get_direction(),
                                                  color=(self.get_color())),
            Snake.Directions.SOUTH: lambda: Snake(x, y - adjust, self.grid,
                                                  speed=self.speed,
                                                  direction=tail.get_direction(),
                                                  color=(self.get_color())),
            Snake.Directions.EAST: lambda: Snake(x - adjust, y, self.grid,
                                                 speed=self.speed,
                                                 direction=tail.get_direction(),
                                                 color=(self.get_color())),
            Snake.Directions.WEST: lambda: Snake(x + adjust, y, self.grid,
                                                 speed=self.speed,
                                                 direction=tail.get_direction(),
                                                 color=(self.get_color()))
        }

        add_length_commands[tail.get_direction()]()

    # ==============================================================================
    #                             Movement Blocks
    # ==============================================================================

    def move_forward(self, speed):
        """
        Checks direction, then moves a [speed] amount of pixels

        :param speed: How many pixels to move forward
        """
        if self.direction == Snake.Directions.NORTH:
            self.y -= speed
        elif self.direction == Snake.Directions.SOUTH:
            self.y += speed
        elif self.direction == Snake.Directions.EAST:
            self.x += speed
        elif self.direction == Snake.Directions.WEST:
            self.x -= speed
        else:
            print('Error')

    @Decorators.queue
    def change_directions(self, direction):
        """
        Changes direction and removes the turn from the queue

        The decorator is used to save every turn done and it's location so that the Snake pieces that
        follow know when and how to turn.

        :param direction: direction to go in
        """
        if self.can_turn(direction):
            self.direction = direction
        else:
            if self.queue:
                self.queue.pop()

    def turn_snake(self, direction):
        """
        In contrast to change_direction, this function is for the head. turn_snake() does not actually
        change the direction immediately, it only appends it to the head's queue of commands.

        :param direction:
        """
        if self.can_turn(direction):
            closest_corner = self.get_closest_corner()[0:2]
            passed_info = self.passed(self, pygame.Vector2(closest_corner))
            if passed_info[0]:
                if abs(passed_info[1]) > 8:
                    Snake.turn_queue.append([self.grid.closest_grid_corner(self.get_coordinates()[0],
                                                                           self.get_coordinates()[1],
                                                                           second_best=True), direction])
                    return False

            Snake.turn_queue.append([closest_corner, direction])

    def follow(self, head=False):

        """
        Moves SnakeBody to coordinates of the SnakeBody/SnakeHead in front of it

        I'm going to be honest,this function is complicated, when any piece of Snake turns,
        that specific piece saves the turn to its "queue"

        The whole point of follow() is to check the queue of the piece in front of it, and execute
        the turn at the right spot.

        :param head: If the current object is the first Snake created
        :return: bool

        """
        follow_queue = None
        snake_ahead = self.current_snake[self._position - 1]

        # If snake is idle, stop the function and continue idling
        if self.idle:
            self.idle_snake()
            return False

        # The head needs to check a different queue of commands
        if head:
            follow_queue = Snake.turn_queue
        else:
            follow_queue = snake_ahead.queue

        # Regardless of the type of queue the snake must execute the rest of the code
        if follow_queue:
            # This function is used to teleport the snake to the right spot in case it screws up
            def go_to_last_coord():
                self.x, self.y = follow_queue[0][0]
                self.change_directions(follow_queue[0][1])
                follow_queue.pop(0)

            self.move_forward(self.speed)
            self_vector = pygame.Vector2(self.get_coordinates())
            ahead_vector = pygame.Vector2(follow_queue[0][0])  # this is just where the next instruction is

            if self_vector - ahead_vector == 0:
                go_to_last_coord()

            # Checking if the Snake passed its destination, it knows how far it missed it by so it just moves back
            # and moves in the right direction instead.
            passed_info = self.passed(self, ahead_vector)
            if passed_info[0]:
                self.move_forward(-abs(passed_info[-1]))
                go_to_last_coord()
                self.move_forward(abs(passed_info[1]))

            return True

        # If the queue is empty, just move forward
        else:
            self.move_forward(self.speed)
            return True

    # ==============================================================================
    #                           Movement Helper Blocks
    # ==============================================================================

    def can_turn(self, direction):
        """
        Checks if you're trying to turn the Snake into itself

        :param direction: a direction to check
        :return: bool
        """
        indx = self._directions_loop.index(self.direction)
        if indx == len(self._directions_loop) - 1:
            turn_left = self._directions_loop[indx - 1]
            turn_right = self._directions_loop[0]
        else:
            turn_left = self._directions_loop[indx - 1]
            turn_right = self._directions_loop[indx + 1]

        if direction == turn_left or direction == turn_right:
            return True

        else:
            return False

    def get_closest_corner(self):
        """
        Finds closest corner's coordinates

        :return: tup of coordinates
        """
        return self.grid.closest_grid_corner(self.get_coordinates()[0], self.get_coordinates()[1])

    def idle_snake(self, pixels=0):
        """
        idle_snake is used to spawn a new tail inside of the last one and allow it to wait a certain
        amount of pixels

        :param pixels: Amount of pixels to wait
        """
        self.idle = True
        if pixels != 0:
            self.max_idle_pixels += pixels

        self.idle_pixels += self.speed

        if self.idle_pixels >= self.max_idle_pixels:
            dead_pixel = self.idle_pixels - self.max_idle_pixels
            temp = self.speed
            self.speed = dead_pixel - temp
            self.move_forward(self.speed)

            self.speed = temp
            self.idle = False
            self.idle_pixels = 0
            self.max_idle_pixels = 0

    @staticmethod
    def passed(s, other_vect):
        """
        Static method to check if a snake has went passed a coordinate
        (It's static because it might be useful in other areas, but it was not incorporated)

        :param s: Snake Object
        :param other_vect: Pygame Vector2 Object
        :return: bool
        """
        self_vect = pygame.Vector2(s.get_coordinates())
        vec_diff = self_vect - other_vect

        if s.get_direction() == Snake.Directions.EAST:
            """ Check if last vector x is equal to 0 or greater than 0"""
            if vec_diff.x > 0:
                return True, vec_diff.x
            else:
                return False, vec_diff.x
        elif s.get_direction() == Snake.Directions.WEST:
            """ Check if last vector x is equal to 0 or less than 0"""
            if vec_diff.x < 0:
                return True, vec_diff.x
            else:
                return False, vec_diff.x
        elif s.get_direction() == Snake.Directions.NORTH:
            """ Check if last vector y is equal to 0 or less than 0"""
            if vec_diff.y < 0:
                return True, vec_diff.y
            else:
                return False, vec_diff.y
        elif s.get_direction() == Snake.Directions.SOUTH:
            """ Check if last vector y is equal to 0 or greater than 0"""
            if vec_diff.y > 0:
                return True, vec_diff.y
            else:
                return False, vec_diff.y
        else:
            return False, vec_diff

    def difference(self):
        """
        Distance between the current snake and the one behind it.

        :return: pygame.Vector2 of distance
        """
        try:
            prev_snake_index = Snake.current_snake.index(self) + 1
            prev_snake = Snake.current_snake[prev_snake_index]
            self_vector = pygame.Vector2(self.get_coordinates())
            previous_vector = pygame.Vector2(prev_snake.get_coordinates())
            return self_vector.distance_to(previous_vector)

        except IndexError:
            pass

    def check_distance(self):
        """
        Idle's snake if it is too far from it's target
        """

        if self.difference() is not None:
            if self.difference() > self.width:
                self.idle_snake(int(self.difference() - self.width))

    # ==============================================================================
    #                             Collision Blocks
    # ==============================================================================

    def is_collided(self):
        """
        Essentially handles all collisions, excluding eating an apple. It checks if the Snake is running into
        itself or out of bounds

        :return: bool
        """
        g_width, g_height = self.grid.get_size()
        g_x, g_y = self.grid.get_coordinates()

        out_of_bound_conditions = [lambda s: s.get_coordinates()[0] + s.get_dimensions()[0] > g_x + g_width,
                                   lambda s: s.get_coordinates()[0] < g_x,
                                   lambda s: s.get_coordinates()[1] < g_y,
                                   lambda s: s.get_coordinates()[1] + s.get_dimensions()[1] > g_y + g_height]

        if self == Snake.current_snake[0]:
            collided = self.to_rect().collidelist([s.to_rect() for s in Snake.current_snake[3:]])

            if collided == -1 and not any([condition(self) for condition in out_of_bound_conditions]):
                return False
            else:
                return True

    def ate_apple(self):
        """
        Apple collision to handle adding and removing apples from the board.

        :return: bool
        """
        if self == Snake.current_snake[0]:
            ate = self.to_rect().collidelist([a.to_rect() for a in Apple.current_apple])
            if ate != -1:
                Apple.current_apple.pop()
                Snake.current_snake[-1].add_length()
                Apple.spawn_apple(self.grid)
                return True
            else:
                return False

    def die(self):
        self.dead = True

    # ==============================================================================
    #                                     Fun!
    # ==============================================================================

    def super_sonic(self):
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))