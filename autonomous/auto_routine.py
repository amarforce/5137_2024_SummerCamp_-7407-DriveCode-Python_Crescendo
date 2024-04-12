from dataclasses import dataclass

import commands2
from commands2 import CommandBase
from wpimath.geometry import Pose2d

import config
from robot_systems import Robot
from utils import POIPose


@dataclass
class AutoRoutine:
    """
    Base auto-routine class.

    :param initial_robot_pose: Initial robot pose.
    :type initial_robot_pose: Pose2d
    :param command: Command to run.
    :type command: CommandBase
    """

    initial_robot_pose: Pose2d
    command: CommandBase

    def run(self):
        """
        Runs the autonomous routine
        """

        # Robot.drivetrain.gyro.reset_angle(self.initial_robot_pose.rotation().radians())
        if config.active_team == config.Team.RED:
            self.initial_robot_pose = Pose2d(self.initial_robot_pose.X(), self.initial_robot_pose.Y(), self.initial_robot_pose.rotation().radians() *-1)
        Robot.drivetrain.reset_odometry(POIPose(self.initial_robot_pose).get())

        commands2.CommandScheduler.getInstance().schedule(self.command)
        