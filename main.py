import pygame
from pygame.locals import *
from Snake import Snake, Apple
from view import SnakeGUI, Grid

pygame.init()

# I have no idea why these have to be at a module level but thats a problem for another time
cool_down = False
cool_down_max_tick = 20
cool_down_current_tick = 0


def start_cooldown(ticks=20):
    """
    How long to freeze Key presses

    :param ticks: length to freeze
    :return: bool
    """
    global cool_down
    global cool_down_max_tick
    if cool_down:
        return False
    else:
        cool_down_max_tick = ticks
        cool_down = True
        return True


def check_cooldown():
    """
    Used with start_cooldown() to check the progress of the cooldown, and add onto the time
    if necessary
    """
    global cool_down
    global cool_down_max_tick
    global cool_down_current_tick

    if cool_down:
        cool_down_current_tick += 1

        if cool_down_current_tick >= cool_down_max_tick:
            cool_down_current_tick = 0
            cool_down_max_tick = 20
            cool_down = False

def main():
    """
    This is the main game loop, all the objects are initialized before the loop and some basic
    conditions are created. Once the loop runs, it checks for events, and then all the game logic
    takes places.

    Controls: Arrow Keys: movement
              ESC: toggles the pause on the game
              ~: toggles debug menu
    """

    global cool_down

    # Create Gui, Clock, and Snake
    Holder = Grid(120, 100, pygame)
    GUI = SnakeGUI(pygame, Holder)
    fps = pygame.time.Clock()

    snake_spawn_x, snake_spawn_y = Holder.closest_grid_corner(145, 275)
    Snake(snake_spawn_x, snake_spawn_y, Holder)

    # Run conditions
    run = True
    debug = False
    supersonic = False
    sprint = False
    menu_loop = True

    while run:
        fps.tick(60)
        GUI.create_all_background_objects()
        head = Snake.current_snake[0]
        while menu_loop:
            GUI.create_all_background_objects()
            GUI.create_main_menu()
            GUI.render()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        menu_loop = False

        # Begin key handling
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
                break
            if event.type == KEYDOWN:
                if event.key == K_BACKQUOTE:
                    if debug:
                        debug = False
                    else:
                        debug = True

                if not cool_down:
                    if event.key == K_UP:
                        head.turn_snake(Snake.Directions.NORTH)

                    elif event.key == K_DOWN:
                        head.turn_snake(Snake.Directions.SOUTH)

                    elif event.key == K_RIGHT:
                        head.turn_snake(Snake.Directions.EAST)

                    elif event.key == K_LEFT:
                        head.turn_snake(Snake.Directions.WEST)

                    start_cooldown(11)

                    if event.key == K_ESCAPE:
                        paused = True
                        while paused:

                            for pause_event in pygame.event.get():
                                if pause_event.type == KEYDOWN:
                                    if pause_event.key == K_ESCAPE:
                                        paused = False
                                    if pause_event.key == K_BACKQUOTE:
                                        if debug:
                                            debug = False
                                        else:
                                            debug = True
                            GUI.create_snake()
                            GUI.create_score()
                            GUI.create_apple()
                            GUI.render()

        keys = pygame.key.get_pressed()
        if keys[K_LSHIFT]:
            sprint = True
        else:
            sprint = False

        check_cooldown()
        # End key handling

        # Handle the passive movement and checking if any distances are off

        debug_snake = []
        for s in Snake.current_snake[::-1]:
            if sprint:
                s.speed = 5
            else:
                s.speed = 2

            if s == Snake.current_snake[0]:
                s.follow(head=True)
            else:
                s.follow()
            debug_snake.append([str(s), s.difference()])
        debug_snake = []

        # Collision handling
        if head.is_collided():
            head.die()
            run = False

        # GUI Handling
        GUI.create_snake()

        if len(Apple.current_apple) > 0:
            GUI.create_apple()
        else:
            Apple.spawn_apple(Holder)
            GUI.create_apple()

        if debug:
            GUI.create_debug_menu()

        if head.ate_apple():
            GUI.increase_score()
            pass

        GUI.create_score()
        GUI.render()

    GUI.create_background()

    run = True
    replay = False
    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
                break
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    run = False
                    replay = True
                    break

        GUI.create_grid()
        GUI.create_snake()
        GUI.create_score()
        GUI.create_game_over()
        GUI.render()

    if replay:
        run = True
        Snake.current_snake = []
        Apple.current_apple = []
        main()
    else:
        pygame.quit()


if __name__ == '__main__':
    main()