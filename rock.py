import cfg
import random
import math
import pygame
import screen


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
        self.points_screen = screen.calc_screen_pos(self, self.points)
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
        cfg.ROCKS[i].points_screen = screen.calc_screen_pos(cfg.ROCKS[i], cfg.ROCKS[i].points)

        screen.rock(cfg.surface, cfg.ROCKS[i])
