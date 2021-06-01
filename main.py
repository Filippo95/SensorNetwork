# Progetto Ricerca Operativa - n.46 "Sensor Network"
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import random as rn
import math
from matplotlib import pyplot as plt
import pprint

max_x = 1200  # longitudine massima
max_y = 800  # latitudine minima

rn.seed(1625)  # Per la riproducibilità degli esempi

# definisco la classe di sensori
class Sensor:
    def __init__(self, an_id):
        self.id = an_id
        self.longitudine = rn.uniform(0, max_x)
        self.latitudine = rn.uniform(0, max_y)
        self.portata = rn.uniform(50, 150)
        self.send_rate = rn.randint(1, 10)
        self.send_rate_unit = "msg/s"

# definisco la classe di gateway
class Gateway:
    def __init__(self, an_id, costo, capacita):
        self.id = an_id  # ID o "classe" del dispositivo
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
# !!!!!!! Forse conviene tenere il fatto di essere in range di sè stessi,
# visto che comunque prima o poi dovremo considerare la capacità anche
# del sensore stesso, se installiamo un dispositivo presso di lui.
# Vale anche nel caso in cui non ci sia nessun sender che gli manda dati !!!!!!!
# Per ora ho tolto questo check, poi vedremo eventualmente se rimetterlo
def find_senders(a_sensor):
    global sensors
    senders = []

    for this_sens in sensors:
        this_dist = distance(a_sensor, this_sens)
        if this_dist <= this_sens.portata:
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


# Data una capacità da "coprire", trova il
# dispositivo/gateway con costo minore possibile
# che la copra interamente
def find_best_gateway(capacita):
    global gateways
    for gw in gateways:
        if gw.capacita < capacita:
            pass
        else:
            return gw

#array di sensori
sensors = []

#array di gateway
gateways = []


#----MAIN
if __name__ == '__main__':
    # -----------------------------------
    # DEFINIZIONE DATI
    # -----------------------------------
    num_sensori = 50
    color_map_name = "viridis"
    verbose = len(sys.argv) > 1 and "-v" in sys.argv
    quiet = len(sys.argv) > 1 and "-q" in sys.argv

    for i in range(num_sensori):
        sensors.append(Sensor(i))

    # Definiamo il listino dei dispositivi, ordinato
    # secondo le loro capacità massime
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
    # -----------------------------------
    # ANALISI
    # -----------------------------------
    # print("Mostra i sender per tutti i sensori")
    # sens_dict = {}
    # for this_sens in sensors:
    #     this_senders = find_senders(this_sens)
    #     num_sensori = len(this_senders)
    #     sens_dict[this_sens.id] = num_sensori
    #     print("\nIl sensore " + str(this_sens.id) + " è nel raggio di " + str(num_sensori) + " altri sensori:")
    #     for temp_sens in this_senders:
    #         print(temp_sens.id)
    # print(sens_dict)
    #
    # sensors_one = sensors.copy()
    # sens_dict_by_senders = {k: v for k, v in sorted(sens_dict.items(), key=lambda item: item[1], reverse=True)}
    # print("Dizionario dei sensori, in ordine per numero di sender")
    # print(sens_dict_by_senders)

    # Greedy che seleziona per primi i siti in cui
    # il rapporto capacità/costo è massimo
    # TODO: Leggere il commento sottostante e implementare il ricalcolo del rapporto capacità/costo
    # ATTENZIONE!!!!!!!!!!!!!!!!! In questa versione non c'è
    # alcun tipo di riaggiornamento del rapporto capacità/costo dopo aver
    # selezionato un sito dove installare un dispositivo. Invece, ogni volta
    # che decido di installare un dispositivo, dovrei rimuovere i sensori
    # dall'insieme di quelli ancora scoperti e andarmi a ricalcolare il
    # rapporto capacità/costo con tutti quelli rimasti.
    # Inoltre questo mi permetterà di evitare ciò che succede ora, cioè che
    # installo sempre un dispositivo presso ogni sensore disponibile (non
    # avverrà più quando rimuovo i sensori dopo aver installato un dispositivo
    # e quindi avendoli "coperti")

    sens_dictionary = {}
    for this_sens in sensors:
        this_senders = find_senders(this_sens)
        tot_capacita = 0
        num_sensori = len(this_senders)
        for temp_sens in this_senders:
            tot_capacita += temp_sens.send_rate
        rapp_cap_costo = tot_capacita/find_best_gateway(tot_capacita).costo
        rapp_numsensori_costo = num_sensori/find_best_gateway(tot_capacita).costo
        sens_dictionary[this_sens] = {"senders": this_senders,
                                      "tot_capacita": tot_capacita,
                                      "rapp_cap_costo": rapp_cap_costo,
                                      "rapp_numsensori_costo": rapp_numsensori_costo}
        print("\nIl sensore " + str(this_sens.id) + " è nel raggio di " + str(num_sensori) + " sensori," +
              " che hanno una capacità totale di " + str(tot_capacita) + " " + this_sens.send_rate_unit)

    # Stampa il dizionario appena creato
    # pp = pprint.PrettyPrinter(indent=5)
    # pp.pprint(sens_dictionary)

    # Ordino secondo il miglior rapporto capacità/costo e stampo
    sens_dict_ord_by_cap = {k: v for k, v in sorted(sens_dictionary.items(),
                                                    key=lambda item: item[1]["rapp_cap_costo"],
                                                    reverse=True)}
    # Ordino secondo il miglior rapporto numsensori coperti/costo
    sens_dict_ord_by_numsensori = {k: v for k, v in sorted(sens_dictionary.items(),
                                                    key=lambda item: item[1]["rapp_numsensori_costo"],
                                                    reverse=True)}

    print("\n\n\n")
    for temp_sens in sens_dict_ord_by_cap.keys():
        print("\nSensore " + str(temp_sens.id) + ":")
        temp_val = sens_dict_ord_by_cap[temp_sens]
        temp_sens_list = temp_val["senders"]
        temp_tot_cap = temp_val["tot_capacita"]
        temp_rapp_cap_costo = temp_val["rapp_cap_costo"]
        print("Senders: ", end='')
        for temp_sender in temp_sens_list:
            print(str(temp_sender.id) + " ", end='')
        print("\nTot_capacità: " + str(temp_tot_cap))
        print("Rapporto capacità/costo: " + str(temp_rapp_cap_costo))

    # Seleziono per primi i siti in cui ho rapporto capacità/costo maggiore
    selected = {}
    sensors_copy = sensors.copy()
    costo_totale = 0
    i = 0
    for temp_sens in sens_dict_ord_by_cap.keys():
        where = temp_sens
        temp_val = sens_dict_ord_by_cap[temp_sens]
        which_covered = temp_val["senders"]
        which_gateway = find_best_gateway(temp_val["tot_capacita"])
        selected[i] = {
            "location": {
                "sensor_id": temp_sens.id,
                "latitudine": temp_sens.latitudine,
                "longitudine": temp_sens.longitudine
            },
            "selected_gateway": {
                "classe": which_gateway.id,
                "costo": which_gateway.costo
            }
        }
        costo_totale += which_gateway.costo
        i += 1
        # Rimuovo da una copia dell'array dei sensori i sensori che ho
        # coperto con questa iterazione
        for a_sensor in which_covered:
            if a_sensor in sensors_copy:
                sensors_copy.remove(a_sensor)

    # Stampo il dizionario che mostra dove e quali dispositivi ho installato
    print("\n\n\n")
    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(selected)

    if len(sensors_copy) == 0:
        print("Non sono rimasti sensori da coprire. Il costo della soluzione è "+str(costo_totale))
    else:
        print("Sono rimasti sensori da coprire. Nessuna soluzione ammissibile trovata!")

    ax.set_aspect('equal', anchor="C")
    ax.set_xbound(lower=0.0, upper=max_x)
    ax.set_ybound(lower=0.0, upper=max_y)
    plt.grid()
    plt.show()


