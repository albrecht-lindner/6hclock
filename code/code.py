import board
import digitalio
import time
import adafruit_ds3231

# seconds between two clock moves
CLOCK_MOVE_INTERVAL = 5*60

# set up timer
i2c = board.I2C()
ds3231 = adafruit_ds3231.DS3231(i2c)

# set up led pins
LED_EXT_PIN = digitalio.DigitalInOut(board.D2)
LED_EXT_PIN.direction = digitalio.Direction.OUTPUT
LED_BOARD_PIN = digitalio.DigitalInOut(board.LED)
LED_BOARD_PIN.direction = digitalio.Direction.OUTPUT

# set up stepper driver pins
MOT_nEN_PIN = digitalio.DigitalInOut(board.A0);
MOT_nEN_PIN.direction = digitalio.Direction.OUTPUT
MOT_M1_PIN = digitalio.DigitalInOut(board.D12);
MOT_M1_PIN.direction = digitalio.Direction.OUTPUT
MOT_M2_PIN = digitalio.DigitalInOut(board.D11);
MOT_M2_PIN.direction = digitalio.Direction.OUTPUT
MOT_nSTBY_PIN = digitalio.DigitalInOut(board.D10);
MOT_nSTBY_PIN.direction = digitalio.Direction.OUTPUT
MOT_M3_STEP_PIN = digitalio.DigitalInOut(board.D9);
MOT_M3_STEP_PIN.direction = digitalio.Direction.OUTPUT
MOT_M4_DIR_PIN = digitalio.DigitalInOut(board.D7);
MOT_M4_DIR_PIN.direction = digitalio.Direction.OUTPUT

# set microstepping to 256 microsteps
# this is done with pins M1, M2, M3, M4 that are latched when standby mode is left
def mot_set_256_microsteps():
    MOT_nSTBY_PIN.value = False
    time.sleep(0.01)

    MOT_M1_PIN.value = True
    MOT_M2_PIN.value = True
    MOT_M3_STEP_PIN.value = False
    MOT_M4_DIR_PIN.value = False
    time.sleep(0.01)

    # leave stby mode, i.e. latch microstepping mode
    MOT_nSTBY_PIN.value = True
    # enable motor
    MOT_nEN_PIN.value = False

# do n steps of the stepper motor
def mot_n_steps(n):
    mot_set_256_microsteps()

    toggle = 0
    nn = 2*256*n  # the additional factor 2 is because toggle needs to go first up and then down for one microstep
    while (nn >= 0):
        # if nn % 10 == 0:
            # print("step " + str(nn))
        if toggle == 0:
            MOT_M4_DIR_PIN.value = True
            MOT_M3_STEP_PIN.value = False
        else:
            MOT_M4_DIR_PIN.value = True
            MOT_M3_STEP_PIN.value = True
        toggle = 1 - toggle
        nn = nn - 1
        # time.sleep(0.001)
    # disable motor
    MOT_nEN_PIN.value = True

# return the current unix time (seconds)
def get_unix_time():
    now = ds3231.datetime
    unixtime = time.mktime(now)
    return unixtime

last_clock_move = get_unix_time() - CLOCK_MOVE_INTERVAL

print("start")

while True:
    now = get_unix_time()
    if (now - last_clock_move >= CLOCK_MOVE_INTERVAL):
        print(now)
        last_clock_move = now
        LED_BOARD_PIN.value = True
        mot_n_steps(200)
        LED_BOARD_PIN.value = False

    time.sleep(0.5)
