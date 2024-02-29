from units.SI import meters, radians, inches_to_meters
from robot_systems import Field
from wpimath.geometry import Translation2d, Pose2d
import constants
from utils import POIPose
import math

coord = (meters, meters, radians)
waypoints = [(meters, meters)]
path = (coord, waypoints, coord)

initial: coord = (1.9 - constants.drivetrain_length_with_bumpers/2, constants.FieldPos.MidLine.note_init, math.radians(-180))

get_first_note: path = (
    initial,
    [],
    Field.POI.Coordinates.Notes.MidLine.kFarRight.withOffset(Translation2d((-2 * constants.drivetrain_length / 3), 0))
)
