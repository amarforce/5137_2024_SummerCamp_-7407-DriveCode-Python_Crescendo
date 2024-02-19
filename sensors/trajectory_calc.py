from enum import IntEnum
from math import degrees  # noqa
from typing import Callable, List, Tuple

import numpy as np
from wpimath.geometry import Pose2d, Pose3d, Rotation2d, Rotation3d, Translation3d

import config
import constants
from sensors.field_odometry import FieldOdometry
from subsystem import Elevator
from toolkit.utils.toolkit_math import NumericalIntegration, extrapolate
from units.SI import radians
from utils import POI, POIPose


class TargetVariable(IntEnum):
    """
    Enum for target variables
    """

    X = 0
    XDOT = 1
    Z = 2
    ZDOT = 3


class TargetCriteria:
    """
    Target criteria helps us understand what we will be using as a criteria
    for hitting that target. With the speaker we want to note to fly a specific
    horizontal distance then look at the vertical height. The criteria variable in
    that case is X and the target variable is Z.
    """

    def __init__(
        self,
        target_variable: TargetVariable,
        criteria_variable: TargetVariable = None,
        criteria_value: float = None,
        end_condition: Callable[[float, List[float]], bool] = None,
    ):
        self.target_variable = target_variable
        self.criteria_variable = criteria_variable
        self.criteria_value = criteria_value
        self.end_condition_function = end_condition

    def set_criteria_value(self, criteria_value: float):
        self.criteria_value = criteria_value

    def end_condition(self, t: float, y: List[float]) -> bool:
        if self.end_condition_function:
            return self.end_condition_function(t, y)
        return y[self.criteria_variable] > self.criteria_value


class Target:
    """
    Class for target to shoot at
    """

    def __init__(
        self,
        pose: POIPose,
        velocity: float,
        criteria: TargetCriteria,
    ):
        self.pose = pose
        self.velocity = velocity
        self.criteria = criteria

    def get_pose2d(self) -> Pose2d:
        return self.pose.get()

    def get_poseZ(self) -> float:
        return self.pose.getZ()


# Targets
speaker_target_pose = Pose3d(
    Translation3d(
        constants.FieldPos.Scoring.speaker_x,
        constants.FieldPos.Scoring.speaker_y,
        constants.FieldPos.Scoring.speaker_z,
    ),
    Rotation3d(0, 0, 0),
)
target_criteria = TargetCriteria(TargetVariable.Z, TargetVariable.X, 5.0)
speaker_target = Target(
    POI.Coordinates.Structures.Scoring.kSpeaker, 25, target_criteria
)


class TrajectoryCalculator:
    """
    TODO: FIND DRAG COEFFICIENT!!!!!!

    Game-piece trajectory calculator that updates based on odometry and vision data.
    """

    def __init__(self, odometry: FieldOdometry, elevator: Elevator, target: Target):
        self.odometry = odometry
        self.target = target
        self.k = 0.5 * constants.c * constants.rho_air * constants.a
        self.shoot_angle = 0
        self.elevator = elevator
        self.numerical_integration = NumericalIntegration()
        self.use_air_resistance = False

    def init(self, set_air_resistance: bool = False):
        self.use_air_resistance = set_air_resistance

    def set_target(self, target: Target):
        self.target = target

    @staticmethod
    def calculate_distance_to_target(
        robot_pose: Pose2d, target_pose: Pose3d, shooter_height: float
    ) -> Tuple[float, float]:
        # Determine horizontal distance
        delta_x = robot_pose.translation().distance(
            target_pose.toPose2d().translation()
        )
        # Determine vertical distance
        delta_z = target_pose.translation().Z() - shooter_height
        return delta_x, delta_z

    def target_horizontal_distance(self) -> float:
        """
        Returns the horizontal distance to the target.
        @return: A float indicated the distance from the target to the robot pose
        """
        return (
            self.odometry.getPose()
            .translation()
            .distance(self.target.get_pose2d().translation())
        )

    def target_vertical_distance(self) -> float:
        """
        Returns the vertical distance to the target.

        @return: a float indicating the vertical distance to the target
        """
        return self.target.get_poseZ() - (
            constants.shooter_height + self.elevator.get_length()
        )

    def calculate_angle_no_air(self) -> float:
        """
        Calculates the angle of the trajectory without air resistance.

        @return: the angle of the trajectory without air resistance
        """
        # update the distances
        delta_x = self.target_horizontal_distance()
        delta_z = self.target_vertical_distance()
        # print(f"odometryPose: {self.odometry.getPose()}")
        # print(f"targetPose: {self.target.get_pose2d()}")
        # print(f"delta_x: {delta_x}, delta_z: {delta_z}")
        # print(f"speed: {self.target.velocity}")

        phi0 = np.arctan(delta_z / delta_x)
        result_angle = (
            0.5
            * np.arcsin(
                np.sin(phi0)
                + constants.g * delta_x * np.cos(phi0) / (self.target.velocity**2)
            )
            + 0.5 * phi0
        )
        return result_angle

    def get_wrist_angle(self) -> Rotation2d:
        """
        function runs sim to calculate a final angle with air resistance considered

        :return: target angle
        """
        delta_x = self.target_horizontal_distance()
        delta_z = self.target_vertical_distance()
        self.target.criteria.set_criteria_value(delta_x)
        theta_1 = self.calculate_angle_no_air()
        if not self.use_air_resistance:
            self.shoot_angle = theta_1
            return Rotation2d(theta_1)
        theta_2 = theta_1 + np.radians(1)
        z_1 = self.run_sim(theta_1)
        z_2 = self.run_sim(theta_2)
        z_goal_error = delta_z - z_2
        z_to_angle_conversion = (theta_2 - theta_1) / (z_2 - z_1)
        correction_angle = z_goal_error * z_to_angle_conversion
        for i in range(config.max_sim_times):
            theta_1 = theta_2
            theta_2 = theta_2 + correction_angle
            z_1 = z_2
            z_2 = self.run_sim(theta_2)
            z_goal_error = delta_z - z_2
            z_to_angle_conversion = (theta_2 - theta_1) / (z_2 - z_1)
            # print(z_goal_error, theta_2, self.delta_z)
            if abs(z_goal_error) < config.shooter_tol:
                self.shoot_angle = theta_2
                return Rotation2d(theta_2)
            correction_angle = z_goal_error * z_to_angle_conversion

    def get_base_angle(self) -> Rotation2d:
        """
        updates rotation of base to face target

        :return: base target angle
        """
        robot_pose_2d = self.odometry.getPose()
        # print("robot_pose_2d: ", robot_pose_2d)

        robot_to_speaker = (
            self.target.get_pose2d().translation() - robot_pose_2d.translation()
        )
        # print("target", self.target.get_pose2d().translation())
        # print("robot_to_speaker", robot_to_speaker)
        answer = robot_to_speaker.angle().radians()
        if answer < 0:
            answer += 2 * np.pi
        return Rotation2d(answer)

    def update(self):
        """
        updates both shooter and base
        saves results in class variables wrist_angle and base_angle

        """
        self.update_shooter()
        self.update_base()
        self.update_tables()

    def update_tables(self):
        self.table.putNumber("wrist angle", degrees(self.get_theta()))
        self.table.putNumber("distance to target", self.distance_to_target)
        self.table.putNumber("bot angle", self.get_bot_theta().degrees())

    def run_sim(self, shooter_theta: radians) -> float:
        delta_x = self.target_horizontal_distance()
        # print(f"delta_x: {delta_x}")
        self.target.criteria.set_criteria_value(delta_x)
        # Set the initial conditions
        u0 = (
            0,
            self.target.velocity * np.cos(shooter_theta),
            0.0,
            self.target.velocity * np.sin(shooter_theta),
        )
        # One minute should be plenty of time.
        t0, tf = 0, 60
        # Stop the integration when we hit the target.
        t, y = self.numerical_integration.adaptive_rk4(
            self.deriv, u0, t0, tf, 0.5, 1e-7, self.target.criteria.end_condition
        )
        target_variable = int(self.target.criteria.target_variable)
        criteria_variable = int(self.target.criteria.criteria_variable)
        criteria_value = self.target.criteria.criteria_value
        return extrapolate(
            criteria_value,
            y[-2][criteria_variable],
            y[-2][target_variable],
            y[-1][criteria_variable],
            y[-1][target_variable],
        )

    def get_theta(self) -> float:
        """
        Returns the angle of the trajectory.
        """
        return self.shoot_angle

    def deriv(self, t, u):
        x, xdot, z, zdot = u
        speed = np.hypot(xdot, zdot)
        xdotdot = -self.k / constants.m * speed * xdot
        zdotdot = -self.k / constants.m * speed * zdot - constants.g
        return np.array([xdot, xdotdot, zdot, zdotdot])
