from display_functions import find_sensor_by_id


def tutti_sensori_coperti(solution, sensor_list):
    sensors_copy = sensor_list.copy()
    for a_gateway in solution.values():
        for covered in a_gateway["sensor_covered"]:
            for a_sensor in sensors_copy:
                if covered == a_sensor.id:
                    sensors_copy.remove(a_sensor)

    return len(sensors_copy) == 0


def gateway_capacity(solution, sensor_list):
    for a_gateway in solution.values():
        temp_capacita = 0
        for a_sensor in a_gateway["sensor_covered"]:
            temp_capacita += find_sensor_by_id(a_sensor, sensor_list).send_rate
        if a_gateway["max_capacity"] < temp_capacita:
            return False
    return True


def single_demand(solution):
    covered_sensors = []
    for a_gateway in solution.values():
        for covered in a_gateway["sensor_covered"]:
            if covered in covered_sensors:
                return False
            else:
                covered_sensors.append(covered)
    return True


def controlla_ammisibilita(solution, sensor_list):
    return tutti_sensori_coperti(solution, sensor_list) and \
            gateway_capacity(solution, sensor_list) and \
            single_demand(solution)
