import logging

import wpilib
from toolkit.command import SubsystemCommand

import config, constants
from subsystem import Drivetrain
from sensors import TrajectoryCalculator
from wpimath.controller import PIDController, ProfiledPIDControllerRadians
from wpimath.trajectory import TrapezoidProfileRadians
from toolkit.utils.toolkit_math import bounded_angle_diff
from math import radians
def curve_abs(x):
    curve = wpilib.SmartDashboard.getNumber('curve', 2)
    return x ** curve


def curve(x):
    if x < 0:
        return -curve_abs(-x)
    return curve_abs(x)


def bound_angle(degrees:float):
    degrees = degrees % 360
    if degrees > 180:
        degrees -= 360
    return degrees
    

class DriveSwerveCustom(SubsystemCommand[Drivetrain]):
    """
    Main drive command
    """
    driver_centric = False
    driver_centric_reversed = True

    def initialize(self) -> None:
        pass

    def execute(self) -> None:
        dx, dy, d_theta = (
            self.subsystem.axis_dx.value * (-1 if config.drivetrain_reversed else 1),
            self.subsystem.axis_dy.value * (-1 if config.drivetrain_reversed else 1),
            -self.subsystem.axis_rotation.value,
        )

        if abs(d_theta) < 0.11:
            d_theta = 0

        dx = curve(dx)
        dy = curve(dy)
        d_theta = curve(d_theta)

        dx *= self.subsystem.max_vel
        dy *= -self.subsystem.max_vel
        d_theta *= self.subsystem.max_angular_vel

        if config.driver_centric:
            self.subsystem.set_driver_centric((dy, -dx), -d_theta)
        elif self.driver_centric_reversed:
            self.subsystem.set_driver_centric((-dy, dx), d_theta)
        else:
            self.subsystem.set_robot_centric((dy, -dx), d_theta)

    def end(self, interrupted: bool) -> None:
        self.subsystem.n_front_left.set_motor_velocity(0)
        self.subsystem.n_front_right.set_motor_velocity(0)
        self.subsystem.n_back_left.set_motor_velocity(0)
        self.subsystem.n_back_right.set_motor_velocity(0)

    def isFinished(self) -> bool:
        return False

    def runsWhenDisabled(self) -> bool:
        return False
    
    
class DriveSwerveAim(SubsystemCommand[Drivetrain]):
    """
    Aim drivetrain at speaker based on shooter calculations
    """
    driver_centric = False
    driver_centric_reversed = True
    
    def __init__(self, drivetrain, target_calc: TrajectoryCalculator):
        super().__init__(drivetrain)
        self.target_calc = target_calc
        # self.theta_controller = PIDController(0.0075, 0, 0.0001, config.period)
        constraints = TrapezoidProfileRadians.Constraints(self.subsystem.max_angular_vel, constants.drivetrain_max_angular_accel)
        self.theta_controller = ProfiledPIDControllerRadians(
            9, 0, .003,
            constraints,
            config.
            period
            )
        self.theta_controller.setTolerance(radians(1), radians(3))

    def initialize(self) -> None:
        self.theta_controller.enableContinuousInput(radians(-180), radians(180))
        self.theta_controller.reset(
            self.subsystem.odometry_estimator.getEstimatedPosition().rotation().radians(),
            self.subsystem.chassis_speeds.omega
            )

    def execute(self) -> None:
        dx, dy = (
            self.subsystem.axis_dx.value * (-1 if config.drivetrain_reversed else 1),
            self.subsystem.axis_dy.value * (-1 if config.drivetrain_reversed else 1),
        )
        
        
        target_angle = self.target_calc.get_bot_theta()
        d_theta = self.theta_controller.calculate(bound_angle(self.subsystem.odometry_estimator.getEstimatedPosition().rotation().radians()), target_angle.radians())
        
        
        # if bounded_angle_diff(self.subsystem.odometry_estimator.getEstimatedPosition().rotation().radians(), target_angle.radians()) < radians(1):
        #     self.subsystem.ready_to_shoot = True
        # else:
        #     self.subsystem.ready_to_shoot = False
        
        if self.theta_controller.atSetpoint():
            self.subsystem.ready_to_shoot = True
        else:
            self.subsystem.ready_to_shoot = False

        dx = curve(dx)
        dy = curve(dy)

        dx *= self.subsystem.max_vel
        dy *= -self.subsystem.max_vel
        # d_theta *= self.subsystem.max_angular_vel

        if config.driver_centric:
            self.subsystem.set_driver_centric((dy, -dx), -d_theta)
        elif self.driver_centric_reversed:
            self.subsystem.set_driver_centric((-dy, dx), d_theta)
        else:
            self.subsystem.set_robot_centric((dy, -dx), d_theta)

    def end(self, interrupted: bool) -> None:
        self.subsystem.ready_to_shoot = False
        self.subsystem.n_front_left.set_motor_velocity(0)
        self.subsystem.n_front_right.set_motor_velocity(0)
        self.subsystem.n_back_left.set_motor_velocity(0)
        self.subsystem.n_back_right.set_motor_velocity(0)

    def isFinished(self) -> bool:
        return False

    def runsWhenDisabled(self) -> bool:
        return False


class DrivetrainZero(SubsystemCommand[Drivetrain]):
    """
    Zeroes drivetrain
    """
    def __init__(self, subsystem: Drivetrain):
        super().__init__(subsystem)
        self.subsystem = subsystem

    def initialize(self) -> None:
        print("ZEROING DRIVETRAIN")
        self.subsystem.gyro.reset_angle()
        self.subsystem.n_front_left.zero()
        self.subsystem.n_front_right.zero()
        self.subsystem.n_back_left.zero()
        self.subsystem.n_back_right.zero()

    def execute(self) -> None:
        pass

    def isFinished(self) -> bool:
        return True

    def end(self, interrupted: bool) -> None:
        logging.info("Successfully re-zeroed swerve pods.")
        ...
