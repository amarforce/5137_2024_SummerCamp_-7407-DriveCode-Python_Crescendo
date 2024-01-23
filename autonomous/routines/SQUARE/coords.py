from units.SI import meters, radians

coord = (meters, meters, radians)
waypoints = [(meters, meters)]
path = (coord, waypoints, coord)

blue_team = True

initial: coord = (0, 0, 0)

drive_forward: path = (
    initial,
    [],
    (initial[0] + 1, initial[1], 0),
)

drive_left: path = (
    drive_forward[2],
    [],
    (initial[0] + 1, initial[1] + 1, 0)
)

drive_back: path = (
    drive_left[2],
    [],
    (initial[0], initial[1] + 1, 0)
)

drive_right: path = (
    drive_back[2],
    [],
    (initial[0], initial[1], 0)
)
