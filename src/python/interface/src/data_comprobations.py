def check_sex(sex):
    if (sex == 'M'):
        return True
    elif (sex == 'F'):
        return True
    elif (sex == 'Unknown'):
        return True
    else:
        return False


def check_coordinates(points):
    if points[0] < 0 or points[1] < 0:
        return False
    else :
        return True