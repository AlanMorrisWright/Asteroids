import cfg
import math
import random
import pygame
import screen


class AlienShip(object):
    def __init__(self):

        self.type = random.choices(population=[1, 2], weights=[70, 30])[0]

        self.scale = [1, 0.7][self.type - 1]
        self.score = [1000, 2000][self.type - 1]
        # target_type = ['moving_player', 'player_position', 'rock', 'random']
        self.targeting = [[0.1, 0.2, 0.5, 0.2], [0.3, 0.3, 0.4, 0.0]][self.type - 1]
        self.targeting = [[0.0, 0.1, 0.9, 0.0], [0.0, 0.1, 0.9, 0.0]][self.type - 1]

        # which side of screen to start?
        if random.randint(1, 2) == 1:
            x = -40
            xv = cfg.ALIEN_SHIP_SPEED
        else:
            x = cfg.SCREEN_WIDTH + 40
            xv = -cfg.ALIEN_SHIP_SPEED
        y = cfg.SCREEN_HEIGHT / 4

        self.pos = list((x, y))

        # x, y
        self.points = [(23, 0), (10, 7), (-10, 7), (-23, 0),
                       (-9, -8), (-4, -16), (4, -16), (9, -8),
                       (23, 0), (-23, 0), (-9, -8), (9, -8)]

        self.born = pygame.time.get_ticks()
        self.next_steer = self.born + 1000
        self.vel = [xv, 0]
        self.points_screen = screen.calc_screen_pos_alien_ship(self)


class AlienBullet(object):
    def __init__(self):
        x, y = cfg.ALIEN_SHIP[0].pos
        targeting = cfg.ALIEN_SHIP[0].targeting
        self.pos = list((x, y))
        self.born = pygame.time.get_ticks()
        self.die = self.born + cfg.BULLET_LIFE_TIME

        alien_ship_vel_x, alien_ship_vel_y = cfg.ALIEN_SHIP[0].vel

        # work out the angle of the bullet

        target_type = random.choices(population=['moving_player',
                                                 'player_position',
                                                 'rock',
                                                 'random'],
                                     weights=targeting)[0]

        # default random shot
        angle = random.uniform(0, 2 * math.pi)

        if target_type == 'rock':
            if not cfg.ROCKS_VISIBLE:
                pass
            else:
                target_dis = 999999
                targeted_rock = -1
                for r in range(len(cfg.ROCKS)):
                    if pygame.time.get_ticks() > cfg.ROCKS[r].ufo_bullet_hit_when:
                        # xo, xy to check if 'off-screen' rock is closer
                        for xo in (-cfg.SCREEN_WIDTH, 0, cfg.SCREEN_WIDTH):
                            for yo in (-cfg.SCREEN_HEIGHT, 0, cfg.SCREEN_HEIGHT):
                                rx = cfg.ROCKS[r].pos[0] + xo
                                ry = cfg.ROCKS[r].pos[1] + yo
                                rvx = cfg.ROCKS[r].vel[0] - alien_ship_vel_x
                                rvy = cfg.ROCKS[r].vel[1] - alien_ship_vel_y

                                qa = rvx ** 2 + rvy ** 2 - cfg.BULLET_VEL ** 2
                                qb = 2 * rx * rvx - 2 * x * rvx + 2 * ry * rvy - 2 * y * rvy
                                qc = rx**2 + x**2 - 2 * x * rx + ry**2 + y**2 - 2 * y * ry
                                q1 = -qb
                                q2 = (qb**2 - 4 * qa * qc)**0.5
                                q3 = 2 * qa
                                t1 = (q1 + q2) / q3
                                t2 = (q1 - q2) / q3
                                max_t = max(t1, t2)
                                tmp_x = rx + rvx * max_t
                                tmp_y = ry + rvy * max_t
                                dis = math.hypot(tmp_x - x, tmp_y - y)
                                if dis < target_dis:
                                    target_dis = dis
                                    angle = math.atan2(tmp_x - x, tmp_y - y)
                                    targeted_rock = r
                if targeted_rock > -1:
                    cfg.ROCKS[targeted_rock].ufo_bullet_hit_when = pygame.time.get_ticks() + 2000

        # target moving_player
        elif target_type == 'moving_player':
            if not cfg.PLAYER_SHIP:
                pass
            else:
                target_dis = 999999
                # xo, xy to check if 'off-screen' rock is closer
                for xo in (-cfg.SCREEN_WIDTH, 0, cfg.SCREEN_WIDTH):
                    for yo in (-cfg.SCREEN_HEIGHT, 0, cfg.SCREEN_HEIGHT):
                        rx = cfg.PLAYER_SHIP[0].pos[0] + xo
                        ry = cfg.PLAYER_SHIP[0].pos[1] + yo
                        rvx = cfg.PLAYER_SHIP[0].vel[0] - alien_ship_vel_x
                        rvy = cfg.PLAYER_SHIP[0].vel[1] - alien_ship_vel_y

                        qa = rvx ** 2 + rvy ** 2 - cfg.BULLET_VEL ** 2
                        qb = 2 * rx * rvx - 2 * x * rvx + 2 * ry * rvy - 2 * y * rvy
                        qc = rx**2 + x**2 - 2 * x * rx + ry**2 + y**2 - 2 * y * ry
                        q1 = -qb
                        q2 = (qb**2 - 4 * qa * qc)**0.5
                        q3 = 2 * qa
                        t1 = (q1 + q2) / q3
                        t2 = (q1 - q2) / q3
                        max_t = max(t1, t2)
                        tmp_x = rx + rvx * max_t
                        tmp_y = ry + rvy * max_t
                        dis = math.hypot(tmp_x - x, tmp_y - y)
                        if dis < target_dis:
                            target_dis = dis
                            angle = math.atan2(tmp_x - x, tmp_y - y)

        # target player_position
        elif target_type == 'player_position':
            if not cfg.PLAYER_SHIP:
                pass
            else:
                rx = cfg.PLAYER_SHIP[0].pos[0]
                ry = cfg.PLAYER_SHIP[0].pos[1]
                rvx = -alien_ship_vel_x
                rvy = -alien_ship_vel_y

                qa = rvx ** 2 + rvy ** 2 - cfg.BULLET_VEL ** 2
                qb = 2 * rx * rvx - 2 * x * rvx + 2 * ry * rvy - 2 * y * rvy
                qc = rx**2 + x**2 - 2 * x * rx + ry**2 + y**2 - 2 * y * ry
                q1 = -qb
                q2 = (qb**2 - 4 * qa * qc)**0.5
                q3 = 2 * qa
                t1 = (q1 + q2) / q3
                t2 = (q1 - q2) / q3
                max_t = max(t1, t2)
                tmp_x = rx + rvx * max_t
                tmp_y = ry + rvy * max_t
                angle = math.atan2(tmp_x - x, tmp_y - y)

        self.vel = (alien_ship_vel_x + math.sin(angle) * cfg.BULLET_VEL,
                    alien_ship_vel_y + math.cos(angle) * cfg.BULLET_VEL)


def add_alien_ship():
    cfg.ALIEN_SHIP.append(AlienShip())


def move_alien_ship():
    # acceleration, velocity and position
    xp = cfg.ALIEN_SHIP[0].pos[0]
    xv = cfg.ALIEN_SHIP[0].vel[0]
    yp = cfg.ALIEN_SHIP[0].pos[1]
    yv = cfg.ALIEN_SHIP[0].vel[1]

    if pygame.time.get_ticks() > cfg.ALIEN_SHIP[0].next_steer:
        if cfg.ALIEN_SHIP[0].vel[0] > 0:
            angle = random.uniform(1 * math.pi / 4, 3 * math.pi / 4)  # move right
        else:
            angle = random.uniform(5 * math.pi / 4, 7 * math.pi / 4)  # move left

        cfg.ALIEN_SHIP[0].vel[0] = cfg.ALIEN_SHIP_SPEED * math.sin(angle)
        cfg.ALIEN_SHIP[0].vel[1] = cfg.ALIEN_SHIP_SPEED * math.cos(angle)
        cfg.ALIEN_SHIP[0].next_steer = pygame.time.get_ticks() + 2000

    cfg.ALIEN_SHIP[0].pos[0] += cfg.ALIEN_SHIP[0].vel[0] / cfg.ACTUAL_FPS
    cfg.ALIEN_SHIP[0].pos[1] += cfg.ALIEN_SHIP[0].vel[1] / cfg.ACTUAL_FPS

    # screen height wrap
    if cfg.ALIEN_SHIP[0].pos[1] < 0:
        cfg.ALIEN_SHIP[0].pos[1] += cfg.SCREEN_HEIGHT
    if cfg.ALIEN_SHIP[0].pos[1] > cfg.SCREEN_HEIGHT:
        cfg.ALIEN_SHIP[0].pos[1] -= cfg.SCREEN_HEIGHT

    cfg.ALIEN_SHIP[0].points_screen = screen.calc_screen_pos_alien_ship(cfg.ALIEN_SHIP[0])

    if cfg.ALIEN_SHIP[0].pos[0] < -40 or cfg.ALIEN_SHIP[0].pos[0] > cfg.SCREEN_WIDTH + 40:
        del cfg.ALIEN_SHIP[0]


def add_bullet():
    if cfg.ALIEN_SHIP:
        if not cfg.ALIEN_BULLETS or len(cfg.ALIEN_BULLETS) < 100:
            cfg.ALIEN_BULLETS.append(AlienBullet())
            cfg.sound_fire.play()
            return True
        return False


def move_bullets():
    if len(cfg.ALIEN_BULLETS):
        for i in range(len(cfg.ALIEN_BULLETS) - 1, -1, -1):
            if pygame.time.get_ticks() >= cfg.ALIEN_BULLETS[i].die:
                del cfg.ALIEN_BULLETS[i]
            else:
                cfg.ALIEN_BULLETS[i].pos[0] += cfg.ALIEN_BULLETS[i].vel[0] / cfg.ACTUAL_FPS
                cfg.ALIEN_BULLETS[i].pos[1] += cfg.ALIEN_BULLETS[i].vel[1] / cfg.ACTUAL_FPS

                if cfg.ALIEN_BULLETS[i].pos[0] < 0:
                    cfg.ALIEN_BULLETS[i].pos[0] += cfg.SCREEN_WIDTH
                if cfg.ALIEN_BULLETS[i].pos[1] < 0:
                    cfg.ALIEN_BULLETS[i].pos[1] += cfg.SCREEN_HEIGHT

                if cfg.ALIEN_BULLETS[i].pos[0] > cfg.SCREEN_WIDTH:
                    cfg.ALIEN_BULLETS[i].pos[0] -= cfg.SCREEN_WIDTH
                if cfg.ALIEN_BULLETS[i].pos[1] > cfg.SCREEN_HEIGHT:
                    cfg.ALIEN_BULLETS[i].pos[1] -= cfg.SCREEN_HEIGHT

                screen.bullet(cfg.surface, cfg.ALIEN_BULLETS[i])
