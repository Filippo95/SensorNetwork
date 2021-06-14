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


# TODO: Inserire questo vincolo nel modello matematico!!!
def only_one_gw_per_site(solution):
    for key, a_gateway in solution.items():
        temp_solution = solution.copy()
        temp_solution.pop(key)
        for another_gateway in temp_solution.values():
            if a_gateway["sensor_id"] == another_gateway["sensor_id"]:
                return False
    return True


def controlla_ammisibilita(solution, sensor_list):
    if not tutti_sensori_coperti(solution, sensor_list):
        return False, "Non tutti i sensori sono stati coperti!"
    if not gateway_capacity(solution, sensor_list):
        return False, "Alcuni gateway coprono capacità superiori al loro massimo!"
    if not single_demand(solution):
        return False, "Alcuni sensori sono coperti da più gateway!"
    if not only_one_gw_per_site(solution):
        return False, "Più gateway sono installati nello stesso sito!"
    return True, "OK"
