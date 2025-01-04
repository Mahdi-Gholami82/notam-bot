from math import atan2

def dms_to_dd(dms):

    direction = dms[-1]
    dms_fx = str(float(dms[:-1]))

    degrees = float(dms_fx[:2])
    minutes = float(dms_fx[2:4])
    seconds = float(dms_fx[4:])

    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)

    if direction in ['W', 'S']:
        return -decimal_degrees
    return decimal_degrees

def calculate_center(coords):
    x, y = zip(*coords)
    center_x = sum(x) / len(coords)
    center_y = sum(y) / len(coords)
    return center_x, center_y

def calculate_angle(point, center):
    angle = atan2(point[1] - center[1], point[0] - center[0])
    return angle

def sort_coordinates(coords):
    center = calculate_center(coords)
    return sorted(coords, key=lambda point: calculate_angle(point, center))
