# Progetto Ricerca Operativa - n.46 "Sensor Network" - A.A. 2020-21
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import random as rn
from math import sin, cos, sqrt, atan2, radians
from matplotlib import pyplot as plt
import folium
import pprint
from deprecated import deprecated

random_seed = 1625  # Per la riproducibilità degli esempi
# Il seed originale è 1625

max_x = 12  # longitudine massima est
min_x = 11  # ovest
max_y = 45  # latitudine minima nord
min_y = 44  # sud

rn.seed(random_seed)


# definisco la classe di sensori
class Sensor:
    def __init__(self, an_id):
        self.id = an_id
        self.longitudine = rn.uniform(min_x, max_x)
        self.latitudine = rn.uniform(min_y, max_y)
        self.portata = rn.uniform(5000, 15000)  # distanza raggio di copertura
        self.send_rate = rn.randint(1, 10)  # quanti msg
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
# Viene considerato anche il sensore stesso.
def find_senders(a_sensor, sensor_list=None):
    global sensors
    if sensor_list is None:
        sensor_list = sensors
    senders = []

    for this_sens in sensor_list:
        this_dist = distance(a_sensor, this_sens)
        if this_dist <= this_sens.portata:
            senders.append(this_sens)

    return senders


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


# Data una capacità da "coprire", trova il
# dispositivo/gateway con costo minore possibile
# che la copra interamente, oppure, se non ne
# esiste uno che possa farlo, restituisce il
# dispositivo con capacità massima
def find_best_gateway(capacita):
    global gateways
    for gw in gateways:
        if gw.capacita < capacita:
            pass
        else:
            return gw

    return gateways[-1]


# -----------------------------------
# VARIABILI GLOBALI
# -----------------------------------

# array di sensori
sensors = []

# array di gateway
gateways = []


# Questa funzione, dato l'array di sensori, crea un dizionario ordinato secondo il parametro order_by.
def calcola_scenario(order_by="rapp_cap_costo", sensor_list=None):
    global sensors
    if sensor_list is None:
        sensor_list = sensors
    sens_dictionary = {}
    for this_sens in sensor_list:
        this_senders = find_senders(this_sens, sensor_list)
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
        if more_verbose:
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


def find_covered(sensor, capacita_to_cover, senders, capacita_gateway, find_by="distanza_capacita"):
    selected = []

    for sender in senders:
        if find_by == "capacita":
            sender.criterio = sender.send_rate
        else:
            distanza = distance(sensor, sender)
            if distanza == 0:
                distanza = 0.0001
            sender.criterio = sender.send_rate / distanza  # vogliamo prioritizzare i sensori che hanno
            # raggio molto piccolo e capacità molto grande, quindi tra quelli più vicini con send_rate più grande

    senders = sorted(senders,
                     key=lambda item: item.criterio,
                     reverse=True)  # in ordine decrescente

    capacita_coperta = 0

    while len(senders) > 0:
        # prendo il primo elemento di senders ordinato per il criterio e controllo che ci stia
        if senders[0].send_rate + capacita_coperta <= capacita_gateway:
            capacita_coperta += senders[0].send_rate  # aggiungo all'accumulatore
            selected.append(senders[0])  # aggiungo ai coperti
        senders.remove(senders[0])  # elimino dai possibili coperti

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

        if temp_val["tot_capacita"] > which_gateway.capacita:
            which_covered = find_covered(where, temp_val["tot_capacita"], temp_val["senders"], which_gateway.capacita,
                                         pack_by)
        else:
            which_covered = temp_val["senders"]

        # creo una array per la stampa dei sensori coperti
        arr = []
        for sensor in which_covered:
            arr.append(sensor.id)

        selected[i] = {
            "sensor_id": where.id,
            "latitudine": where.latitudine,
            "longitudine": where.longitudine,
            "classe": which_gateway.id,
            "costo": which_gateway.costo,
            "sensor_covered": arr
        }
        costo_totale += which_gateway.costo
        i += 1
        # Rimuovo da una copia dell'array dei sensori i sensori che ho
        # coperto con questa iterazione
        for a_sensor in which_covered:
            if a_sensor in sensors_copy:
                sensors_copy.remove(a_sensor)
        if not quiet:
            print("\nITERAZIONE: " + str(i - 1))
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


def find_reachable_vertices(edge_list, a_vertex):
    reachable_vertices = []
    for edge in edge_list:
        if edge["node_one"] == a_vertex:
            reachable_vertices.append(edge["node_two"])
        elif edge["node_two"] == a_vertex:
            reachable_vertices.append(edge["node_one"])
    return reachable_vertices


def depth_first_visit(edge_list, this_vertex, visited_vertices, parent, opened_vertices, vertices_left):
    visited_vertices.append(this_vertex)
    vertices_left.remove(this_vertex)

    # Trovo i vertici raggiungibili partendo dal vertice attuale
    vertici_raggiungibili = find_reachable_vertices(edge_list, this_vertex)
    # Per ogni vertice raggiungibile, se non è già stato aperto, lo aggiungo in testa
    # alla lista dei vertici aperti
    for a_vertex in vertici_raggiungibili:
        if a_vertex not in opened_vertices:
            opened_vertices.insert(0, a_vertex)

    # Rimuovo il parent per evitare di visitarlo di nuovo
    if parent in opened_vertices:
        opened_vertices.remove(parent)

    # Verifico se fra i vertici raggiungibili c'è uno dei vertici già visitati,
    # senza considerare il vertice dal quale provengo (ossia parent), se ciò è
    # verificato, allora ho trovato un ciclo
    for a_vertex in vertici_raggiungibili:
        if a_vertex in visited_vertices and a_vertex != parent:
            return True
    # Sennò proseguo la visita in profondità.

    # Può darsi che la lista di vertici aperti sia nulla, ad esempio in casi in cui ho
    # selezionato due archi che collegano due coppie di vertici diversi. Quindi devo controllare se
    # la lista dei vertici aperti è vuota, e in quel caso effettuare una nuova visita.
    parent = this_vertex
    if len(opened_vertices) > 0:
        next_vertex = opened_vertices[0]
        opened_vertices.pop(0)
    else:
        # Se sono riuscito a visitare tutti i nodi del grafo, non ho trovato nessun ciclo
        if len(vertices_left) == 0:
            return False
        next_vertex = vertices_left[0]
    return depth_first_visit(edge_list, next_vertex, visited_vertices, parent, opened_vertices, vertices_left)


def ha_cicli(edge_list):
    vertices_to_visit = []
    for an_edge in edge_list:
        n1 = an_edge["node_one"]
        n2 = an_edge["node_two"]
        if n1 not in vertices_to_visit:
            vertices_to_visit.append(n1)
        if n2 not in vertices_to_visit:
            vertices_to_visit.append(n2)

    return depth_first_visit(edge_list, edge_list[0]["node_one"], [], None, [], vertices_to_visit)


def esiste_arco(edges, node_one, node_two):
    for item in edges:
        if (item["node_one"] == node_one and item["node_two"] == node_two) or \
                (item["node_one"] == node_two and item["node_two"] == node_one):
            return True
    return False


def minimum_spanning_tree(result):
    # Costruisco il grafo dei dispositivi, che è un grafo
    # completamente connesso i cui nodi rappresentano i dispositivi
    vertices = []  # i nodi del grafo
    edges = []  # gli archi del grafo

    for gateway in result:
        vertices.append(gateway)
        temp_result = result.copy()  # creo una copia del dizionario
        temp_result.pop(gateway)  # e ne elimino l'elemento attuale
        for node in temp_result:
            if not esiste_arco(edges, gateway, node):  # se non esiste già l'arco che connette il gateway attuale
                # con il nodo attuale (cioè qualsiasi altro gateway), lo aggiungo al grafo (senza questo check avrei
                # un multigrafo, noi invece vogliamo creare un grafo semplice)
                edges.append({
                    "node_one": gateway,
                    "node_two": node,
                    "costo": distance_by_coord((result.get(gateway)['latitudine'],  # Vengono passate delle tuple
                                                result.get(gateway)['longitudine']),  # di coordinate
                                               (result.get(node)['latitudine'],
                                                result.get(node)['longitudine'])) * rn.uniform(0.75, 1.25)
                    # La funzione costo è proporzionale alla distanza fra i due dispositivi,
                    # ma moltiplicata per un fattore casuale (per fare in modo che non dipenda
                    # esclusivamente dalla distanza)
                })

    # Algoritmo di Kruskal:
    # 1) Seleziono l'arco di costo minimo fra quelli non ancora considerati e lo aggiungo alla soluzione
    # 2) Se il grafo risultante contiene un ciclo lo rimuovo dalla soluzione e continuo
    # 3) Se il grafo, invece, è aciclico, lo mantengo nella soluzione e continuo
    # 4) Mi fermo se ho esaminato tutti gli archi o se len(soluzione) == n-1 (numero di vertici, o nodi, -1)

    # ordino gli archi per costo
    edges = sorted(edges,
                   key=lambda item: item["costo"],
                   reverse=False)  # dal più basso al più alto

    # creo un array che contiene gli archi che ho selezionato
    selected = []
    while len(edges) > 0 and len(selected) < len(vertices) - 1:
        # aggiungo l'arco alla soluzione (il primo elemento di edges
        # è sempre quello con costo minore)
        selected.append(edges[0])
        # verifico che il grafo attuale non contenga cicli
        # Devo passare una copia del dizionario "selected" o la
        # funzione modifica il dizionario originale
        selected_copy = selected.copy()
        if ha_cicli(selected_copy):
            # ha cicli, quindi lo rimuovo
            selected.pop(-1)
        # in ogni caso, elimino l'arco appena considerato
        edges.pop(0)

    # Stampo gli archi selezionati
    print("Archi selezionati per il MST:")
    for selected_edge in selected:
        print("{} - {} - {}".format(selected_edge["node_one"], selected_edge["node_two"], selected_edge["costo"]))


def print_sensori(sensors):
    m = folium.Map(location=[44.50, 11], tiles="OpenStreetMap", zoom_start=8)

    for i in range(len(sensors)):
        temp_sensor = sensors[i]
        folium.Circle(
            location=(temp_sensor.latitudine, temp_sensor.longitudine),
            popup='id: ' + str(temp_sensor.id) + 'lat: ' + str(temp_sensor.latitudine) + 'long: ' + str(
                temp_sensor.longitudine),
            radius=float(temp_sensor.portata),
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)
    m.save('./1-sensors.html')


def find_sensor_by_id(sensor):
    for sen in sensors:
        if sen.id == sensor:
            return sen
    return None


def display_solution(solution):
    m = folium.Map(location=[44.50, 11], tiles="OpenStreetMap", zoom_start=8)
    for gateway in solution:
        color = "#%06x" % rn.randint(0, 0xFFFFFF)
        folium.Marker(
            location=[solution.get(gateway)['latitudine'], solution.get(gateway)['longitudine']],
            popup='id: ' + str(solution.get(gateway)['sensor_id']) +
                  ' latitudine: ' + str(solution.get(gateway)['latitudine']) +
                  ' longitudine: ' + str(solution.get(gateway)['longitudine']) +
                  ' sensori coperti: ' + str(solution.get(gateway)['sensor_covered']),
        ).add_to(m)
        for sensor in solution.get(gateway)['sensor_covered']:
            sensore = find_sensor_by_id(sensor)
            folium.Circle(
                location=(sensore.latitudine, sensore.longitudine),
                popup='id: ' + str(sensore.id) + ' lat: ' + str(sensore.latitudine) + ' long: ' + str(
                    sensore.longitudine),
                radius=float(sensore.portata),
                color=str(color),
                labels=str(sensore.id),
                fill=True,
                fill_color=str(color)
            ).add_to(m)

    m.save('./2-solution.html')


# Inutilizzato.
# Metodo creato in origine per plottare il nostro scenario, ora si
# utilizza la rappresentazione tramite mappa (pacchetto folium).
# I raggi dei sensori non saranno disegnati correttamente.
@deprecated(reason="Utilizzare il metodo display_solution()")
def plot_graph_old():
    global sensors
    x = []
    y = []
    colors = []
    labels = []

    ax = plt.axes(xlim=(0, max_x), ylim=(0, max_y))
    for (index, a_sens) in enumerate(sensors):
        x.append(a_sens.longitudine)
        y.append(a_sens.latitudine)

        radius = a_sens.portata

        colors.append(a_sens.id)

        if verbose:
            center = "center: x={} y={}".format(round(a_sens.longitudine), round(a_sens.latitudine))
            coords = "range: x={}-{} | y={}-{}".format(round(a_sens.longitudine - radius),
                                                       round(a_sens.longitudine + radius),
                                                       round(a_sens.latitudine - radius),
                                                       round(a_sens.latitudine + radius))
            labels.append("id={} r={}\n{}\n{}".format(a_sens.id, round(radius), center, coords))
        elif quiet:
            labels.append("{}".format(a_sens.id))
        else:
            labels.append("id:{} r={}".format(a_sens.id, round(radius)))

        ax.add_artist(plt.Circle((a_sens.longitudine, a_sens.latitudine), radius,
                                 color=plt.cm.get_cmap(color_map_name).colors[i * round(256 / num_sensori)],
                                 fill=True, alpha=0.5))  # Disegna i raggi dei sensori

    ax.scatter(x, y, c=colors, s=5, cmap=color_map_name, alpha=1.0)  # Disegna i centri dei sensori

    for x_pos, y_pos, label in zip(x, y, labels):
        ax.annotate(label, xy=(x_pos, y_pos), xytext=(7, 0), textcoords='offset points',
                    ha='left', va='center')

    ax.set_aspect('equal', anchor="C")
    ax.set_xbound(lower=min_x, upper=max_x)
    ax.set_ybound(lower=min_y, upper=max_y)
    plt.grid()
    plt.show()


# ----MAIN
if __name__ == '__main__':
    # -----------------------------------
    # DEFINIZIONE DATI
    # -----------------------------------
    num_sensori = 50
    color_map_name = "viridis"
    verbose = len(sys.argv) > 1 and "-v" in sys.argv
    more_verbose = len(sys.argv) > 1 and "-vv" in sys.argv
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

    # -----------------------------------
    # COSTRUZIONE DELLO SCENARIO
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

    print_sensori(sensors)
    result = greedy_optimization(sensors, sens_dict_ord_by_cap)
    # greedy_optimization(sensors, sens_dict_ord_by_num_sensori)

    # greedy_optimization(sensors, sens_dict_ord_by_cap, pack_by="capacita")
    # greedy_optimization(sensors, sens_dict_ord_by_num_sensori, pack_by="capacita")

    display_solution(result)
    minimum_spanning_tree(result)

    # TODO Considerare queste idee:
    # 1) Una funzione che fa il "test di ammissibilità", ossia che data una soluzione fa tutti i controlli
    # per verificare se i vincoli sono stati rispettati (single demand, capacità massima dei dispositivi, ...)
    # 2) Aggiungere come criterio nella greedy non solo il massimo rapporto capacità/costo,
    # ma anche un ulteriore valore che considera quanti sensori sto coprendo, ossia: se ho un solo sensore di
    # capacità 8 e un gateway di capacità 8, il rapporto capacità/costo è 1.0 (il massimo). Però vorrei mettere
    # in testa al nostro dizionario di siti da considerare quelli che hanno un rapporto capacità/costo elevato
    # e che contemporaneamente coprono molti sensori, così "sfoltisco" il prima possibile i siti molto densi.
    # E' un po' una combinazione del rapporto capacità/costo e numsensori/costo.
