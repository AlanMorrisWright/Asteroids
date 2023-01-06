import cfg
import hit
import rock
import screen
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

                screen.bullet(cfg.surface, cfg.ALIEN_BULLETS[i])

def main():
    load_high_scores()
    rock.instigate_rocks(cfg.ROCK_COUNT_START)
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
            screen.start_screen(cfg.surface)
            if cfg.player_ship_firing:
                cfg.player_ship_firing = False
                cfg.PLAYER_STATUS = 'waiting for space'

        if cfg.PLAYER_STATUS == 'waiting for space':
            if rock.min_rock_distance() > cfg.ROCK_SHIP_START_DIS_MIN:
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
            screen.game_over(cfg.surface)
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
            screen.game_over(cfg.surface)

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
            screen.ship(cfg.surface, cfg.PLAYER_SHIP[0].points_screen)
            if cfg.playing_thrust_sound:
                screen.ship(cfg.surface, cfg.PLAYER_SHIP[0].fpoints_screen)
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
        rock.move_rocks()

        new_score(cfg.SCORE, hit.bullet_rock(cfg.PLAYER_BULLETS))
        new_score(cfg.SCORE, hit.player_bullet_ship())
        new_score(cfg.SCORE, hit.player_ship_rock())

        if new_score(cfg.SCORE, hit.ship_ship()):
            cfg.PLAYER_STATUS == 'ship died'

        hit.alien_ship_rock()
        if hit.alien_bullet_ship():
            cfg.PLAYER_STATUS == 'ship died'

        hit.bullet_rock(cfg.ALIEN_BULLETS)
        hit.move_sparks()
        screen.score(cfg.surface)
        screen.parked_ships(cfg.surface)

        # alien ship
        if len(cfg.ALIEN_SHIP) > 0:
            if not ufo_sound:
                cfg.sound_big_ufo.play(-1, fade_ms=1000)
                ufo_sound = True
            screen.ship(cfg.surface, cfg.ALIEN_SHIP[0].points_screen)
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
                rock.instigate_rocks(cfg.ROCK_COUNT_START)
                cfg.ROCKS_VISIBLE = True
                waiting_for_spacer = pygame.time.get_ticks()

        cfg.ACTUAL_FPS = max(clock.get_fps(), 1)
        screen.debug(cfg.surface, 0, 90, "A FPS: " + str(int(cfg.ACTUAL_FPS)))
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
