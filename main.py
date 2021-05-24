# Progetto Ricerca Operativa - n.46 "Sensor Network"
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import random as rn
from matplotlib import pyplot as plt

max_x = 1200  # longitudine
max_y = 800  # latitudine


class Sensor:
    def __init__(self, an_id):
        self.id = an_id
        self.longitudine = rn.uniform(0, max_x)
        self.latitudine = rn.uniform(0, max_y)
        self.portata = rn.uniform(50, 150)
        self.send_rate = rn.randint(1, 10)
        self.send_rate_unit = "msg/s"


class Gateway:
    def __init__(self, an_id):
        self.id = an_id
        self.longitudine = 0
        self.latitudine = 0
        self.costo = rn.randint(100, 1000)
        self.capacita = rn.randint(50, 1000)
        self.capacita_elab_unit = "msg/s"


# class Progetto:
#    def __init__(self, num_sensori):
#        self.num_sensori = num_sensori


if __name__ == '__main__':
    num_sensori = 50
    color_map_name = "viridis"
    verbose = len(sys.argv) > 1 and "-v" in sys.argv
    quiet = len(sys.argv) > 1 and "-q" in sys.argv

    sensors = []
    gateways = []
    for i in range(num_sensori):
        sensors.append(Sensor(i))

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

    ax.set_aspect('equal', anchor="C")
    ax.set_xbound(lower=0.0, upper=max_x)
    ax.set_ybound(lower=0.0, upper=max_y)
    plt.grid()
    plt.show()
