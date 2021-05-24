# Progetto Ricerca Operativa
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import random as rn
from matplotlib import pyplot as plt


class Sensor:
    def __init__(self, an_id):
        self.id = an_id
        self.latitudine = rn.uniform(0, 800)
        self.longitudine = rn.uniform(0, 1000)
        self.portata = rn.uniform(50, 100)
        self.send_rate = rn.randint(1, 10)
        self.send_rate_unit = "msg/s"


class Gateway:
    def __init__(self, an_id):
        self.id = an_id
        self.latitudine = 0
        self.longitudine = 0
        self.costo = rn.randint(100, 1000)
        self.capacita = rn.randint(50, 1000)
        self.capacita_elab_unit = "msg/s"


# class Progetto:
#    def __init__(self, num_sensori):
#        self.num_sensori = num_sensori


if __name__ == '__main__':
    num_sensori = 50

    sensors = []
    gateways = []
    for i in range(num_sensori):
        sensors.append(Sensor(i))

    x = []
    y = []
    areas = []
    colors = []
    labels = []


    # FONDAMENTALE: La dimensione dei cerchi NON è quella giusta!!!
    # Dobbiamo trovare un modo di plottare accuratamente le portate dei sensori
    for i in range(len(sensors)):
        x.append(sensors[i].longitudine)
        y.append(sensors[i].latitudine)

        radius = sensors[i].portata
        areas.append(radius ** 2)

        colors.append(sensors[i].id)
        labels.append("id={} r={}".format(sensors[i].id, round(sensors[i].portata)))

    plt.scatter(x, y, s=areas, c=colors, cmap="viridis", marker="o", alpha=0.5)

    for x_pos, y_pos, label in zip(x, y, labels):
        plt.annotate(label,  # The label for this point
                     xy=(x_pos, y_pos),  # Position of the corresponding point
                     xytext=(7, 0),  # Offset text by 7 points to the right
                     textcoords='offset points',  # tell it to use offset points
                     ha='left',  # Horizontally aligned to the left
                     va='center')  # Vertical alignment is centered

    plt.grid()
    plt.show()
