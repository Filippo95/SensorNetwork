# Progetto Ricerca Operativa - n.46 "Sensor Network"
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import random as rn
import math
from matplotlib import pyplot as plt

max_x = 1200  # longitudine
max_y = 800  # latitudine

rn.seed(1625)  # Per la riproducibilità degli esempi


class Sensor:
    def __init__(self, an_id):
        self.id = an_id
        self.longitudine = rn.uniform(0, max_x)
        self.latitudine = rn.uniform(0, max_y)
        self.portata = rn.uniform(50, 150)
        self.send_rate = rn.randint(1, 10)
        self.send_rate_unit = "msg/s"


class Gateway:
    def __init__(self, an_id, costo, capacita):
        self.id = an_id
        self.longitudine = 0
        self.latitudine = 0
        self.costo = costo
        self.capacita = capacita
        self.capacita_elab_unit = "msg/s"


# class Progetto:
#    def __init__(self, num_sensori):
#        self.num_sensori = num_sensori

# Questa funzione, dato un sensore in input, trova tutti i sensori
# che possono trasmettergli dati.
def find_senders(a_sensor):
    global sensors
    sensors_without_self = sensors.copy()
    # sensors_without_self.remove(a_sensor)
    senders = []

    for this_sens in sensors:
        this_dist = distance(a_sensor, this_sens)
        if this_dist <= this_sens.portata and this_dist != 0:
            senders.append(this_sens)

    return senders


# Prende in input due sensori e restituisce
# la loro distanza euclidea
def distance(sens_one, sens_two):
    x_0 = sens_one.longitudine
    y_0 = sens_one.latitudine
    x_1 = sens_two.longitudine
    y_1 = sens_two.latitudine
    return math.sqrt((y_0 - y_1) ** 2 + (x_0 - x_1) ** 2)


sensors = []
gateways = []

if __name__ == '__main__':
    num_sensori = 50
    color_map_name = "viridis"
    verbose = len(sys.argv) > 1 and "-v" in sys.argv
    quiet = len(sys.argv) > 1 and "-q" in sys.argv

    for i in range(num_sensori):
        sensors.append(Sensor(i))

    # Definiamo il listino dei dispositivi
    gateways.append(Gateway(1, 8, 8))
    gateways.append(Gateway(2, 16, 16))
    gateways.append(Gateway(3, 24, 24))
    gateways.append(Gateway(4, 32, 32))
    gateways.append(Gateway(5, 40, 40))

    x = []
    y = []
    colors = []
    labels = []

    ax = plt.axes(xlim=(0, max_x), ylim=(0, max_y))
    for i in range(len(sensors)):
        x.append(sensors[i].longitudine)
        y.append(sensors[i].latitudine)

        radius = sensors[i].portata

        colors.append(sensors[i].id)

        if verbose:
            center = "center: x={} y={}".format(round(sensors[i].longitudine), round(sensors[i].latitudine))
            coords = "range: x={}-{} | y={}-{}".format(round(sensors[i].longitudine - radius),
                                                       round(sensors[i].longitudine + radius),
                                                       round(sensors[i].latitudine - radius),
                                                       round(sensors[i].latitudine + radius))
            labels.append("id={} r={}\n{}\n{}".format(sensors[i].id, round(radius), center, coords))
        elif quiet:
            labels.append("{}".format(sensors[i].id))
        else:
            labels.append("id:{} r={}".format(sensors[i].id, round(radius)))

        ax.add_artist(plt.Circle((sensors[i].longitudine, sensors[i].latitudine), radius,
                                 color=plt.cm.get_cmap(color_map_name).colors[i * round(256 / num_sensori)],
                                 fill=True, alpha=0.5))  # Disegna i "raggi" dei sensori

    ax.scatter(x, y, c=colors, s=5, cmap=color_map_name, alpha=1.0)  # Disegna i "centri" dei sensori

    for x_pos, y_pos, label in zip(x, y, labels):
        ax.annotate(label, xy=(x_pos, y_pos), xytext=(7, 0), textcoords='offset points',
                    ha='left', va='center')

    print("Mostra i sender per tutti i sensori")
    sens_dict = {}
    for this_sens in sensors:
        this_senders = find_senders(this_sens)
        num_sensori = len(this_senders)
        sens_dict[this_sens.id] = num_sensori
        print("\nIl sensore " + str(this_sens.id) + " è nel raggio di " + str(num_sensori) + " altri sensori:")
        for temp_sens in this_senders:
            print(temp_sens.id)

    print(sens_dict)

    ax.set_aspect('equal', anchor="C")
    ax.set_xbound(lower=0.0, upper=max_x)
    ax.set_ybound(lower=0.0, upper=max_y)
    plt.grid()
    plt.show()
