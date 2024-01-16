import commands2
from toolkit.subsystem import Subsystem
import ntcore
import wpilib
import command
import config
import constants
from robot_systems import Robot, Pneumatics, Sensors, LEDs, PowerDistribution, Field
import sensors
import subsystem
import utils
from oi.OI import OI
from oi.IT import IT
from wpilib import SmartDashboard
import autonomous

class _Robot(wpilib.TimedRobot):
    def __init__(self):
        super().__init__()
        ...
        self.log = utils.LocalLogger("Robot")
        self.nt = ntcore.NetworkTableInstance.getDefault()
        self.scheduler = commands2.CommandScheduler.getInstance()

        self.auto_selection: wpilib.SendableChooser | None = None

    def robotInit(self):
        ...
        self.log._robot_log_setup()

        if config.DEBUG_MODE:
            self.log.setup("WARNING: DEBUG MODE IS ENABLED")

        # Initialize Operator Interface
        OI.init()
        OI.map_controls()

        IT.init()
        IT.map_systems()
        period = .03
        self.scheduler.setPeriod(period)

        self.log.info(f"Scheduler period set to {period} seconds")

        # Initialize subsystems and sensors
        def init_subsystems():
            subsystems: list[Subsystem] = list(
                {k: v for k, v in Robot.__dict__.items() if isinstance(v, Subsystem) and hasattr(v, 'init')}.values()
            )

            for subsystem in subsystems:
                subsystem.init()

        try:
            init_subsystems()
        except Exception as e:
            self.log.error(str(e))
            self.nt.getTable('errors').putString('subsystem init', str(e))

            if config.DEBUG_MODE:
                raise e

        def init_sensors():
            sensors: list[Sensors] = list(
                {k: v for k, v in Sensors.__dict__.items() if isinstance(v, Sensors) and hasattr(v, 'init')}.values()
            )

            # for sensor in sensors:
            #     sensor.init()
            Sensors.limelight.init()
            Sensors.odometry.enable()

        try:
            init_sensors()
        except Exception as e:
            self.log.error(str(e))
            self.nt.getTable('errors').putString('sensor init', str(e))

            if config.DEBUG_MODE:
                raise e

        self.log.complete("Robot initialized")

        # Auto Selection
        self.auto_selection = wpilib.SendableChooser()

        self.auto_selection.setDefaultOption("Drive Straight", autonomous.drive_straight)

    def robotPeriodic(self):
        ...
        if self.isSimulation():
            wpilib.DriverStation.silenceJoystickConnectionWarning(True)

        try:
            self.scheduler.run()
        except Exception as e:
            self.log.error(str(e))
            self.nt.getTable('errors').putString('command scheduler', str(e))

            if config.DEBUG_MODE:
                raise e

        try:
            # Sensors.limelight_back.update()
            # Sensors.limelight_front.update()
            Sensors.limelight.update()
        except Exception as e:
            self.log.error(str(e))
            self.nt.getTable('errors').putString('limelight update', str(e))

            if config.DEBUG_MODE:
                raise e

        try:
            Sensors.odometry.update()
        except Exception as e:
            self.log.error(str(e))
            self.nt.getTable('errors').putString('odometry update', str(e))

            if config.DEBUG_MODE:
                raise e

        pose = Sensors.odometry.getPose()
        self.nt.getTable("Odometry").putNumberArray(
            "Estimated Pose", [
                pose.X(),
                pose.Y(),
                pose.rotation().radians()
            ]
        )

    def teleopInit(self):
        # self.log.info("Teleop initialized")
        ...
        self.scheduler.schedule(commands2.SequentialCommandGroup(
            command.DrivetrainZero(Robot.drivetrain),
            command.DriveSwerveCustom(Robot.drivetrain)
        )
        )

    def teleopPeriodic(self):
        ...

    def autonomousInit(self):
        self.log.info("Autonomous initialized")

        Robot.drivetrain.n_front_left.zero()
        Robot.drivetrain.n_front_right.zero()
        Robot.drivetrain.n_back_left.zero()
        Robot.drivetrain.n_back_right.zero()

        config.active_team = config.Team.BLUE

        self.auto_selection.getSelected().run()

    def autonomousPeriodic(self):
        pass

    def disabledInit(self) -> None:
        self.log.info("Robot disabled")
        ...

    def disabledPeriodic(self) -> None:
        pass


if __name__ == "__main__":
    wpilib.run(_Robot)
