import cfg
import pygame
import math

f = cfg.FONT


def calc_screen_pos(self, poly):
    points_screen = []
    for point in range(len(poly)):
        point_ang = poly[point][0] + self.angle
        point_dis = poly[point][1]
        scale = self.scale
        x = self.pos[0] + math.sin(point_ang) * point_dis * scale
        y = self.pos[1] + math.cos(point_ang) * point_dis * scale
        points_screen.append((x, y))
    return points_screen


def calc_screen_pos_alien_ship(self):
    points_screen = []
    for point in range(len(self.points)):
        scale = self.scale
        x = self.pos[0] + self.points[point][0] * scale
        y = self.pos[1] + self.points[point][1] * scale
        points_screen.append((x, y))
    return points_screen


def spark_bit(surface, this_bit):
    rr, gg, bb = cfg.SCREEN_COLOR
    num = this_bit.die - pygame.time.get_ticks()
    den = this_bit.die - this_bit.born
    per = max(0, min(1, num / den))
    pygame.draw.circle(
        surface,
        [rr * per, gg * per, bb * per],
        (int(this_bit.pos[0]),
         int(this_bit.pos[1])), int(this_bit.size),
        1)


def rock(surface, this_rock):
    col = cfg.SCREEN_COLOR
    # make the rock appear on the other side before it's origin
    # todo: doses collision detect the 'other side' rock
    for xo in (-cfg.SCREEN_WIDTH, 0, cfg.SCREEN_WIDTH):
        for yo in (-cfg.SCREEN_HEIGHT, 0, cfg.SCREEN_HEIGHT):
            new_rock_points = []
            for p in range(len(this_rock.points_screen)):
                x, y = this_rock.points_screen[p]
                new_x = xo + x
                new_y = yo + y
                new_rock_points.append((new_x, new_y))
            pygame.draw.polygon(
                surface,
                col,
                new_rock_points,
                1)


def bullet(surface, this_bullet):
    x, y = this_bullet.pos
    pygame.draw.circle(
        surface,
        cfg.SCREEN_COLOR,
        (int(x), int(y)),
        cfg.BULLET_RADIUS,
        1)


def ship(surface, this_poly):
    # if cfg.show_ship:
    pygame.draw.polygon(
        surface,
        cfg.SCREEN_COLOR,
        this_poly,
        1)


def parked_ships(surface):
    for s in range(len(cfg.PARKED_SHIPS)):
        pygame.draw.polygon(
            surface,
            cfg.SCREEN_COLOR,
            cfg.PARKED_SHIPS[s].points_screen,
            1)


def start_screen(surface):
    font = pygame.font.SysFont(f, 20)
    characters = "Press FIRE to start"
    colour = cfg.SCREEN_COLOR
    text = font.render(characters, True, colour)
    x = (cfg.SCREEN_WIDTH - text.get_width()) / 2
    y = (cfg.SCREEN_HEIGHT - text.get_height()) / 4
    surface.blit(text, (x, y))
    show_scores(surface)


def show_scores(surface):
    font = pygame.font.SysFont(f, 20)
    colour = cfg.SCREEN_COLOR
    for s in range(len(cfg.hiscores)):
        sc = cfg.hiscores[s][0]
        if sc > 0:
            strsc = font.render(str(sc), True, colour)
            x = cfg.SCREEN_WIDTH / 2 - strsc.get_width() - 10
            y = cfg.SCREEN_HEIGHT / 4 + (s + 1) * 30
            surface.blit(strsc, (x, y))

            who = font.render(cfg.hiscores[s][1], True, colour)
            x = cfg.SCREEN_WIDTH / 2 + 10
            y = cfg.SCREEN_HEIGHT / 4 + (s + 1) * 30
            surface.blit(who, (x, y))


def game_over(surface):
    font = pygame.font.SysFont(f, 20)
    characters = "Game Over !"
    colour = cfg.SCREEN_COLOR
    text = font.render(characters, True, colour)
    x = (cfg.SCREEN_WIDTH - text.get_width()) / 2
    y = (cfg.SCREEN_HEIGHT - text.get_height()) / 4
    surface.blit(text, (x, y))
    show_scores(surface)


def score(surface):
    font = pygame.font.SysFont(f, 20)
    characters = "Score: " + str(cfg.SCORE)
    colour = cfg.SCREEN_COLOR
    text = font.render(characters, True, colour)
    x = 0
    y = 0
    surface.blit(text, (x, y))


def debug(surface, x, y, txt):
    font = pygame.font.SysFont(f, 20)
    characters = txt
    colour = [255, 255, 255]
    text = font.render(characters, True, colour)
    surface.blit(text, (x, y))
