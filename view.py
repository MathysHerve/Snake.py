import Snake


class Grid:

    def __init__(self, x, y, pyg, row=15, col=15, step=25):
        self._row = row
        self._col = col
        self._x = x
        self._y = y
        self._pygame = pyg
        self._step = step
        self._grid = []
        self._coords = []

        for i in range(15):
            for j in range(15):
                self._coords.append((x + (i * step), y + (j * step)))

        self._grid_coords = [self.coord_to_grid(coord[0], coord[1]) for coord in self._coords]

        self.gen_grid()

    # ==============================================================================
    #                                Initializing Blocks
    # ==============================================================================

    def gen_grid(self):
        """This block is what actually creates every rectangle to be drawn by the GUI"""
        for coordinate in self._coords:
            self._grid.append(
                [self._pygame.Rect([coordinate, tuple([self._step, self._step])]), None]
            )
        return self._grid

    # ==============================================================================
    #                                Get Blocks
    # ==============================================================================

    def get_center_of_grid(self, col, row):
        x, y = self.grid_to_coord(col, row)
        x += self._step // 2
        y += self._step // 2
        return x, y

    def get_coordinates(self):
        return self._x, self._y

    def get_size(self):
        width = (self._col * self._step)
        height = (self._row * self._step)
        return width, height

    def get_grid(self):
        return self._grid

    # ==============================================================================
    #                       Converting Blocks and Math Blocks
    # ==============================================================================

    def coord_to_grid(self, pos_x, pos_y):
        new_x = (self._x - 1) - pos_x
        new_y = (self._y - 1) - pos_y
        col = new_x // self._step
        row = new_y // self._step
        return abs(col) - 1, abs(row) - 1

    def grid_to_coord(self, col, row):
        new_x = self._x + (col * self._step)
        new_y = self._y + (row * self._step)
        return new_x, new_y

    def grid_to_index(self, col, row):
        return (row * self._col) + col

    def index_to_grid(self, index):
        return index % self._col, index // self._col

    def closest_grid_corner(self, pos_x, pos_y, second_best=False):
        """
        Seems complicated but it really just checks all corners near a point and returns
        the closest one.

        :param pos_x: x value to test
        :param pos_y: y value to test
        :param second_best: If you want the second best value instead of the best one
        :return: Coordinate Tuple
        """
        best_move = None

        col, row = self.coord_to_grid(pos_x, pos_y)
        moves = self.grid_to_coord(col, row), \
                self.grid_to_coord(col, row - 1), \
                self.grid_to_coord(col + 1, row), \
                self.grid_to_coord(col, row + 1), \
                self.grid_to_coord(col - 1, row)

        coord_vec = self._pygame.Vector2(pos_x, pos_y)
        moves = [self._pygame.Vector2(move) for move in moves]
        moves_distance = [move.distance_to(coord_vec) for move in moves]

        shortest_move = min(moves_distance)
        index_of_shortest_move = moves_distance.index(shortest_move)
        best_move = moves[index_of_shortest_move]

        if second_best:
            moves.pop(index_of_shortest_move)
            moves_distance.pop(index_of_shortest_move)
            next_shortest_move = min(moves_distance)
            index_of_next_shortest_move = moves_distance.index(next_shortest_move)
            second_best_move = moves[index_of_next_shortest_move]
            return second_best_move[0], second_best_move[1]

        return best_move[0], best_move[1]


class SnakeGUI:

    def __init__(self, pyg, grid, window_size=(600, 600), bg_color=(50, 150, 82)):
        self._pygame = pyg
        self._screen_size = self._pygame.Vector2(window_size)
        self._bg_color = bg_color
        self._screen = self._pygame.display.set_mode(window_size)
        self._new_rects = []
        self._scoreboard = 0

        self._alternate = False
        self._grid = grid

    def render(self):
        """Renders every thing to be actually seen on the GUI"""
        if self._new_rects:
            self._pygame.display.update(self._new_rects)
            self._new_rects = []
            self._alternate = False

    # ==============================================================================
    #                           Background and Board
    # ==============================================================================

    def create_all_background_objects(self):
        self.create_background()
        self.create_grid()

    def create_background(self):
        """Append the Background Image text for drawing"""
        bg = self._pygame.image.load('tree_background.jpg')

        self._new_rects.append(
            self._screen.blit(bg, (0, 0))
        )

    def create_grid(self):
        """
        Seems complicated but its just making each little grid and alternating
        their colors so it looks better
        """
        # A Grid is a list of lists. The lists contain [Rect, Object]
        # Where the Object is an optional player/item to draw.
        bg_x, bg_y, bg_width, bg_height = self._grid.get_coordinates()[0], self._grid.get_coordinates()[1], \
                                          self._grid.get_size()[0], self._grid.get_size()[1]

        width = 10
        extra_height = 30
        bg = self._pygame.Rect(bg_x - width, bg_y - width, bg_width + width * 2, bg_height + extra_height + width * 2)

        self._new_rects.append(
            self._pygame.draw.rect(self._screen, (58, 71, 45), bg, border_radius=width)
        )

        for grid_list in self._grid.get_grid():
            if self._alternate:
                self._new_rects.append(
                    self._pygame.draw.rect(self._screen, (115, 148, 15), grid_list[0])
                )
                self._alternate = False
            else:
                self._new_rects.append(
                    self._pygame.draw.rect(self._screen, (175, 224, 25), grid_list[0])
                )
                self._alternate = True

            if not grid_list[1] is None:
                self._new_rects.append(
                    self._pygame.draw.rect(self._screen, grid_list[1].get_color(), grid_list[1].to_rect())
                )

    # ==============================================================================
    #                             Scoreboard
    # ==============================================================================

    def create_score(self):
        """Append the Score text for drawing"""
        score = self._pygame.font.SysFont('calibri', 25)
        score_surface = score.render('Score: {}'.format(self._scoreboard), True, (255, 255, 255))
        self._new_rects.append(
            self._screen.blit(score_surface, (265, 483))
        )

    def increase_score(self):
        self._scoreboard += 1

    # ==============================================================================
    #                             Unique Screens
    # ==============================================================================

    def create_main_menu(self):
        bg_x, bg_y, bg_width, bg_height = self._grid.get_coordinates()[0], self._grid.get_coordinates()[1], \
                                          self._grid.get_size()[0], self._grid.get_size()[1]
        center = self._pygame.Vector2(self._screen_size.x/2, self._screen_size.y/2)
        menu_background = self._pygame.Rect(bg_x, bg_y, bg_width, bg_height)
        self._new_rects.append(
            self._pygame.draw.rect(self._screen, (100, 140, 90), menu_background)
        )

        snake_title = self._pygame.font.SysFont('Showcard Gothic', 100)
        snake_title_surface = snake_title.render('SNAKE', True, (220, 220, 220))
        self._new_rects.append(
            self._screen.blit(snake_title_surface, (center.x-snake_title_surface.get_size()[0]/2+2, bg_y+20))
        )

        fake_snake_shadow = self._pygame.image.load('snake_menu_shadow.png')
        self._new_rects.append(
            self._screen.blit(fake_snake_shadow, (self._screen_size.y/2 - 155, self._screen_size.y/2-150))
        )

        fake_snake = self._pygame.image.load('snake_menu.png')
        self._new_rects.append(
            self._screen.blit(fake_snake, (self._screen_size.y/2 - 158, self._screen_size.y/2-153))
        )

        instructions = self._pygame.font.SysFont('Peignot Medium', 30)
        instructions_surface = instructions.render('SPACE TO START', True, (220, 220, 220))
        self._new_rects.append(
            self._screen.blit(instructions_surface, (center.x-instructions_surface.get_size()[0]/2+6, self._screen_size.y/2+125))
        )

    def create_game_over(self):
        """Append the Game Over text for drawing"""
        game_over_text = self._pygame.font.SysFont('calibri', 75)
        game_over_shadow = self._pygame.font.SysFont('calibri', 75)
        game_over_surface = game_over_text.render('Game Over!', True, (255, 255, 255))
        game_over_shadow_surface = game_over_shadow.render('Game Over!', True, (33, 33, 33))
        game_over_coords = self._pygame.Vector2(self._screen_size.x / 2 + 3 - game_over_surface.get_size()[0] / 2,
                                                self._screen_size.y // 2 -
                                                game_over_surface.get_size()[1] / 2)
        self._new_rects.append(
            self._screen.blit(game_over_shadow_surface, game_over_coords.elementwise() + 3)
        )
        self._new_rects.append(
            self._screen.blit(game_over_surface, game_over_coords)
        )

    def create_debug_menu(self):
        """
        This is appending the debug menu for drawing, it just contains basic information about
        the mouse to help debug
        """
        mouseex, mousey = self._pygame.mouse.get_pos()

        mousex = self._pygame.font.SysFont('calibri', 12)
        gridx = self._pygame.font.SysFont('calibri', 12)
        coord = self._pygame.font.SysFont('calibri', 12)

        text_surface = mousex.render('mouse position ' + str(mouseex) + ' , ' + str(mousey), True, (255, 255, 255))
        text_surface2 = gridx.render('grid position ' + str(self._grid.coord_to_grid(mouseex, mousey)), True,
                                     (255, 255, 255))
        text_surface3 = coord.render('coord grid ' + str(
            self._grid.grid_to_coord(self._grid.coord_to_grid(mouseex, mousey)[0],
                                     self._grid.coord_to_grid(mouseex, mousey)[1])), True,
                                     (255, 255, 255))

        debug_zone = self._pygame.Vector2(tuple([self._screen_size.x, 15]))
        debug_zone2 = self._pygame.Vector2(tuple([self._screen_size.x, 30]))
        debug_zone3 = self._pygame.Vector2(tuple([self._screen_size.x, 45]))

        text_size = self._pygame.Vector2(text_surface.get_size())

        self._new_rects.append(
            self._screen.blit(text_surface, debug_zone - text_size)
        )
        self._new_rects.append(
            self._screen.blit(text_surface2, debug_zone2 - text_size)
        )
        self._new_rects.append(
            self._screen.blit(text_surface3, debug_zone3 - text_size)
        )

    # ==============================================================================
    #                               Objects
    # ==============================================================================

    def create_snake(self):
        """Appends snake for drawing"""
        for snake in Snake.Snake.current_snake:
            self._new_rects.append(
                self._pygame.draw.rect(self._screen, snake.get_color(), [self._pygame.Vector2(snake.get_coordinates()),
                                                                         self._pygame.Vector2(snake.get_dimensions())])
            )

    def create_apple(self):
        """Appends apple for drawing"""
        for apple in Snake.Apple.current_apple:
            self._new_rects.append(
                self._pygame.draw.rect(self._screen, apple.get_color(), [apple.get_coordinates(),
                                                                         apple.get_dimensions()])
            )
