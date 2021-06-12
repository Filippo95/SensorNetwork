# Progetto Ricerca Operativa - n.46 "Sensor Network" - A.A. 2020-21
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import random as rn
import pprint
import display_functions
from graph_functions import minimum_spanning_tree
from utility_functions import print_scenario
from greedy_functions import calcola_scenario, find_best_gateway, find_covered
from feasibility_functions import controlla_ammisibilita
from math import ceil


random_seed = 12345  # Per la riproducibilità degli esempi
# Il seed originale è 1625

num_sensori = 500  # Quanti sensori generare

# -----------------------------------
# VARIABILI GLOBALI
# -----------------------------------

# lista di sensori
sensors = []

# lista di gateway
gateways = []

max_x = 12  # longitudine massima est
min_x = 11  # ovest
max_y = 45  # latitudine minima nord
min_y = 44  # sud


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
    def __init__(self, an_id, capacita, costo):
        self.id = an_id  # ID o "classe" del dispositivo
        self.longitudine = 0
        self.latitudine = 0
        self.costo = costo
        self.capacita = capacita
        self.capacita_elab_unit = "msg/s"


def greedy_optimization(sensors, gateways, sens_dict_ordered, pack_by="distanza_capacita"):
    # Seleziono per primi i siti in cui ho rapporto capacità/costo maggiore
    # (o rapporto numsensori/costo maggiore)
    selected = {}
    sensors_copy = sensors.copy()
    utilizzo_gateway = [0, 0, 0, 0, 0]
    costo_totale = 0
    i = 0
    while len(sens_dict_ordered) > 0:
        (where, temp_val) = list(sens_dict_ordered.items())[0]

        which_gateway = find_best_gateway(temp_val["tot_capacita"], gateways)
        if which_gateway.id != 0:  # Ho disponibilità illimitata dei gateway di classe 0
            gateways.remove(which_gateway)
        utilizzo_gateway[which_gateway.id] += 1

        if temp_val["tot_capacita"] > which_gateway.capacita:
            which_covered = find_covered(where, temp_val["senders"], which_gateway.capacita, pack_by)
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
            "max_capacity": which_gateway.capacita,
            "sensor_covered": arr
        }
        costo_totale += which_gateway.costo
        i += 1
        # Rimuovo da una copia dell'array dei sensori i sensori che ho
        # coperto con questa iterazione
        for a_sensor in which_covered:
            # Ho rimosso il check "if a_sensor in sensors_copy", perchè  per come abbiamo scritto
            # il codice, quella condizione sarà sempre vera
            sensors_copy.remove(a_sensor)
        if not quiet:
            print("\nITERAZIONE: " + str(i - 1))
            for temp in sensors_copy:
                print(temp.id, end=',')
            print("\n")

        # aggiorno lo scenario dopo l'assegnazione, e dopo aver rimosso quelli già assegnati
        sens_dict_ordered = calcola_scenario(sensors_copy, gateways)

    # Stampo l'utilizzo dei dispositivi per classe
    print("\n\n\n")
    print(f"Sono stati utilizzati:\n"
          f"{utilizzo_gateway[0]} dispositivi di classe 0, costo totale {utilizzo_gateway[0] * 6}\n"
          f"{utilizzo_gateway[1]} dispositivi di classe 1, costo totale {utilizzo_gateway[1] * 14}\n"
          f"{utilizzo_gateway[2]} dispositivi di classe 2, costo totale {utilizzo_gateway[2] * 25}\n"
          f"{utilizzo_gateway[3]} dispositivi di classe 3, costo totale {utilizzo_gateway[3] * 75}\n"
          f"{utilizzo_gateway[4]} dispositivi di classe 4, costo totale {utilizzo_gateway[4] * 175}\n")

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


# ----MAIN
if __name__ == '__main__':
    # Come far partire il programma da riga di comando:
    # python main.py [numsensori] [seed] [-v] [-vv] [-q]
    # O passo sia il numero dei sensori sia il seed, oppure
    # il programma utilizzerà entrambi i valori di default.

    # -----------------------------------
    # DEFINIZIONE DATI
    # -----------------------------------
    color_map_name = "viridis"

    if len(sys.argv) > 2:
        num_sensori = int(sys.argv[1])
        random_seed = int(sys.argv[2])

    rn.seed(random_seed)

    verbose = len(sys.argv) > 1 and "-v" in sys.argv
    more_verbose = len(sys.argv) > 1 and "-vv" in sys.argv
    quiet = len(sys.argv) > 1 and "-q" in sys.argv

    for i in range(num_sensori):
        sensors.append(Sensor(i))

    # Definiamo il listino dei dispositivi, ordinato
    # secondo le loro capacità massime
    num_lowest_class = 500
    gateways.append(Gateway(0, 8, 6))  # Gateway di classe 0: disponibilità limitata
    for i in range(num_lowest_class):
        gateways.append(Gateway(1, 15, 14))  # Gateway di classe 1
    for i in range(ceil(num_lowest_class/5)):
        gateways.append(Gateway(2, 25, 25))  # Gateway di classe 2
    for i in range(ceil(num_lowest_class/25)):
        gateways.append(Gateway(3, 50, 75))  # Gateway di classe 3
    for i in range(ceil(num_lowest_class/125)):
        gateways.append(Gateway(4, 100, 175))  # Gateway di classe 4

    # -----------------------------------
    # COSTRUZIONE DELLO SCENARIO
    # -----------------------------------

    # calcola l'insieme dei sensori con le relative proprietà
    sens_dict_ord_by_cap = calcola_scenario(sensors, gateways)
    sens_dict_ord_by_num_sensori = calcola_scenario(sensors, gateways, order_by="rapp_numsensori_costo")
    if verbose:
        print("SCENARIO - CAPACITA'/COSTO: ")
        print_scenario(sens_dict_ord_by_cap)
        print("\n\n\n\n\n---------------------------------------------------\n\n\n\n\n")
        print("SCENARIO - NUM_SENSORI/COSTO: ")
        print_scenario(sens_dict_ord_by_num_sensori)

    display_functions.display_sensors(sensors, "./solutions/"+str(random_seed)+"/"+str(num_sensori)+"/")
    result = greedy_optimization(sensors, gateways, sens_dict_ord_by_cap)
    # greedy_optimization(sensors, gateways, sens_dict_ord_by_num_sensori)

    # greedy_optimization(sensors, gateways, sens_dict_ord_by_cap, pack_by="capacita")
    # greedy_optimization(sensors, gateways, sens_dict_ord_by_num_sensori, pack_by="capacita")

    if controlla_ammisibilita(result, sensors):
        print("\n\n\n-----------------LA SOLUZIONE TROVATA E' AMMISSIBILE-----------------\n\n\n")
    else:
        print("\n\n\n-----------------LA SOLUZIONE TROVATA !!!!!NON!!!!! E' AMMISSIBILE-----------------\n\n\n")

    display_functions.display_solution(result, sensors, "./solutions/"+str(random_seed)+"/"+str(num_sensori)+"/")
    mst = minimum_spanning_tree(result)
    display_functions.display_mst(mst, result, "./solutions/"+str(random_seed)+"/"+str(num_sensori)+"/")
    display_functions.display_full_solution(mst, result, sensors, "./solutions/"+str(random_seed)+"/"+str(num_sensori)+"/")

    # TODO: Aggiungere alla greedy il calcolo del minimum spanning tree
    # La greedy deve poter cosiderare anche il costo di installare un dispositivo in un determinato sito in
    # relazione al costo del minimum spanning tree.

    # < Aggiungere come criterio nella greedy non solo il massimo rapporto capacità/costo,
    # ma anche un ulteriore valore che considera quanti sensori sto coprendo, ossia: se ho un solo sensore di
    # capacità 8 e un gateway di capacità 8, il rapporto capacità/costo è 1.0 (il massimo). Però vorrei mettere
    # in testa al nostro dizionario di siti da considerare quelli che hanno un rapporto capacità/costo elevato
    # e che contemporaneamente coprono molti sensori, così "sfoltisco" il prima possibile i siti molto densi.
    # E' un po' una combinazione del rapporto capacità/costo e numsensori/costo. >

    # TODO: Dimensionare correttamente il costo del Minimum Spanning Tree

    # TODO: Test di ammissibilità
    # Una funzione che fa il "test di ammissibilità", ossia che data una soluzione fa tutti i controlli
    # per verificare se i vincoli sono stati rispettati:
    # < 4) Qualche controllo sul minimum spanning tree? >
