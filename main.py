import cfg
import pygame
import sys
import os
import math
import pickle
import random
from string import ascii_uppercase

name_chars = ascii_uppercase + ' '

if sys.platform in ["win32", "win64"]:
    os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()

pygame.display.set_caption('Asteroids')
pygame.mouse.set_visible(0)

def reset_high_scores():
    pass
    # hiscores_file = "hiscores.pickle"
    # if os.path.isfile(hiscores_file):
    #     os.remove(hiscores_file)


def load_high_scores():
    try:
        infile = open("hiscores.pickle", "rb")
        cfg.hiscores = pickle.load(infile)
        infile.close()
    except OSError:
        # print('no file')
        random.choice(ascii_uppercase)
        for i in range(11):
            score = random.randrange(50, 3000, 50)
            who = random.choice(ascii_uppercase)
            who += random.choice(ascii_uppercase)
            who += random.choice(ascii_uppercase)
            # score = 0
            # who = '   '
            cfg.hiscores.append([score, who])

        outfile = open("hiscores.pickle", "wb")
        pickle.dump(sorted(cfg.hiscores, reverse=True)[:10], outfile)
        outfile.close()

        infile = open("hiscores.pickle", "rb")
        cfg.hiscores = pickle.load(infile)
        infile.close()

        # print('made new')
    finally:
        # print('done')
        # print(cfg.hiscores)
        pass

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
        self.points_screen = calc_screen_pos(self, self.points)
        # flame
        self.fpoints = []
        self.fpoints.append((0, -13))
        self.fpoints.append((0.8 * math.pi, 8))
        self.fpoints.append(((2 - 0.8) * math.pi, 8))
        self.fpoints_screen = calc_screen_pos(self, self.fpoints)


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

    cfg.PLAYER_SHIP[0].points_screen = calc_screen_pos(cfg.PLAYER_SHIP[0], cfg.PLAYER_SHIP[0].points)
    cfg.PLAYER_SHIP[0].fpoints_screen = calc_screen_pos(cfg.PLAYER_SHIP[0], cfg.PLAYER_SHIP[0].fpoints)


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

                bullet(cfg.surface, who[i])

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
        self.points_screen = calc_screen_pos_alien_ship(self)


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

    cfg.ALIEN_SHIP[0].points_screen = calc_screen_pos_alien_ship(cfg.ALIEN_SHIP[0])

    if cfg.ALIEN_SHIP[0].pos[0] < -40 or cfg.ALIEN_SHIP[0].pos[0] > cfg.SCREEN_WIDTH + 40:
        del cfg.ALIEN_SHIP[0]


def add_alien_bullet():
    if cfg.ALIEN_SHIP:
        if not cfg.ALIEN_BULLETS or len(cfg.ALIEN_BULLETS) < 100:
            cfg.ALIEN_BULLETS.append(AlienBullet())
            cfg.sound_fire.play()
            return True
        return False


def move_alien_bullets():
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

                bullet(cfg.surface, cfg.ALIEN_BULLETS[i])

class Rock(object):
    def __init__(self, size, pos, vel):
        if size is None:
            size = 1
            self.size = size

        self.size = size
        self.score = [50, 100, 200, 500, 1000][self.size - 1]

        self.pos = list(pos)
        self.scale = 1
        angle = random.uniform(0, 2 * math.pi)
        vel_x = vel * math.sin(angle)
        vel_y = vel * math.cos(angle)
        self.rotation_speed = random.uniform(-cfg.ROCK_ROTATION_MAX, cfg.ROCK_ROTATION_MAX)
        self.vel = (vel_x, vel_y)
        self.points = []
        segment_angle = 2 * math.pi / cfg.ROCK_VERTICES

        for point in range(cfg.ROCK_VERTICES):
            point_ang = random.uniform(point, point + 1) * segment_angle
            point_dis = random.uniform(cfg.ROCK_RADIUS_MIN,
                                       cfg.ROCK_RADIUS_MAX) / cfg.ROCK_SPLIT_FACTOR ** (size - 1)
            self.points.append((point_ang, point_dis))
        self.angle = random.uniform(0, 2 * math.pi)
        self.angle = 0
        self.points_screen = calc_screen_pos(self, self.points)
        self.ufo_bullet_hit_when = 0

        """
        find centroid offset
        https://en.wikipedia.org/wiki/Centroid
        https://stackoverflow.com/questions/5271583/center-of-gravity-of-a-polygon
        """
        self.cg = [0, 0]
        area = 0
        for point in range(cfg.ROCK_VERTICES):
            p1x = self.points_screen[point][0] - self.pos[0]
            p1y = self.points_screen[point][1] - self.pos[1]
            p2x = self.points_screen[point - 1][0] - self.pos[0]
            p2y = self.points_screen[point - 1][1] - self.pos[1]

            param1 = p1x + p2x
            param2 = p1y + p2y
            param3 = p1x * p2y - p2x * p1y

            self.cg[0] += param1 * param3
            self.cg[1] += param2 * param3
            area += param3 / 2

        self.cg[0] = self.cg[0] / (6 * area)
        self.cg[1] = self.cg[1] / (6 * area)

        # adjust dis and ang of points to move rock to centre of mass
        for point in range(cfg.ROCK_VERTICES):
            point_ang, point_dis = self.points[point]
            x = point_dis * math.sin(point_ang)
            y = point_dis * math.cos(point_ang)
            new_x = x - self.cg[0]
            new_y = y - self.cg[1]
            new_point_dis = math.hypot(new_x, new_y)
            new_point_ang = math.atan2(new_y, new_x)
            self.points[point] = (new_point_ang, new_point_dis)


def instigate_rocks(i):
    cfg.ROCKS = []
    for i in range(i):
        size = 1
        pos_type = 2
        x = random.uniform(0, cfg.SCREEN_WIDTH)
        y = random.uniform(0, cfg.SCREEN_HEIGHT)
        if pos_type == 2:
            # rocks places around the edge of screen, 1/6 screen
            edge = random.choice(('L', 'R', 'U', 'D'))
            ed = 6
            en = ed - 1
            if edge == 'L':
                x = random.uniform(0, cfg.SCREEN_WIDTH * 1 / ed)
                y = random.uniform(0, cfg.SCREEN_HEIGHT)
            if edge == 'R':
                x = random.uniform(cfg.SCREEN_WIDTH * en / ed, cfg.SCREEN_WIDTH)
                y = random.uniform(0, cfg.SCREEN_HEIGHT)
            if edge == 'U':
                x = random.uniform(0, cfg.SCREEN_WIDTH)
                y = random.uniform(0, cfg.SCREEN_HEIGHT * 1 / ed)
            if edge == 'D':
                x = random.uniform(0, cfg.SCREEN_WIDTH)
                y = random.uniform(cfg.SCREEN_HEIGHT * en / ed, cfg.SCREEN_HEIGHT)
        pos = (x, y)

        vel = random.uniform(cfg.ROCK_VEL_MIN, cfg.ROCK_VEL_MAX) * cfg.ROCK_SPLIT_FACTOR ** (size - 1)
        cfg.ROCKS.append(Rock(size, pos, vel))

    # todo: is this my pythonic?
    # particles = [Particle() for i in range(num_particles)]


def calc_screen_pos(self):
    points_screen = []
    for point in range(len(self.points)):
        point_ang = self.points[point][0] + self.angle
        point_dis = self.points[point][1]
        scale = self.scale
        x = self.pos[0] + math.sin(point_ang) * point_dis * scale
        y = self.pos[1] + math.cos(point_ang) * point_dis * scale
        points_screen.append((x, y))
    return points_screen


def split_rock(r):
    h = cfg.ROCKS[r]  # the rock which was hit
    if h.size < 3:
        new_vel = math.hypot(h.vel[0], h.vel[1]) * cfg.ROCK_SPLIT_FACTOR
        cfg.ROCKS.append(Rock(h.size + 1, h.pos, new_vel))
        cfg.ROCKS.append(Rock(h.size + 1, h.pos, new_vel))
    del cfg.ROCKS[r]
    if not cfg.ROCKS:
        cfg.ROCKS_VISIBLE = False
        cfg.no_rocks_when = pygame.time.get_ticks()


def min_rock_distance():
    min_dis = cfg.SCREEN_WIDTH + cfg.SCREEN_HEIGHT
    for r in range(len(cfg.ROCKS)):
        rock_x, rock_y = cfg.ROCKS[r].pos
        dis = math.hypot(rock_x - cfg.SCREEN_WIDTH / 2, rock_y - cfg.SCREEN_HEIGHT / 2)
        if dis < min_dis:
            min_dis = dis
    return min_dis


def move_rocks():
    for i in range(len(cfg.ROCKS)):
        cfg.ROCKS[i].pos[0] += cfg.ROCKS[i].vel[0] / cfg.ACTUAL_FPS
        cfg.ROCKS[i].pos[1] += cfg.ROCKS[i].vel[1] / cfg.ACTUAL_FPS

        if cfg.ROCKS[i].pos[0] < 0:
            cfg.ROCKS[i].pos[0] += cfg.SCREEN_WIDTH
        if cfg.ROCKS[i].pos[1] < 0:
            cfg.ROCKS[i].pos[1] += cfg.SCREEN_HEIGHT

        if cfg.ROCKS[i].pos[0] > cfg.SCREEN_WIDTH:
            cfg.ROCKS[i].pos[0] -= cfg.SCREEN_WIDTH
        if cfg.ROCKS[i].pos[1] > cfg.SCREEN_HEIGHT:
            cfg.ROCKS[i].pos[1] -= cfg.SCREEN_HEIGHT

        cfg.ROCKS[i].angle += cfg.ROCKS[i].rotation_speed / cfg.ACTUAL_FPS
        cfg.ROCKS[i].points_screen = calc_screen_pos(cfg.ROCKS[i], cfg.ROCKS[i].points)

        rock(cfg.surface, cfg.ROCKS[i])

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

                spark_bit(cfg.surface, cfg.SPARKS[i])
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
        split_rock(r)
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
        split_rock(r)
        del cfg.ALIEN_SHIP[0]
    return 0


def player_ship_rock():
    if cfg.show_ship:
        r = ship_rock(cfg.PLAYER_SHIP)
        if r > -1:
            cfg.PLAYER_STATUS = 'ship died'
            cfg.GAME_STATUS_WHEN = pygame.time.get_ticks()
            score = cfg.ROCKS[r].score
            split_rock(r)
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


def main():
    load_high_scores()
    instigate_rocks(cfg.ROCK_COUNT_START)
    add_parked_ships(9)
    player_ship_fired_when = 0
    no_alien_ship_when = 0
    alien_ship_fire_when = 0

    clock = pygame.time.Clock()
    ufo_sound = False

    while True:
        if not get_input():
            break

        cfg.surface.fill((0, 0, 0))

        if cfg.PLAYER_STATUS == 'start screen':
            start_screen(cfg.surface)
            if cfg.player_ship_firing:
                cfg.player_ship_firing = False
                cfg.PLAYER_STATUS = 'waiting for space'

        if cfg.PLAYER_STATUS == 'waiting for space':
            if min_rock_distance() > cfg.ROCK_SHIP_START_DIS_MIN:
                add_ship()
                cfg.PLAYER_STATUS = 'playing'
                cfg.control_play_ship = True
                cfg.show_ship = True

        if cfg.PLAYER_STATUS == 'ship died':
            if pygame.time.get_ticks() > cfg.GAME_STATUS_WHEN + 5000:
                if len(cfg.PARKED_SHIPS) == 0:
                    cfg.PLAYER_STATUS = 'game over'
                else:
                    cfg.PLAYER_STATUS = 'waiting for space'

        if cfg.PLAYER_STATUS == 'game over':
            game_over(cfg.surface)
            cfg.control_play_ship = False
            if cfg.player_ship_firing:
                cfg.player_ship_firing = False
            if cfg.SCORE > cfg.hiscores[9][0]:
                cfg.PLAYER_STATUS = 'new high score'
                cfg.GAME_STATUS_WHEN = pygame.time.get_ticks()
                cfg.hiscores.append([cfg.SCORE, '   '])
                tmp_scores = sorted(cfg.hiscores, reverse=True)[:10]
                cfg.hiscores = tmp_scores
                letter_change_when = 0
                flash_when = 0
                for i in range(10):
                    if cfg.hiscores[i][1] == '   ':
                        my_pos = i
                my_char_id = 0
                my_char_setting = 0
                me = list('   ')
                me_setting = list(name_chars[my_char_id] + '  ')
                me_show = True

        if cfg.PLAYER_STATUS == 'new high score':
            game_over(cfg.surface)

            if pygame.time.get_ticks() > flash_when + 150:
                # make it flash..
                flash_when = pygame.time.get_ticks()
                if me_show:
                    cfg.hiscores[my_pos][1] = ''.join(me_setting)
                else:
                    cfg.hiscores[my_pos][1] = ''.join(me)
                if pygame.time.get_ticks() < letter_change_when + 250:
                    # ..unless the user is setting right now
                    me_show = True
                else:
                    me_show = not me_show

            if pygame.time.get_ticks() > letter_change_when + 200:
                # change letter once per 200ms
                if cfg.player_ship_rotation_thruster != 0:
                    letter_change_when = pygame.time.get_ticks()
                    my_char_id -= cfg.player_ship_rotation_thruster
                    if my_char_id < 0:
                        my_char_id = len(name_chars) - 1
                    if my_char_id > len(name_chars) - 1:
                        my_char_id = 0
                    me_setting = list(name_chars[my_char_id] + '  ')
                    if name_chars[my_char_id] == ' ':
                        me = '-  '
                    else:
                        me = '   '
                    cfg.hiscores[my_pos][1] = ''.join(me_setting)

                if cfg.player_ship_firing:
                    letter_change_when = pygame.time.get_ticks()
                    me = me_setting
                    my_char_setting += 1


        if cfg.PLAYER_STATUS == 'playing':
            ship(cfg.surface, cfg.PLAYER_SHIP[0].points_screen)
            if cfg.playing_thrust_sound:
                ship(cfg.surface, cfg.PLAYER_SHIP[0].fpoints_screen)
            if cfg.player_ship_thrust:
                if not cfg.playing_thrust_sound:
                    cfg.sound_thruster.play(-1, fade_ms=100)
                    cfg.playing_thrust_sound = True
            else:
                if cfg.playing_thrust_sound:
                    cfg.sound_thruster.fadeout(200)
                    cfg.playing_thrust_sound = False
            if cfg.player_ship_firing:
                if not player_ship_fired_when:
                    # just pressed fire
                    player_ship_fired_when = pygame.time.get_ticks()
                    add_bullet()
                else:
                    # still pushing fire button
                    if pygame.time.get_ticks() > player_ship_fired_when + cfg.AUTO_REFIRE_DELAY:
                        player_ship_fired_when = pygame.time.get_ticks()
                        add_bullet()
            else:
                if player_ship_fired_when:
                    # just released fire key
                    player_ship_fired_when = 0
            move_ship()

        # always fo these
        move_bullets(cfg.PLAYER_BULLETS)
        move_bullets(cfg.ALIEN_BULLETS)
        move_rocks()

        new_score(cfg.SCORE, bullet_rock(cfg.PLAYER_BULLETS))
        new_score(cfg.SCORE, player_bullet_ship())
        new_score(cfg.SCORE, player_ship_rock())

        if new_score(cfg.SCORE, ship_ship()):
            cfg.PLAYER_STATUS == 'ship died'

        alien_ship_rock()
        if alien_bullet_ship():
            cfg.PLAYER_STATUS == 'ship died'

        bullet_rock(cfg.ALIEN_BULLETS)
        move_sparks()
        score(cfg.surface)
        parked_ships(cfg.surface)

        # alien ship
        if len(cfg.ALIEN_SHIP) > 0:
            if not ufo_sound:
                cfg.sound_big_ufo.play(-1, fade_ms=1000)
                ufo_sound = True
            ship(cfg.surface, cfg.ALIEN_SHIP[0].points_screen)
            move_alien_ship()
            if pygame.time.get_ticks() > alien_ship_fire_when:
                if add_alien_bullet():
                    alien_ship_fire_when = pygame.time.get_ticks() + 5000
        else:
            if ufo_sound:
                cfg.sound_big_ufo.fadeout(100)
                ufo_sound = False
            if no_alien_ship_when == 0:
                no_alien_ship_when = pygame.time.get_ticks()
            if pygame.time.get_ticks() > no_alien_ship_when + 15000:
                add_alien_ship()
                no_alien_ship_when = 0
                alien_ship_fire_when = pygame.time.get_ticks() + 2000

        # rocks
        if cfg.no_rocks_when:
            if pygame.time.get_ticks() > cfg.no_rocks_when + 4000:
                cfg.no_rocks_when = 0
                if cfg.ROCK_COUNT_START < 6:
                    cfg.ROCK_COUNT_START += 1
                instigate_rocks(cfg.ROCK_COUNT_START)
                cfg.ROCKS_VISIBLE = True
                waiting_for_spacer = pygame.time.get_ticks()

        cfg.ACTUAL_FPS = max(clock.get_fps(), 1)
        debug(cfg.surface, 0, 90, "A FPS: " + str(int(cfg.ACTUAL_FPS)))
        # draw_screen.debug(surface, 0, 90, "a: " + str(no_alien_ship_when))

        pygame.display.update()
        clock.tick(cfg.TARGET_FPS)
    pygame.quit()


def new_score(score_before, score_delta):
    cfg.SCORE += score_delta
    if int(cfg.SCORE / cfg.EXTRA_SHIP_SCORE) > int(score_before / cfg.EXTRA_SHIP_SCORE):
        add_parked_ships(1)
        cfg.sound_extra_ship.play(4)


if __name__ == "__main__":
    main()
