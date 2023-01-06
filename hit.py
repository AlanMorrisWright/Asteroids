import cfg
import rock
import random
import math
import pygame
import calcscreen

# TODO: is there any boxing limits for efficiency?
'''
circle - poly
   player bullet
 1     rock         player_bullet_rock         71
 2     alien ship   player_bullet_alien_ship   86
   alien bullet
 3     rock         alien_bullet_rock         104
 4     player ship  alien_bullet_player_ship  115

poly - poly
   player ship
 5     rock         player_ship_rock          125
 6     alien ship
   alien ship
 7     rock        
'''


class Spark(object):
    def __init__(self, pos, vel_x, vel_y):
        self.pos = list(pos)
        self.size = random.uniform(1, 3)
        angle = random.uniform(0, 2 * math.pi)
        bit_vel = random.uniform(0, 100)
        vel_x += bit_vel * math.sin(angle)
        vel_y += bit_vel * math.cos(angle)
        self.vel = (vel_x, vel_y)
        self.born = pygame.time.get_ticks()
        self.die = self.born + random.randint(10, 5000)  # todo


def add_sparks(pos, vel_x, vel_y, n):
    for i in range(n):
        cfg.SPARKS.append(Spark(pos, vel_x / 2, vel_y / 2))


def move_sparks():
    some_bits = False
    if len(cfg.SPARKS):
        for i in range(len(cfg.SPARKS) - 1, -1, -1):
            if pygame.time.get_ticks() >= cfg.SPARKS[i].die:
                del cfg.SPARKS[i]
            else:
                some_bits = True
                cfg.SPARKS[i].pos[0] += cfg.SPARKS[i].vel[0] / cfg.ACTUAL_FPS
                cfg.SPARKS[i].pos[1] += cfg.SPARKS[i].vel[1] / cfg.ACTUAL_FPS

                if cfg.SPARKS[i].pos[0] < 0:
                    cfg.SPARKS[i].pos[0] += cfg.SCREEN_WIDTH
                if cfg.SPARKS[i].pos[1] < 0:
                    cfg.SPARKS[i].pos[1] += cfg.SCREEN_HEIGHT

                if cfg.SPARKS[i].pos[0] > cfg.SCREEN_WIDTH:
                    cfg.SPARKS[i].pos[0] -= cfg.SCREEN_WIDTH
                if cfg.SPARKS[i].pos[1] > cfg.SCREEN_HEIGHT:
                    cfg.SPARKS[i].pos[1] -= cfg.SCREEN_HEIGHT

                calcscreen.spark_bit(cfg.surface, cfg.SPARKS[i])
    return some_bits


def alien_bullet_ship():
    if cfg.PLAYER_SHIP:
        bullets = cfg.ALIEN_BULLETS
        ship = cfg.PLAYER_SHIP
        b, u = check_collision_bullet_ship(bullets, ship)
        if b > -1:
            add_sparks(ship[0].pos,
                       ship[0].vel[0],
                       ship[0].vel[1],
                       50)
            del bullets[b]
            score = ship[0].score
            del ship[u]
            cfg.sound_rock_hit.play()
            cfg.PLAYER_STATUS = 'ship died'
            cfg.GAME_STATUS_WHEN = pygame.time.get_ticks()
            cfg.player_ship_thrust = False
            cfg.playing_thrust_sound = False


def player_bullet_ship():
    bullets = cfg.PLAYER_BULLETS
    ship = cfg.ALIEN_SHIP
    b, u = check_collision_bullet_ship(bullets, ship)
    if b > -1:
        add_sparks(ship[0].pos,
                   ship[0].vel[0],
                   ship[0].vel[1],
                   50)
        del bullets[b]
        score = ship[0].score
        del ship[u]
        cfg.sound_rock_hit.play()
        return score
    return 0


def bullet_rock(bullets):
    b, r = check_collision_bullet_rocks(bullets)
    if b > -1:
        del bullets[b]
        add_sparks(cfg.ROCKS[r].pos, 0, 0, 7)
        score = cfg.ROCKS[r].score
        rock.split_rock(r)
        cfg.sound_rock_hit.play()
        return score
    return 0


def ship_rock(ship):
    if len(ship) > 0:
        for l1 in range(len(ship[0].points_screen)):
            l1p1x, l1p1y = ship[0].points_screen[l1]
            l1p2x, l1p2y = ship[0].points_screen[(l1 - 1)]
            for r in range(len(cfg.ROCKS)):
                for l2 in range(len(cfg.ROCKS[r].points_screen)):
                    l2p1x, l2p1y = cfg.ROCKS[r].points_screen[l2]
                    l2p2x, l2p2y = cfg.ROCKS[r].points_screen[(l2 - 1)]
                    if line_line_hit(l1p1x, l1p1y, l1p2x, l1p2y, l2p1x, l2p1y, l2p2x, l2p2y):
                        add_sparks(ship[0].pos,
                                   ship[0].vel[0],
                                   ship[0].vel[1],
                                   50)
                        cfg.sound_rock_hit.play()
                        return r
    return -1


def alien_ship_rock():
    r = ship_rock(cfg.ALIEN_SHIP)
    if r > -1:
        rock.split_rock(r)
        del cfg.ALIEN_SHIP[0]
    return 0


def player_ship_rock():
    if cfg.show_ship:
        r = ship_rock(cfg.PLAYER_SHIP)
        if r > -1:
            cfg.PLAYER_STATUS = 'ship died'
            cfg.GAME_STATUS_WHEN = pygame.time.get_ticks()
            score = cfg.ROCKS[r].score
            rock.split_rock(r)
            cfg.control_play_ship = False
            cfg.show_ship = False
            cfg.player_ship_thrust = False
            cfg.playing_thrust_sound = False
            cfg.sound_thruster.fadeout(200)
            del cfg.PLAYER_SHIP[0]
            return score
    return 0


def check_collision_bullet_rocks(bullets):
    if not bullets:
        return -1, -1
    for b in range(len(bullets)):
        bx, by = bullets[b].pos
        bpx = bx - (bullets[b].vel[0] / cfg.ACTUAL_FPS)
        bpy = by - (bullets[b].vel[1] / cfg.ACTUAL_FPS)
        for r in range(len(cfg.ROCKS)):
            # TODO: boxing here
            # min dis needs to be sum off
            #     rock radius
            #     bullet radius
            #     distance bullet can travel in 1 refresh
            min_dis = cfg.ROCK_RADIUS_MAX + cfg.BULLET_RADIUS + cfg.BULLET_VEL / cfg.ACTUAL_FPS
            dis_x = abs(bx - cfg.ROCKS[r].pos[0])
            dis_y = abs(by - cfg.ROCKS[r].pos[1])
            if dis_x > min_dis or dis_y > min_dis:
                pass
            else:
                for p in range(len(cfg.ROCKS[r].points_screen)):
                    p1x, p1y = cfg.ROCKS[r].points_screen[p]
                    p2x, p2y = cfg.ROCKS[r].points_screen[(p - 1)]
                    if line_circle_hit(bx, by, cfg.BULLET_RADIUS, p1x, p1y, p2x, p2y):
                        return b, r
                    if line_line_hit(bx, by, bpx, bpy, p1x, p1y, p2x, p2y):
                        return b, r
    return -1, -1


def check_collision_bullet_ship(bullets, ship):
    if not bullets:
        return -1, -1
    for b in range(len(bullets)):
        bx, by = bullets[b].pos
        bpx = bx - (bullets[b].vel[0] / cfg.ACTUAL_FPS)
        bpy = by - (bullets[b].vel[1] / cfg.ACTUAL_FPS)
        for u in range(len(ship)):
            for l1 in range(len(ship[u].points_screen)):
                l1p1x, l1p1y = ship[u].points_screen[l1]
                l1p2x, l1p2y = ship[u].points_screen[(l1 - 1)]
                if line_circle_hit(bx, by, cfg.BULLET_RADIUS, l1p1x, l1p1y, l1p2x, l1p2y):
                    return b, u
                if line_line_hit(bx, by, bpx, bpy, l1p1x, l1p1y, l1p2x, l1p2y):
                    return b, u
    return -1, -1


def ship_ship():
    if cfg.PLAYER_SHIP and cfg.ALIEN_SHIP:
        ship1 = cfg.PLAYER_SHIP[0]
        ship2 = cfg.ALIEN_SHIP[0]
        for l1 in range(len(ship1.points_screen)):
            l1p1x, l1p1y = ship1.points_screen[l1]
            l1p2x, l1p2y = ship1.points_screen[(l1 - 1)]
            for l2 in range(8):
                l2p1x, l2p1y = ship2.points_screen[l2]
                l2p2x, l2p2y = ship2.points_screen[(l2 - 1)]
                if line_line_hit(l1p1x, l1p1y, l1p2x, l1p2y, l2p1x, l2p1y, l2p2x, l2p2y):
                    add_sparks(ship1.pos, ship1.vel[0], ship1.vel[1], 50)
                    add_sparks(ship2.pos, ship2.vel[0], ship2.vel[1], 50)
                    cfg.sound_rock_hit.play()
                    score = cfg.ALIEN_SHIP[0].score
                    del cfg.ALIEN_SHIP[0]
                    del cfg.PLAYER_SHIP[0]
                    cfg.PLAYER_STATUS = 'ship died'
                    cfg.GAME_STATUS_WHEN = pygame.time.get_ticks()
                    return score
    return 0


def line_line_hit(l1p1x, l1p1y, l1p2x, l1p2y, l2p1x, l2p1y, l2p2x, l2p2y):
    x1 = (l1p1x * l1p2y - l1p1y * l1p2x) * (l2p1x - l2p2x) - (l1p1x - l1p2x) * (l2p1x * l2p2y - l2p1y * l2p2x)
    x2 = (l1p1x - l1p2x) * (l2p1y - l2p2y) - (l1p1y - l1p2y) * (l2p1x - l2p2x)
    if x2 != 0:
        x = x1 / x2
        if max(l1p1x, l1p2x) >= x >= min(l1p1x, l1p2x) and max(l2p1x, l2p2x) >= x >= min(l2p1x, l2p2x):
            y1 = (l1p1x * l1p2y - l1p1y * l1p2x) * (l2p1y - l2p2y) - (l1p1y - l1p2y) * (l2p1x * l2p2y - l2p1y * l2p2x)
            y2 = (l1p1x - l1p2x) * (l2p1y - l2p2y) - (l1p1y - l1p2y) * (l2p1x - l2p2x)
            if y2 != 0:
                y = y1 / y2
                if max(l1p1y, l1p2y) >= y >= min(l1p1y, l1p2y) and max(l2p1y, l2p2y) >= y >= min(l2p1y, l2p2y):
                    return True
    return False


def line_circle_hit(bx, by, rad, l2p1x, l2p1y, l2p2x, l2p2y):
    m = (l2p2y - l2p1y) / (l2p2x - l2p1x)
    c = l2p1y - l2p1x * m
    p = bx
    q = by
    r = rad

    a = m * m + 1
    b = 2 * (m * c - m * q - p)
    c = q * q - r * r + p * p - 2 * c * q + c * c

    if b * b >= 4 * a * c:
        quad1 = -b
        quad2 = (b * b - 4 * a * c) ** 0.5
        quad3 = 2 * a
        x1 = (quad1 + quad2) / quad3
        x2 = (quad1 - quad2) / quad3
        if max(x1, x2) >= min(l2p1x, l2p2x) and min(x1, x2) <= max(l2p1x, l2p2x):
            return True
    return False
