from math import sin, cos, sqrt, atan2, radians
from deprecated import deprecated


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
