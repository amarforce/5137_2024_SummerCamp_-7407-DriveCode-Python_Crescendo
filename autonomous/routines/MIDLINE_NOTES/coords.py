from units.SI import meters, radians
from robot_systems import Field
from utils import POIPose
from wpimath.geometry import Translation2d
# from constants.FieldPos import MidLine
from constants import field_width, FieldPos, drivetrain_length_with_bumpers
import math
from typing import Tuple

coord = Tuple[meters, meters, radians]
waypoints = Tuple[meters, meters]
path = Tuple[coord, waypoints, coord]

initial: coord = (1.9 - drivetrain_length_with_bumpers/2, field_width-5.373, math.pi)

get_first_ring: path = ( 
    initial,
    [],
    Field.POI.Coordinates.Notes.MidLine.kFarRight,
)

come_back_to_shoot_first_ring: path = (
    get_first_ring[2],
    [],
    Field.POI.Coordinates.Notes.MidLine.kFarRight.withOffset(Translation2d(-4.3, -.7)),
)

get_second_ring: path = (
    come_back_to_shoot_first_ring[2],
    [],
    Field.POI.Coordinates.Notes.MidLine.kMidRight,
)

come_back_to_shoot_second_ring: path = (
    get_second_ring[2],
    [],
    Field.POI.Coordinates.Notes.MidLine.kFarRight.withOffset(Translation2d(-4.3, -.7)),
)

get_third_ring: path = (
    come_back_to_shoot_second_ring[2],
    [],
    Field.POI.Coordinates.Notes.MidLine.kCenter,
)

come_back_to_shoot_third_ring: path = (
    get_third_ring[2],
    [(FieldPos.Stage.stage_x, FieldPos.Stage.stage_y)],
    Field.POI.Coordinates.Notes.MidLine.kCenter.withOffset(Translation2d(-4.5, -1.2)),
)