import cfg
import math
import pygame
import screen


class PlayerShip(object):
    def __init__(self, pos=None, scale=None):
        if pos is not None:
            self.pos = pos
        else:
            self.pos = list((cfg.SCREEN_WIDTH / 2, cfg.SCREEN_HEIGHT / 2))

        if scale is not None:
            self.scale = scale
        else:
            self.scale = 1
        self.score = [1]  # bullet / ship collision detection expects this
        self.points = []
        self.points.append((0, 20))  # nose
        self.points.append((0.7 * math.pi, 10))  # right fin
        self.points.append(((2 - 0.7) * math.pi, 10))  # left fin
        self.vel = [0, 0]
        self.angle = math.pi
        self.rotation_vel = 0
        self.points_screen = screen.calc_screen_pos(self, self.points)
        # flame
        self.fpoints = []
        self.fpoints.append((0, -13))
        self.fpoints.append((0.8 * math.pi, 8))
        self.fpoints.append(((2 - 0.8) * math.pi, 8))
        self.fpoints_screen = screen.calc_screen_pos(self, self.fpoints)


class PlayerBullet(object):
    def __init__(self):
        self.pos = (cfg.PLAYER_SHIP[0].points_screen[0][0],
                    cfg.PLAYER_SHIP[0].points_screen[0][1])
        self.pos = list(self.pos)
        self.vel = (cfg.PLAYER_SHIP[0].vel[0] + math.sin(cfg.PLAYER_SHIP[0].angle) * cfg.BULLET_VEL,
                    cfg.PLAYER_SHIP[0].vel[1] + math.cos(cfg.PLAYER_SHIP[0].angle) * cfg.BULLET_VEL)
        self.born = pygame.time.get_ticks()
        self.die = self.born + cfg.BULLET_LIFE_TIME


def add_parked_ships(s):
    parked_ships = len(cfg.PARKED_SHIPS)
    for ps in range(s):
        x = cfg.SCREEN_WIDTH - (parked_ships + ps + 1) * 15 - 10
        y = 15
        pos = (x, y)
        scale = 0.5
        cfg.PARKED_SHIPS.append(PlayerShip(pos, scale))


def add_ship():
    if len(cfg.PARKED_SHIPS):
        del cfg.PARKED_SHIPS[-1]
        cfg.PLAYER_SHIP.append(PlayerShip())
        return True
    else:
        return False


def move_ship():
    # acceleration, velocity and position
    if cfg.player_ship_thrust:
        cfg.PLAYER_SHIP[0].vel[0] += \
            cfg.PLAYER_SHIP_SPEED * math.sin(cfg.PLAYER_SHIP[0].angle) / cfg.ACTUAL_FPS
        cfg.PLAYER_SHIP[0].vel[1] += \
            cfg.PLAYER_SHIP_SPEED * math.cos(cfg.PLAYER_SHIP[0].angle) / cfg.ACTUAL_FPS
    cfg.PLAYER_SHIP[0].pos[0] += cfg.PLAYER_SHIP[0].vel[0] / cfg.ACTUAL_FPS
    cfg.PLAYER_SHIP[0].pos[1] += cfg.PLAYER_SHIP[0].vel[1] / cfg.ACTUAL_FPS

    # screen wrap
    if cfg.PLAYER_SHIP[0].pos[0] < 0:
        cfg.PLAYER_SHIP[0].pos[0] += cfg.SCREEN_WIDTH
    if cfg.PLAYER_SHIP[0].pos[1] < 0:
        cfg.PLAYER_SHIP[0].pos[1] += cfg.SCREEN_HEIGHT
    if cfg.PLAYER_SHIP[0].pos[0] > cfg.SCREEN_WIDTH:
        cfg.PLAYER_SHIP[0].pos[0] -= cfg.SCREEN_WIDTH
    if cfg.PLAYER_SHIP[0].pos[1] > cfg.SCREEN_HEIGHT:
        cfg.PLAYER_SHIP[0].pos[1] -= cfg.SCREEN_HEIGHT

    # rotation
    if cfg.player_ship_rotation_thruster:
        cfg.PLAYER_SHIP[0].rotation_vel += cfg.player_ship_rotation_thruster \
                                           * cfg.PLAYER_SHIP_ROTATION_ACCEL / cfg.ACTUAL_FPS
        if abs(cfg.PLAYER_SHIP[0].rotation_vel) > cfg.PLAYER_SHIP_ROTATION_SPEED:
            cfg.PLAYER_SHIP[0].rotation_vel = math.copysign(cfg.PLAYER_SHIP_ROTATION_SPEED,
                                                            cfg.PLAYER_SHIP[0].rotation_vel)
    else:
        cfg.PLAYER_SHIP[0].rotation_vel = 0

    cfg.PLAYER_SHIP[0].angle += \
        cfg.PLAYER_SHIP[0].rotation_vel * cfg.PLAYER_SHIP_ROTATION_SPEED / cfg.ACTUAL_FPS

    cfg.PLAYER_SHIP[0].points_screen = screen.calc_screen_pos(cfg.PLAYER_SHIP[0], cfg.PLAYER_SHIP[0].points)
    cfg.PLAYER_SHIP[0].fpoints_screen = screen.calc_screen_pos(cfg.PLAYER_SHIP[0], cfg.PLAYER_SHIP[0].fpoints)


def add_bullet():
    if not cfg.PLAYER_BULLETS or len(cfg.PLAYER_BULLETS) < cfg.FIRED_BULLETS_MAX:
        cfg.PLAYER_BULLETS.append(PlayerBullet())
        cfg.sound_fire.play()
        return True
    return False


def move_bullets(who):
    if len(who):
        for i in range(len(who) - 1, -1, -1):
            if pygame.time.get_ticks() >= who[i].die:
                del who[i]
            else:
                who[i].pos[0] += who[i].vel[0] / cfg.ACTUAL_FPS
                who[i].pos[1] += who[i].vel[1] / cfg.ACTUAL_FPS

                if who[i].pos[0] < 0:
                    who[i].pos[0] += cfg.SCREEN_WIDTH
                if who[i].pos[1] < 0:
                    who[i].pos[1] += cfg.SCREEN_HEIGHT

                if who[i].pos[0] > cfg.SCREEN_WIDTH:
                    who[i].pos[0] -= cfg.SCREEN_WIDTH
                if who[i].pos[1] > cfg.SCREEN_HEIGHT:
                    who[i].pos[1] -= cfg.SCREEN_HEIGHT

                screen.bullet(cfg.surface, who[i])
