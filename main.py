import cfg
import hit
import get_input
import player
import alien
import rock
import screen
import pygame
import sys
import os
import math
import hiscore
from string import ascii_uppercase

name_chars = ascii_uppercase + ' '

if sys.platform in ["win32", "win64"]:
    os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()

pygame.display.set_caption('Asteroids')
pygame.mouse.set_visible(0)


def main():
    hiscore.load_in()
    rock.instigate_rocks(cfg.ROCK_COUNT_START)
    player.add_parked_ships(9)
    player_ship_fired_when = 0
    no_alien_ship_when = 0
    alien_ship_fire_when = 0

    clock = pygame.time.Clock()
    ufo_sound = False

    while True:
        if not get_input.get_input():
            break

        cfg.surface.fill((0, 0, 0))

        if cfg.PLAYER_STATUS == 'start screen':
            screen.start_screen(cfg.surface)
            if cfg.player_ship_firing:
                cfg.player_ship_firing = False
                cfg.PLAYER_STATUS = 'waiting for space'

        if cfg.PLAYER_STATUS == 'waiting for space':
            if rock.min_rock_distance() > cfg.ROCK_SHIP_START_DIS_MIN:
                player.add_ship()
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
                    player.add_bullet()
                else:
                    # still pushing fire button
                    if pygame.time.get_ticks() > player_ship_fired_when + cfg.AUTO_REFIRE_DELAY:
                        player_ship_fired_when = pygame.time.get_ticks()
                        player.add_bullet()
            else:
                if player_ship_fired_when:
                    # just released fire key
                    player_ship_fired_when = 0
            player.move_ship()

        # always fo these
        player.move_bullets(cfg.PLAYER_BULLETS)
        player.move_bullets(cfg.ALIEN_BULLETS)
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
            alien.move_alien_ship()
            if pygame.time.get_ticks() > alien_ship_fire_when:
                if alien.add_bullet():
                    alien_ship_fire_when = pygame.time.get_ticks() + 5000
        else:
            if ufo_sound:
                cfg.sound_big_ufo.fadeout(100)
                ufo_sound = False
            if no_alien_ship_when == 0:
                no_alien_ship_when = pygame.time.get_ticks()
            if pygame.time.get_ticks() > no_alien_ship_when + 15000:
                alien.add_alien_ship()
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
        player.add_parked_ships(1)
        cfg.sound_extra_ship.play(4)


if __name__ == "__main__":
    main()
