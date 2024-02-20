from command.autonomous.custom_pathing import FollowPathCustom
from command.autonomous.trajectory import CustomTrajectory
from command import DrivetrainZero, Giraffe, RunIntake, PassNote, SetFlywheelLinearVelocity
from robot_systems import Robot
from utils import POIPose
import config

from commands2 import (
    InstantCommand,
    SequentialCommandGroup,
    ParallelCommandGroup,
    WaitCommand
)

from autonomous.auto_routine import AutoRoutine
from autonomous.routines.MIDLINE_NOTES.coords import (
    initial,
    get_first_ring,
    come_back_to_shoot_first_ring,
    get_second_ring,
    come_back_to_shoot_second_ring,
    get_third_ring,
    come_back_to_shoot_third_ring,
)

from wpimath.geometry import Pose2d, Translation2d

path_1 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        start_pose=POIPose(Pose2d(*get_first_ring[0])),
        waypoints=[Translation2d(*coord) for coord in get_first_ring[1]],
        end_pose=get_first_ring[2],
        max_velocity=12,
        max_accel=3,
        start_velocity=0,
        end_velocity=0,
        rev=True,
    ),
    period=0.03,
)

path_2 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        start_pose=come_back_to_shoot_first_ring[0],
        waypoints=[Translation2d(*coord) for coord in come_back_to_shoot_first_ring[1]],
        end_pose=come_back_to_shoot_first_ring[2],
        max_velocity=12,
        max_accel=3,
        start_velocity=0,
        end_velocity=0,
        rev=False,
    ),
    period=0.03,
)

path_3 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        start_pose=get_second_ring[0],
        waypoints=[Translation2d(*coord) for coord in get_second_ring[1]],
        end_pose=get_second_ring[2],
        max_velocity=12,
        max_accel=3,
        start_velocity=0,
        end_velocity=0,
        rev=True,
    ),
    period=0.03,
)

path_4 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        start_pose=come_back_to_shoot_second_ring[0],
        waypoints=[Translation2d(*coord) for coord in come_back_to_shoot_second_ring[1]],
        end_pose=come_back_to_shoot_second_ring[2],
        max_velocity=12,
        max_accel=3,
        start_velocity=0,
        end_velocity=0,
        rev=False,
    ),
    period=0.03,
)

path_5 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        start_pose=get_third_ring[0],
        waypoints=[Translation2d(*coord) for coord in get_third_ring[1]],
        end_pose=get_third_ring[2],
        max_velocity=12,
        max_accel=3,
        start_velocity=0,
        end_velocity=0,
        rev=True,
    ),
    period=0.03,
)

path_6 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        start_pose=come_back_to_shoot_third_ring[0],
        waypoints=[Translation2d(*coord) for coord in come_back_to_shoot_third_ring[1]],
        end_pose=come_back_to_shoot_third_ring[2],
        max_velocity=12,
        max_accel=3,
        start_velocity=0,
        end_velocity=0,
        rev=False,
    ),
    period=0.03,
)

# Between paths, need to score rings
auto = SequentialCommandGroup(
    DrivetrainZero(Robot.drivetrain),
    ParallelCommandGroup(
        SetFlywheelLinearVelocity(Robot.flywheel, 5),
        SequentialCommandGroup(
            Giraffe(Robot.elevator, Robot.wrist, config.Giraffe.kAim), # aim
            PassNote(Robot.wrist), # shoot
            path_1,
            RunIntake(Robot.intake), # intake
            path_2,
            Giraffe(Robot.elevator, Robot.wrist, config.Giraffe.kAim), # aim
            PassNote(Robot.wrist), # shoot
            path_3,
            RunIntake(Robot.intake), # intake
            path_4,
            Giraffe(Robot.elevator, Robot.wrist, config.Giraffe.kAim), # aim
            PassNote(Robot.wrist), # shoot
            path_5,
            RunIntake(Robot.intake), # intake
            path_6,
            Giraffe(Robot.elevator, Robot.wrist, config.Giraffe.kAim), # aim
            PassNote(Robot.wrist), # shoot
            
            InstantCommand(lambda: print("Done")),
        )
    )
)

routine = AutoRoutine(Pose2d(*initial), auto)
