from command.autonomous.custom_pathing import FollowPathCustom, AngleType
from command.autonomous.trajectory import CustomTrajectory, PoseType
from robot_systems import Robot, Field
from utils import POIPose
from command import *
import config
import math

from commands2 import (
    InstantCommand,
    SequentialCommandGroup,
    ParallelCommandGroup,
    WaitCommand
)

from autonomous.auto_routine import AutoRoutine
from autonomous.routines.FOUR_NOTE_MIDDLE.coords import (
    get_first_note,
    get_second_note,
    get_third_note,
    go_to_midline,
    shoot_last_note,
    initial
)


from wpimath.geometry import Pose2d, Translation2d

path_1 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        # start_pose=POIPose(Pose2d(*get_first_note[0])),
        start_pose=PoseType.current,
        waypoints=[Translation2d(*coord) for coord in get_first_note[1]],
        end_pose=get_first_note[2],
        max_velocity=config.drivetrain_max_vel_auto,
        max_accel=config.drivetrain_max_accel_auto - 1.5,
        start_velocity=0,
        end_velocity=0,
        rev=True,
        start_rotation=math.radians(-135)
    ),
    theta_f=AngleType.calculate
)

path_2 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        # start_pose=get_second_note[0],
        start_pose=PoseType.current,
        waypoints=[coord for coord in get_second_note[1]],
        end_pose=get_second_note[2],
        max_velocity=config.drivetrain_max_vel_auto,
        max_accel=config.drivetrain_max_accel_auto - 1.5,
        start_velocity=0,
        end_velocity=0,
        rev=False,
        start_rotation=get_second_note[0].get().rotation().radians()
    ),
    theta_f=AngleType.calculate
)

path_3 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        # start_pose=get_third_note[0],
        start_pose=PoseType.current,
        waypoints=[coord for coord in get_third_note[1]],
        end_pose=get_third_note[2],
        max_velocity=config.drivetrain_max_vel_auto,
        max_accel=config.drivetrain_max_accel_auto - 1.5,
        start_velocity=0,
        end_velocity=0,
        rev=False,
        start_rotation=get_third_note[0].get().rotation().radians()
    ),
    theta_f=AngleType.calculate
)

path_4 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        # start_pose=go_to_midline[0],
        start_pose=PoseType.current,
        waypoints=[coord for coord in go_to_midline[1]],
        end_pose=go_to_midline[2],
        max_velocity=config.drivetrain_max_vel_auto,
        max_accel=config.drivetrain_max_accel_auto,
        start_velocity=0,
        end_velocity=0,
        rev=True,
        start_rotation=go_to_midline[0].get().rotation().radians()
    ),
    theta_f=math.radians(-180)
)

path_5 = FollowPathCustom(
    subsystem=Robot.drivetrain,
    trajectory=CustomTrajectory(
        start_pose=PoseType.current,
        waypoints=[coord for coord in shoot_last_note[1]],
        end_pose=shoot_last_note[2],
        max_velocity=config.drivetrain_max_vel_auto,
        max_accel=config.drivetrain_max_accel_auto - 1.5,
        start_velocity=0,
        end_velocity=0,
        rev=False,
        start_rotation=go_to_midline[0].get().rotation().radians()
    ),
    theta_f=AngleType.calculate
)

auto = ParallelCommandGroup(
    SetFlywheelShootSpeaker(Robot.flywheel, Field.calculations),
    SequentialCommandGroup(
        ZeroWrist(Robot.wrist),
        ZeroElevator(Robot.elevator),

        # Shoot first note preload and deploy intake`   `
        DeployIntake(Robot.intake).withTimeout(1),
        PassNote(Robot.wrist),
        
        # Get second note
        PathUntilIntake(path_1, Robot.wrist, Robot.intake, 1.5),

        # Shoot second note
        ShootAuto(Robot.drivetrain, Robot.wrist, Robot.flywheel, Field.calculations),


        # Get third note
        PathUntilIntake(path_2, Robot.wrist, Robot.intake, 1.5),

        # Shoot third note
        ShootAuto(Robot.drivetrain, Robot.wrist, Robot.flywheel, Field.calculations),

        # Get fourth note
        PathUntilIntake(path_3, Robot.wrist, Robot.intake, 1.5),

        # Shoot fourth note
        ShootAuto(Robot.drivetrain, Robot.wrist, Robot.flywheel, Field.calculations),

        # Get fifth note, go to midline
        PathUntilIntake(path_4, Robot.wrist, Robot.intake),
        # path_4,
        # AutoPickupNote

        path_5,
        
        ShootAuto(Robot.drivetrain, Robot.wrist, Robot.flywheel, Field.calculations)
    )
    # SequentialCommandGroup(
    #     path_1,
    #     path_2,
    #     path_3,
    #     path_4,
    #     path_5
    # )
)

routine = AutoRoutine(Pose2d(*initial), auto)
