TARGET_FPS = 100
ACTUAL_FPS = TARGET_FPS
# game & screen
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 720
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600
SCREEN_SIZE = [SCREEN_WIDTH, SCREEN_HEIGHT]
# SCREEN_COLOR = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
c = 255
SCREEN_COLOR = [c, c, c]
FONT = "Courier New"

# game
SCORE = 0
hiscores = []
PLAYER_STATUS = 'start screen'
GAME_STATUS_WHEN = 0
ROCKS_VISIBLE = True
PLAYER_SHIP_VISIBLE = False
SCORE_VISIBLE = False
EXTRA_SHIP_SCORE = 10000
game_over = False

# player ship
START_SHIP_COUNT = 3
PLAYER_SHIP = []
SPARKS = []
SPARKLES_BRIGHTNESS = 0
PLAYER_SHIP_ROTATION_ACCEL = 20.0
PLAYER_SHIP_ROTATION_SPEED = 2.0  # of 2 pi per sec?
PLAYER_SHIP_SPEED = 200
left_key = False
right_key = False
player_ship_thrust = 0
player_ship_rotation_thruster = 0
player_ship_firing = False
control_play_ship = False
show_ship = False
added_thrust_bit_when = 0
playing_thrust_sound = False
PARKED_SHIPS = []

# rocks
ROCKS = []
ROCK_COUNT_START = 2
ROCK_VERTICES = 8  # number of vertices
ROCK_RADIUS_MAX = 50  # max diameter
ROCK_RADIUS_MIN = ROCK_RADIUS_MAX * 0.65
ROCK_VEL_MAX = 80
ROCK_VEL_MIN = ROCK_VEL_MAX * 0.5
ROCK_ROTATION_MAX = 3
ROCK_SPLIT_FACTOR = 1.8
ROCK_SHIP_START_DIS_MIN = 150
no_rocks_when = 0

# bullet
PLAYER_BULLETS = []
ALIEN_BULLETS = []
BULLET_RADIUS = 2
BULLET_VEL = 600
BULLET_RELOAD_TIME = 1
BULLET_LIFE_TIME = SCREEN_WIDTH * 1.5
FIRED_BULLETS_MAX = 4
AUTO_REFIRE_DELAY = 700
player_ship_fired_when = 0

# alien ship
ALIEN_SHIP = []
ALIEN_SHIP_SPEED = 150  # of 2 pi per sec?
# xxx = 50000  not needed?

SCORE_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ '
