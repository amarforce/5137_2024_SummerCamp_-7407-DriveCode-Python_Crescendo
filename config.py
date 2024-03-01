# from dataclasses import dataclass
from enum import Enum

from wpilib import AnalogEncoder, DigitalInput
from wpimath.geometry import Pose3d, Rotation3d

from toolkit.motors import SparkMaxConfig
from rev import CANSparkMax
import rev, math
from enum import Enum
import constants

from wpilib import AnalogEncoder, DigitalInput
from wpimath.geometry import Pose3d, Rotation3d

from toolkit.motors import SparkMaxConfig
from toolkit.motors.ctre_motors import TalonConfig
from units.SI import degrees_to_radians, meters, radians, meters_per_second
from typing import Literal

comp_bot: DigitalInput = DigitalInput(
    2
)  # if true, we are using the practice bot (we will put a jumper on the DIO port)

# from units.SI import (
#     inches_to_meters,
#     meters,
#     meters_per_second,
#     meters_per_second_squared,
#     radians,
# )

DEBUG_MODE: bool = True
# MAKE SURE TO MAKE THIS FALSE FOR COMPETITION
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
LOGGING: bool = True
LOG_OUT_LEVEL: int = 0
LOG_FILE_LEVEL: int = 1

# Levels are how much information is logged
# higher level = less information
# level 0 will log everything
# level 1 will log everything except debug
# and so on
# levels:
# 0 = All
# 1 = INFO
# 2 = WARNING
# 3 = ERROR
# 4 = SETUP
# anything else will log nothing
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

period: float = 0.04  # seconds

# Giraffe
elevator_wrist_limit: float = 0.75  # TODO: PLACEHOLDER
elevator_wrist_threshold: float = 0.75  # TODO: PLACEHOLDER

# odometry config

odometry_debounce: float = 0.1  # TODO: PLACEHOLDER
stage_distance_threshold: float = constants.FieldPos.Stage.stage_length * math.sin(math.radians(30))


#STATE VARIABLES -- PLEASE DO NOT CHANGE




# Leds
def KRainbow():
    return {"type": 2}


class Type:
    def KStatic(r, g, b):
        return {"type": 1, "color": {"r": r, "g": g, "b": b}}

    def KTrack(r1, g1, b1, r2, g2, b2):
        return {
            "type": 3,
            "color": {"r1": r1, "g1": g1, "b1": b1, "r2": r2, "g2": g2, "b2": b2},
        }

    def KBlink(r, g, b):
        return {"type": 4, "color": {"r": r, "g": g, "b": b}}

    def KLadder(typeA, typeB, percent, speed):
        return {
            "type": 5,
            "percent": percent,  # 0-1
            "typeA": typeA,
            "typeB": typeB,
            "speed": speed,
        }


# TEAM
class Team(Enum):
    RED = 0
    BLUE = 1


active_team: Team = Team.RED


# LIMELIGHT
class LimelightPipeline:
    feducial = 0.0
    neural = 1.0
    retroreflective = 2.0


limelight_led_mode = {
    "pipline_default": 0,
    "force_off": 1,
    "force_blink": 2,
    "force_on": 3,
}

# CLIMBING
ready_to_climb: bool = False
climbing: bool = False
climbed: bool = False

# AMP
amping: bool = False

class LimelightPosition:
    init_elevator_front = Pose3d(constants.limelight_right_LL3, constants.limelight_forward_LL3,
                                 constants.limelight_height_LL3, Rotation3d(0, constants.limelight_elevator_angle, 0))
    init_elevator_back = Pose3d(constants.limelight_right, constants.limelight_forward, constants.limelight_height,
                                Rotation3d(0, constants.limelight_elevator_angle, constants.limelight_back_yaw))
    fixed_intake = Pose3d(0, 0, 0, Rotation3d(0, 0, 0))

# Intake
inner_intake_id = 13
outer_intake_back_id = 17
deploy_intake_id = 12

intake_inner_speed = 0.2
intake_inner_pass_speed = .1
intake_inner_eject_speed = 1
intake_outer_speed = 1
intake_outer_idle_speed = .15
intake_outer_eject_speed = 1

deploy_intake_timeout = .25
deploy_tenting_timeout = .1

intake_timeout = 5
intake_roller_current_limit = 18
intake_deploy_current_limit = 30
tenting_deploy_current_limit = 30
intake_sensor_debounce = 0.1
intake_distance_sensor_threshold: float = 0.3

double_note_timeout = 2

# Elevator

elevator_can_id: int = 10
elevator_can_id_2: int = 15
elevator_ramp_rate: float = .2
elevator_feed_forward: float = 0.0 
elevator_climb_ff: float = -3.7
elevator_moving = False
elevator_zeroed_pos = 0.036 if comp_bot.get() else 0.023 
#helloworld
# Wrist
wrist_zeroed_pos = 0.0
wrist_motor_id = 2
wrist_time_to_max_vel = 0.0
feed_motor_id = 3
feed_motor_ramp_rate = 0
wrist_flat_ff = -1
stage_timeout = 5
wrist_tent_limit = 15 * degrees_to_radians
feeder_velocity = .2
feeder_voltage_feed = 8
feeder_voltage_trap = 14
feeder_voltage_crawl = 4
feeder_pass_velocity = .5
feeder_pass_voltage = 2
feeder_sensor_threshold = .65
feeder_beam_break_first_channel = 1
feeder_beam_break_second_channel = 0

# DRIVETRAIN
front_left_move_id = 7
front_left_turn_id = 8
front_left_encoder_port = AnalogEncoder(3)
front_left_encoder_zeroed_pos = 0.487 if comp_bot.get() else 0.860

front_right_move_id = 4
front_right_turn_id = 6
front_right_encoder_port = AnalogEncoder(2)
front_right_encoder_zeroed_pos = 0.793 if comp_bot.get() else 0.536

back_left_move_id = 11
back_left_turn_id = 14
back_left_encoder_port = AnalogEncoder(1 if comp_bot.get() else 0)
back_left_encoder_zeroed_pos = 0.221 if comp_bot.get() else 0.458

back_right_move_id = 18
back_right_turn_id = 16
back_right_encoder_port = AnalogEncoder(0 if comp_bot.get() else 1)
back_right_encoder_zeroed_pos = 0.151 if comp_bot.get() else 0.984
driver_centric: bool = True
drivetrain_reversed: bool = False

# Flywheel
flywheel_id_1 = 19
flywheel_id_2 = 1
flywheel_motor_count = 1
flywheel_amp_speed: meters = 15
v0_flywheel: meters_per_second = 25
# v0_effective_flywheel: meters_per_second = 12
idle_flywheel: meters_per_second = v0_flywheel / 2
shooter_tol = 0.001  # For aim of shooter
max_sim_times = 100  # To make sure that we don't have infinite while loop
auto_shoot_deadline = 1.2
auto_intake_note_deadline = 3
flywheel_feed_forward = 0.0  # TODO: placeholder
flywheel_shot_tolerance: meters_per_second = .5
flywheel_shot_current_threshold = 20

flywheel_manual: bool = False

# Odometry
odometry_visible_tags_threshold = 1
odometry_tag_span_threshold = 0
odometry_tag_distance_threshold = 4

# Configs 
ELEVATOR_CONFIG = SparkMaxConfig(
    0.3, 0.0, 0.02, elevator_feed_forward, (-.65, 1), idle_mode=rev.CANSparkMax.IdleMode.kBrake
)
WRIST_CONFIG = SparkMaxConfig(.55, 0, 0.002, 0, (-.75, .5), idle_mode=rev.CANSparkMax.IdleMode.kBrake)
FEED_CONFIG = SparkMaxConfig(0.08, 0, 0, idle_mode=rev.CANSparkMax.IdleMode.kBrake)
INNER_CONFIG = SparkMaxConfig(.08, 0, 0, idle_mode=rev.CANSparkMax.IdleMode.kBrake)
OUTER_CONFIG = SparkMaxConfig(.5, 0, 0, idle_mode=rev.CANSparkMax.IdleMode.kBrake)
DEPLOY_CONFIG = SparkMaxConfig(.5, 0, 0, idle_mode=rev.CANSparkMax.IdleMode.kBrake)
FLYWHEEL_CONFIG = SparkMaxConfig(
    0.055, 0.0, 0.01, flywheel_feed_forward, idle_mode=rev.CANSparkMax.IdleMode.kCoast
)

TURN_CONFIG = SparkMaxConfig(
    0.2, 0, 0.003, 0.00015, (-0.5, 0.5), rev.CANSparkMax.IdleMode.kBrake
)
MOVE_CONFIG = TalonConfig(
    0.11, 0, 0, 0.25, 0.01, brake_mode=True, current_limit=60  # integral_zone=1000, max_integral_accumulator=10000
)

# Giraffe

staging_angle:radians = 60 * degrees_to_radians


class Giraffe:
    class GiraffePos:
        class Special(Enum):
            kStage = 0
            kAim = 1
            kHeightAuto = 2
            kCurrentAngle = 3
            kCurrentHeight = 4

        def __init__(self, height: meters | Special, wrist_angle: radians | Special):
            self.height = height
            self.wrist_angle = wrist_angle

    kIdle = GiraffePos(0, staging_angle)

    kStage = GiraffePos(0, GiraffePos.Special.kStage)

    kAim = GiraffePos(GiraffePos.Special.kCurrentAngle, GiraffePos.Special.kAim)

    kAimLow = GiraffePos(0, GiraffePos.Special.kAim)

    kAimHigh = GiraffePos(constants.elevator_max_length, GiraffePos.Special.kAim)

    kClimbReach = GiraffePos(constants.elevator_max_length, 10*degrees_to_radians)

    kClimbPullUp = GiraffePos(0, 50*degrees_to_radians)

    kTestFF = GiraffePos(0, 20 * degrees_to_radians)

    kClimbTrap = GiraffePos(constants.elevator_max_length, 30 * degrees_to_radians)

    kAmp = GiraffePos(0.27, 0 * degrees_to_radians)

    kElevatorHigh = GiraffePos(constants.elevator_max_length, GiraffePos.Special.kCurrentAngle)

    kElevatorLow = GiraffePos(0, GiraffePos.Special.kCurrentAngle)

    kElevatorMid = GiraffePos(constants.elevator_max_length / 2, GiraffePos.Special.kCurrentAngle)


"""
c = drag coefficient
a = projectile area (m^2)
m = projectile mass (kg)
rho_air = air density (kg/m^3)
g = acceleration due to gravity (m/s^2)
v0 = initial velocity of shooter flywheel (m/s) config
delta_x = distance from shooter to target (COULD BE IN ODOMETRY) (m)
y = height of target (COULD BE IN ODOMETRY) (m) const
tol = tolerance of error in distance to target (m)
"""

# Gyro
gyro_id = 29
