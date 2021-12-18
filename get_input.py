import cfg
import pygame


def get_input():
    # todo: use mouse to control ship angle?
    # mouse_buttons = pygame.mouse.get_pressed()
    # mouse_position = pygame.mouse.get_pos()
    # mouse_rel = pygame.mouse.get_rel()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_LEFT:
                cfg.player_ship_rotation_thruster = 1
            elif event.key == pygame.K_RIGHT:
                cfg.player_ship_rotation_thruster = -1
            elif event.key == pygame.K_UP:
                cfg.player_ship_thrust = True
            elif event.key == pygame.K_SPACE:
                cfg.player_ship_firing = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                cfg.player_ship_rotation_thruster = 0
            elif event.key == pygame.K_UP:
                cfg.player_ship_thrust = False
            elif event.key == pygame.K_SPACE:
                cfg.player_ship_firing = False
    return True
