import math
from unittest.mock import MagicMock, Mock

import pytest

# import config
# import constants
from sensors.trajectory_calc import TrajectoryCalculator

# from pytest import MonkeyPatch


@pytest.fixture
def trajectory_calc():
    field_od = MagicMock()
    # drivetrain = MagicMock()
    elevator = MagicMock()
    trajectory_calc = TrajectoryCalculator(field_od, elevator)
    trajectory_calc.odometry = MagicMock()
    # distance to speaker (m)
    trajectory_calc.odometry.getPose.return_value.translation.return_value.distance.return_value = (
        5
    )
    # current height of elevator (m)
    trajectory_calc.elevator.get_height.return_value = 0.5
    return trajectory_calc


@pytest.mark.parametrize(
    "distance_to_target, delta_z, expected_angle",
    [(5, 0.7, 0.25064), (5, 0.5, 0.21069), (3, 0.8, 0.32732), (3, 0.4, 0.19866)],
)
def test_update(
    trajectory_calc, distance_to_target, delta_z, expected_angle
):
    trajectory_calc.delta_z = delta_z
    trajectory_calc.distance_to_target = distance_to_target
    assert trajectory_calc.calculate_angle_no_air(
        distance_to_target, delta_z
    ) == pytest.approx(expected_angle, 0.0001)


@pytest.mark.parametrize(
    "angle, x_distance, expected_answer",
    [
        (0.3, 5.88, 0.9114040891170673),
        (0.56, 6.53, 2.6401846942215146),
        (0.9, 7.8, 5.730080943722868),
        (0.52, 2.1, 1.0700338538709877),
    ],
)
def test_run_sim(trajectory_calc, angle, x_distance, expected_answer):
    config = Mock()
    constants = Mock()

    config.v0_flywheel = 15
    constants.g = 9.8
    constants.c = 0.47
    constants.rho_air = 1.28
    constants.a = 14 * 0.0254 * 2 * 0.0254
    constants.m = 0.235301
    constants.speaker_z = 1.7

    trajectory_calc.distance_to_target = x_distance
    # trajectory_calc.print_constants()
    ans = trajectory_calc.run_sim(angle)
    assert ans == pytest.approx(expected_answer, 0.01)


@pytest.mark.parametrize(
    "x_distance, y_distance, expected_answer",
    [
        (1.15, 1.35, 0.8918247212271702),
        (5.27, 1.63, 0.4323481479683407),
        (6.11, 1.67, 0.4234831594121902),
        (4.86, 1.71, 0.45967112158043777),
    ],
)
def test_calculate_angle_air(trajectory_calc, x_distance, y_distance, expected_answer):
    config = Mock()
    constants = Mock()

    config.v0_flywheel = 15
    constants.g = 9.8
    constants.c = 0.47
    constants.rho_air = 1.28
    constants.a = 14 * 0.0254 * 2 * 0.0254
    constants.m = 0.235301
    constants.speaker_z = 1.7
    trajectory_calc.distance_to_target = x_distance
    trajectory_calc.delta_z = y_distance
    angle = trajectory_calc.calculate_angle_air()
    assert angle == pytest.approx(expected_answer, math.radians(2))