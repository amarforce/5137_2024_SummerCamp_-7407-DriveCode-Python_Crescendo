import math
from math import pi

import config
import ntcore
import constants
from toolkit.motors.rev_motors import SparkMax
from toolkit.subsystem import Subsystem
from toolkit.utils.toolkit_math import bounded_angle_diff
from units.SI import radians
from wpilib import DigitalInput


class Wrist(Subsystem):
    def __init__(self):
        super().__init__()
        self.wrist_motor = SparkMax(
            can_id=config.wrist_motor_id, inverted=True, config=config.WRIST_CONFIG
        )

        self.feed_motor = SparkMax(
            can_id=config.feed_motor_id, inverted=True, config=config.FEED_CONFIG
        )
        self.note_staged: bool = False
        self.wrist_zeroed: bool = False
        self.rotation_disabled: bool = False
        self.feed_disabled: bool = False
        self.beam_break_first: DigitalInput = None
        self.beam_break_second: DigitalInput = None   
        self.disable_rotation: bool = False
        self.locked: bool = False
        self.ready_to_shoot: bool = False
        self.target_angle: radians = 0
        self.wrist_moving: bool = False

    def init(self):
        self.wrist_motor.init()
        # self.wrist_motor.motor.restoreFactoryDefaults(True)
        self.wrist_motor.motor.setClosedLoopRampRate(config.wrist_time_to_max_vel)
        # self.wrist_motor.pid_controller.setFeedbackDevice(self.wrist_motor.abs_encoder())
        # self.wrist_motor.pid_controller.setFeedbackDevice(self.wrist_motor.encoder)
        
        # self.wrist_motor.pid_controller.setPositionPIDWrappingEnabled(False)
        # self.wrist_motor.pid_controller.setPositionPIDWrappingMinInput(self.radians_to_abs(constants.wrist_max_rotation))
        # self.wrist_motor.pid_controller.setPositionPIDWrappingMaxInput(self.radians_to_abs(constants.wrist_min_rotation))
        # self.wrist_motor.motor.burnFlash()
        self.wrist_abs_encoder = self.wrist_motor.abs_encoder()
        self.feed_motor.init()
        self.beam_break_first = DigitalInput(config.feeder_beam_break_first_channel)
        self.beam_break_second = DigitalInput(config.feeder_beam_break_second_channel)

    def limit_angle(self, angle: radians) -> radians:
        if self.locked and angle <= constants.wrist_min_rotation_stage:
            return constants.wrist_min_rotation_stage
        if angle <= constants.wrist_min_rotation:
            return constants.wrist_min_rotation
        elif angle >= constants.wrist_max_rotation:
            return constants.wrist_max_rotation
        return angle
    
    @staticmethod
    def abs_to_radians(abs_angle: float) -> radians:
        if abs_angle > .5:
            return (1 - abs_angle) * -2 * math.pi
        else:
            return abs_angle * 2 * math.pi
        
    @staticmethod
    def radians_to_abs(angle: radians) -> float:
        if angle < 0:
            return 1 - (angle / (-2 * math.pi))
        else:
            return angle / (2 * math.pi)

    # wrist methods
    def set_wrist_angle(self, angle: radians):
        """
        Sets the wrist angle to the given position
        :param pos: The position to set the wrist to(float)
        :return: None
        """
        angle = self.limit_angle(angle)
        self.target_angle = angle

        current_angle = self.get_wrist_angle()

        ff = config.wrist_flat_ff * math.cos(angle) #* (1 if angle < current_angle else -1)

        if not self.rotation_disabled:
            self.wrist_motor.set_target_position(
                (angle / (pi * 2)) * constants.wrist_gear_ratio,
                ff# if angle < current_angle else 0
            )

    def get_wrist_angle(self):
        """
        Gets the wrist rotation in radians
        :return:
        """
        return (
                (self.wrist_motor.get_sensor_position() / constants.wrist_gear_ratio)
                * pi
                * 2
        )
        
        # return (
        #     (self.wrist_abs_encoder.getPosition())
        # )

    def note_detected(self) -> bool:
        return not self.beam_break_second.get()

    def detect_note_first(self) -> bool:
        return not self.beam_break_first.get()
    
    def detect_note_second(self) -> bool:
        return not self.beam_break_second.get()

    def is_at_angle(self, angle: radians, threshold=math.radians(2)):
        """
        Checks if the wrist is at the given angle
        :param angle: The angle to check for
        :param threshold: The threshold to check for
        :return: True if the wrist is at the given angle, False otherwise
        """
        return abs(bounded_angle_diff(self.get_wrist_angle(), angle)) < threshold

    def get_wrist_abs_angle(self):

        angle = self.wrist_abs_encoder.getPosition() - config.wrist_zeroed_pos

        return self.abs_to_radians(angle)

    def zero_wrist(self) -> None:  # taken from cyrus' code
        # Reset the encoder to zero

        pos = (self.get_wrist_abs_angle() / (2 * math.pi)) * constants.wrist_gear_ratio
        print(math.degrees(self.get_wrist_abs_angle()))
        print(pos)
        self.wrist_motor.set_sensor_position(
            pos
        )
        self.wrist_zeroed = True

    # feed in methods
    def feed_in(self):
        if not self.feed_disabled:
            # self.feed_motor.set_target_velocity(config.feeder_velocity)
            # self.feed_motor.set_raw_output(config.feeder_velocity)
            self.feed_motor.set_target_voltage(config.feeder_voltage_feed)

    def set_feed_voltage(self, voltage: float):
        self.feed_motor.set_target_voltage(voltage)

    def feed_out(self):
        if not self.feed_disabled:
            # self.feed_motor.set_target_velocity(-(config.feeder_velocity))
            # self.feed_motor.set_raw_output(-(config.feeder_velocity))
            self.feed_motor.set_target_voltage(-config.feeder_voltage_trap)

    def stop_feed(self):
        # self.feed_motor.set_target_position(self.feed_motor.get_sensor_position())
        # self.feed_motor.set_raw_output(0)
        self.feed_motor.set_target_voltage(0)
        
    def feed_idle(self):
        self.feed_motor.set_target_voltage(3)

    def feed_note(self):
        if not self.feed_disabled:
            # self.feed_motor.set_raw_output(config.feeder_pass_velocity)
            self.feed_motor.set_target_voltage(config.feeder_pass_voltage)

    def set_note_staged(self):
        self.note_staged = True

    def set_note_not_staged(self):
        self.note_staged = False

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def periodic(self) -> None:
        # self.zero_wrist()
        table = ntcore.NetworkTableInstance.getDefault().getTable('wrist')

        # table.putNumber('wrist angle', math.degrees(self.get_wrist_angle()))
        table.putNumber('wrist abs angle', math.degrees(self.get_wrist_abs_angle()))
        # table.putNumber('wrist abs raw', self.wrist_abs_encoder.getPosition())
        table.putNumber('wrist angle', math.degrees(self.get_wrist_angle()))
        table.putBoolean('note in feeder', self.note_staged)
        table.putBoolean('note detected', self.note_detected())
        table.putBoolean('wrist zeroed', self.wrist_zeroed)
        table.putBoolean('ready to shoot', self.ready_to_shoot)
        table.putBoolean('first beam break', not self.beam_break_first.get())
        table.putBoolean('second beam break', not self.beam_break_second.get())
        table.putBoolean('rotation disabled', self.rotation_disabled)
        table.putBoolean('feed disabled', self.feed_disabled)
        table.putBoolean('locked', self.locked)
        table.putNumber('target angle', math.degrees(self.target_angle))
        table.putNumber('target angle raw', self.radians_to_abs(self.target_angle))
        table.putBoolean('wrist moving', self.wrist_moving)
        table.putNumber('wrist current', self.wrist_motor.motor.getOutputCurrent())
        table.putNumber('wrist applied output', self.wrist_motor.motor.getAppliedOutput())
