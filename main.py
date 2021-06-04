# Progetto Ricerca Operativa - n.46 "Sensor Network"
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import random as rn
import math
from matplotlib import pyplot as plt
import pprint

random_seed = 12345  # Per la riproducibilità degli esempi
# Il seed originale è 1625

max_x = 1200  # longitudine massima
max_y = 800  # latitudine minima

rn.seed(random_seed)


# definisco la classe di sensori
class Sensor:
    def __init__(self, an_id):
        self.id = an_id
        self.longitudine = rn.uniform(0, max_x)
        self.latitudine = rn.uniform(0, max_y)
        self.portata = rn.uniform(50, 150)#distaza raggio di copertura
        self.send_rate = rn.randint(1, 10)# quanti msg
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

    return gateways[-1]








# array di sensori
sensors = []

# array di gateway
gateways = []


# Questa funzione dato l'array di sensori calcola un dizionario ordinato per il parametro order_by.
def calcola_scenario(order_by="rapp_cap_costo", sensor_list=None):
    global sensors
    if sensor_list is None:
        sensor_list = sensors
    sens_dictionary = {}
    for this_sens in sensor_list:
        this_senders = find_senders(this_sens)
        tot_capacita = 0
        num_sensori = len(this_senders)
        for temp_sens in this_senders:
            tot_capacita += temp_sens.send_rate
        rapp_cap_costo = tot_capacita / find_best_gateway(tot_capacita).costo
        rapp_numsensori_costo = num_sensori / find_best_gateway(tot_capacita).costo
        sens_dictionary[this_sens] = {"senders": this_senders,
                                      "tot_capacita": tot_capacita,
                                      "rapp_cap_costo": rapp_cap_costo,
                                      "rapp_numsensori_costo": rapp_numsensori_costo}
        if verbose:
            print("\nIl sensore " + str(this_sens.id) + " è nel raggio di " + str(num_sensori) + " sensori," +
                  " che hanno una capacità totale di " + str(tot_capacita) + " " + this_sens.send_rate_unit)

    return {k: v for k, v in sorted(sens_dictionary.items(),
                                    key=lambda item: item[1][order_by],
                                    reverse=True)}


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


def find_covered(sensor,capacita_to_cover, senders, capacita_gateway, find_by="distanza_capacita"):
    selected = []

    for sender in senders:

        if find_by == "capacita":
            sender.criterio = sender.send_rate
        else :
            distanza = distance(sensor, sender)
            if distanza == 0:
                distanza = 0.0001
            sender.criterio = sender.send_rate / distanza  # vogliamo prioritizzare i sensori che hanno raggio molto piccolo e capacità molto grande quindi tra quelli più vicini con send_rate più grande

    senders = sorted(senders,
                                    key=lambda item: item.criterio,
                                    reverse=True)#in ordine decrescente
    capacita_coperta=0

    while len(senders) > 0:
        #prendo il primo elemento di senders ordinato per il criterio e controllo che ci stia
        if senders[0].send_rate+capacita_coperta <= capacita_gateway:
            capacita_coperta += senders[0].send_rate #aggiungo all'accumulatore
            selected.append(senders[0]) #aggiungo ai coperti
        senders.remove(senders[0]) #elimino dai possibili coperti


    return selected


def greedy_optimization(sensors, sens_dict_ordered, pack_by="distanza_capacita"):
    # Seleziono per primi i siti in cui ho rapporto capacità/costo maggiore
    # (o rapporto numsensori/costo maggiore)
    selected = {}
    sensors_copy = sensors.copy()
    costo_totale = 0
    i = 0
    while len(sens_dict_ordered) > 0:
        (where, temp_val) = list(sens_dict_ordered.items())[0]

        which_gateway = find_best_gateway(temp_val["tot_capacita"])

        if temp_val["tot_capacita"]>which_gateway.capacita:
            which_covered = find_covered(where,temp_val["tot_capacita"],temp_val["senders"],which_gateway.capacita,pack_by)
        else:
            which_covered = temp_val["senders"]

        # creo una array per la stampa dei sensori coperti
        arr=[]
        for sensor in which_covered:
            arr.append(sensor.id)

        selected[i] = {
            "gateway": {
                "sensor_id": where.id,
                "latitudine": where.latitudine,
                "longitudine": where.longitudine,

                "classe": which_gateway.id,
                "costo": which_gateway.costo,
                "sensor_covered": arr

            }
        }
        costo_totale += which_gateway.costo
        i += 1
        # Rimuovo da una copia dell'array dei sensori i sensori che ho
        # coperto con questa iterazione
        for a_sensor in which_covered:
            if a_sensor in sensors_copy:
                sensors_copy.remove(a_sensor)
        print("\n ITERAZIONE: " + str(i - 1))
        for temp in sensors_copy:
            print(temp.id, end=',')
        print("\n")

        # aggiorno lo scenario dopo l'assegnazione, e dopo aver rimosso quelli già assegnati
        sens_dict_ordered = calcola_scenario(sensor_list=sensors_copy)

    # Stampo il dizionario che mostra dove e quali dispositivi ho installato
    print("\n\n\n")
    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(selected)

    with open('greedy_output.txt', 'a') as f:
        original_stdout = sys.stdout
        if len(sensors_copy) == 0:
            print("Non sono rimasti sensori da coprire. Il costo della soluzione è " + str(costo_totale))
            sys.stdout = f
            print("SEED: " + str(random_seed))
            print("Non sono rimasti sensori da coprire. Il costo della soluzione è " + str(costo_totale))
            print("\n")
            sys.stdout = original_stdout
        else:
            sys.stdout = f
            print("SEED: " + str(random_seed))
            print("Sono rimasti sensori da coprire. Nessuna soluzione ammissibile trovata!")
            print("\n")
            sys.stdout = original_stdout
    return selected


def distance_by_coord(sorgente, destinazione):
    return math.sqrt((sorgente[0]-destinazione[0])**2+(sorgente[1]-destinazione[1])**2)

#TODO implementare la funzione di visita in profondità
def ha_cicli(selected):
    #faccio una riceerca in profondità
    visited = []
    for arco in selected:
        if arco["source"] in visited:
            return True
        else:
            visited.append(arco["source"])
            ha_cicli(selected.pop())

#TODO metodo che ritorna true o false
# True se esiste un arco in edges che va da destinationa soruce
# False se non esiste un arco in edges che va da destination a source
def esiste_reverse(edges, source, destination):
    return True


def minimum_spanning_tree(result):
    vertices = []#i nodi del grafo
    edges = []#gli archi del grafo

    for gateway in result:
        vertices.append(gateway)
        temp_result=result.copy() # creo una copia deel dizionario in modo da poi eliminare l'elemeento attuale
        temp_result.pop(gateway)
        for node in temp_result:
            if not(esiste_reverse(edges, gateway,node)):
                edges.append({
                    "source": gateway,
                    "destination": node,
                    "costo": distance_by_coord((result.get(gateway)['latitudine'],result.get(gateway)['longitudine']),
                                               (result.get(node)['latitudine'],result.get(node)['longitudine'])) * rn.uniform(0.5, 1.5)
                })

    #kruskal
    #ordino gli archi per costo
    edges = {k: v for k, v in sorted(edges.items(),
                             key=lambda item: item[1]["costo"],
                             reverse=False)}# dal più basso al più alto

    # creo un arrray che contiene gli archi che ho selezionato
    selected=[]
    i=0
    while len(edges)>0 and len(selected)<len(vertices)-1:
        #aggiungo l'arco alla soluzione
        selected.append(edges[0])
        # passo la la suole (il grafo ) alla funzione ch econtrolla se ha cicli
        if ha_cicli(selected):
            # ha cicli quindi lo rimuovo
            selected.pop(-1)







# ----MAIN
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
    # ANALISI (???)
    # -----------------------------------

    # calcola l'insieme dei sensori con le relative proprietà
    sens_dict_ord_by_cap = calcola_scenario()
    sens_dict_ord_by_num_sensori = calcola_scenario(order_by="rapp_numsensori_costo")
    if verbose:
        print("SCENARIO - CAPACITA'/COSTO: ")
        print_scenario(sens_dict_ord_by_cap)
        print("\n\n\n\n\n---------------------------------------------------\n\n\n\n\n")
        print("SCENARIO - NUM_SENSORI/COSTO: ")
        print_scenario(sens_dict_ord_by_num_sensori)

    result=greedy_optimization(sensors, sens_dict_ord_by_cap)
    greedy_optimization(sensors, sens_dict_ord_by_num_sensori)

    greedy_optimization(sensors, sens_dict_ord_by_cap, pack_by="capacita")
    greedy_optimization(sensors, sens_dict_ord_by_num_sensori, pack_by="capacita")

    minimum_spanning_tree(result)

    ax.set_aspect('equal', anchor="C")
    ax.set_xbound(lower=0.0, upper=max_x)
    ax.set_ybound(lower=0.0, upper=max_y)
    plt.grid()
    plt.show()
