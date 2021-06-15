from math import sin, cos, sqrt, atan2, radians
from deprecated import deprecated


# classe di supporto per controllare la quanità
# di output stampato a video
class Verbosity:
    def __init__(self, quiet, verbose, more_verbose):
        self.quiet = quiet
        self.verbose = verbose or more_verbose       # se ho output more_verbose voglio che si stampi anche il verbose
        self.more_verbose = more_verbose


# Inutilizzato.
# Creato in origine per calcolare la distanza in 2D, ora si usa
# un metodo più preciso che tiene conto della curvatura terrestre.
@deprecated(reason="Utilizzare il metodo distance(), che tiene conto della curvatura terrestre")
def distance_in_2d(sens_one, sens_two):
    x_0 = sens_one.longitudine
    y_0 = sens_one.latitudine
    x_1 = sens_two.longitudine
    y_1 = sens_two.latitudine
    return sqrt((y_0 - y_1) ** 2 + (x_0 - x_1) ** 2)


def find_sensor_by_id(sensor):
    for sen in get_global_sensors():
        if sen.id == sensor:
            return sen
    return None


# Prende in input due tuple di coordinate e restituisce la loro distanza sulla superficie terrestre
def distance_by_coord(node_one, node_two):
    # Approssimazione del raggio della Terra in Km
    raggio_terra = 6373.0

    lat1 = radians(node_one[0])
    lon1 = radians(node_one[1])
    lat2 = radians(node_two[0])
    lon2 = radians(node_two[1])

    diff_lon = lon2 - lon1
    diff_lat = lat2 - lat1

    a = sin(diff_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(diff_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distanza = raggio_terra * c * 1000
    return distanza


# Prende in input due sensori e restituisce
# la loro distanza sulla superficie terrestre
def distance(sens_one, sens_two):
    return distance_by_coord((sens_one.latitudine, sens_one.longitudine),
                             (sens_two.latitudine, sens_two.longitudine))


def print_scenario(a_dict):
    for temp_sens in a_dict.keys():
        print("\nSensore " + str(temp_sens.id) + ":")
        temp_val = a_dict[temp_sens]
        temp_sens_list = temp_val["senders"]
        temp_tot_cap = temp_val["tot_capacita"]
        temp_rapp_cap_costo = temp_val["rapp_cap_costo"]
        temp_rapp_numsensori_costo = temp_val["rapp_numsensori_costo"]
        print("Senders: ", end='')
        for temp_sender in temp_sens_list:
            print(str(temp_sender.id) + " ", end='')
        print("\nTot_capacità: " + str(temp_tot_cap))
        print("Rapporto capacità/costo: " + str(temp_rapp_cap_costo))
        print("Rapporto numsensori/costo: " + str(temp_rapp_numsensori_costo))
    print("\n\n")


verbosity = Verbosity(False, False, False)


def get_verbosity():
    return verbosity


def set_verbosity(quiet=False, verbose=False, more_verbose=False):
    global verbosity
    verbosity = Verbosity(quiet, verbose, more_verbose)


random_seed = 12345  # Per la riproducibilità degli esempi
# Il seed originale è 1625


def get_seed():
    return random_seed


def set_seed(new_seed):
    global random_seed
    random_seed = new_seed


gateway_classes = []


def get_gateways_classes():
    return gateway_classes


def set_gateways_classes(new_gateway_classes):
    global gateway_classes
    gateway_classes = new_gateway_classes


sensors = []


def get_global_sensors():
    return sensors


def set_global_sensors(new_sensors):
    global sensors
    sensors = new_sensors

