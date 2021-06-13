# Progetto Ricerca Operativa - n.46 "Sensor Network" - A.A. 2020-21
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import os
import random as rn
import display_functions
from graph_functions import minimum_spanning_tree
from utility_functions import print_scenario, get_seed, set_seed, get_verbosity, set_verbosity
from greedy_functions import calcola_scenario, greedy_optimization
from feasibility_functions import controlla_ammisibilita
from math import ceil

# -----------------------------------
# VARIABILI GLOBALI
# -----------------------------------

num_sensori = 50  # Quanti sensori generare (di default; si può
# controllare tramite i parametri da riga di comando)

# lista di sensori
sensors = []

# lista di gateway
gateways = []

max_x = 12  # longitudine massima est   DX
min_x = 10  # ovest                     SX
max_y = 45  # latitudine minima nord    UP
min_y = 44  # sud                       DN
# Originali: 12 / 11 / 45 / 44


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


# ----MAIN
if __name__ == '__main__':
    # Come far partire il programma da riga di comando:
    # python main.py [numsensori] [seed] [-v] [-vv] [-q]
    # O passo sia il numero dei sensori sia il seed, oppure
    # il programma utilizzerà entrambi i valori di default.
    # Passare uno solo dei modificatori dell'output (-v, -vv o -q).

    if len(sys.argv) > 2:
        num_sensori = int(sys.argv[1])
        set_seed(int(sys.argv[2]))

    set_verbosity(
        "-q" in sys.argv,
        "-v" in sys.argv,
        "-vv" in sys.argv
    )

    rn.seed(get_seed())

    # Creiamo i sensori in maniera pseudo-casuale
    for i in range(num_sensori):
        sensors.append(Sensor(i))

    # Definiamo il listino dei dispositivi, ordinato
    # secondo le loro capacità massime, e impostiamo
    # una disponibilità limitata per ogni classe di
    # dispositivo, a parte la più basica di cui si
    # suppone si abbia disponibilità illimitata
    classe_0 = Gateway(0, 8, 6)
    classe_1 = Gateway(1, 15, 14)
    classe_2 = Gateway(2, 25, 25)
    classe_3 = Gateway(3, 50, 75)
    classe_4 = Gateway(4, 100, 175)
    num_lowest_class = 500  # Originale: 500
    gateways.append(classe_0)  # Gateway di classe 0
    for i in range(num_lowest_class):
        gateways.append(classe_1)  # Gateway di classe 1
    for i in range(ceil(num_lowest_class/5)):
        gateways.append(classe_2)  # Gateway di classe 2
    for i in range(ceil(num_lowest_class/25)):
        gateways.append(classe_3)  # Gateway di classe 3
    for i in range(ceil(num_lowest_class/125)):
        gateways.append(classe_4)  # Gateway di classe 4

    # -----------------------------------
    # COSTRUZIONE DELLO SCENARIO
    # -----------------------------------

    # Crea un dizionario dei sensori con le relative proprietà
    sens_dict_ord_by_cap = calcola_scenario(sensors, gateways)
    sens_dict_ord_by_num_sensori = calcola_scenario(sensors, gateways, order_by="rapp_numsensori_costo")
    if get_verbosity().verbose:
        print("SCENARIO - CAPACITA'/COSTO: ")
        print_scenario(sens_dict_ord_by_cap)
        print("\n\n\n\n\n---------------------------------------------------\n\n\n\n\n")
        print("SCENARIO - NUM_SENSORI/COSTO: ")
        print_scenario(sens_dict_ord_by_num_sensori)

    # Preparo le cartelle necessarie
    saving_path = f"./solutions/{get_seed()}/{num_sensori}/"
    if not os.path.isdir("./solutions"):
        os.mkdir("./solutions")
    if not os.path.isdir(f"./solutions/{get_seed()}"):
        os.mkdir(f"./solutions/{get_seed()}")
    if not os.path.isdir(saving_path):
        os.mkdir(saving_path)

    display_functions.display_sensors(sensors, saving_path)
    result, greedy_cost = greedy_optimization(sensors, gateways, sens_dict_ord_by_cap)
    # greedy_optimization(sensors, gateways, sens_dict_ord_by_num_sensori)

    # greedy_optimization(sensors, gateways, sens_dict_ord_by_cap, pack_by="capacita")
    # greedy_optimization(sensors, gateways, sens_dict_ord_by_num_sensori, pack_by="capacita")

    if controlla_ammisibilita(result, sensors):
        print("\n\n\n-----------------LA SOLUZIONE TROVATA E' AMMISSIBILE-----------------\n\n\n")
    else:
        print("\n\n\n-----------------LA SOLUZIONE TROVATA !!!!!NON!!!!! E' AMMISSIBILE-----------------\n\n\n")
        print("\n\n\n-----------------COMPUTAZIONE INTERROTTA-----------------\n\n\n")
        sys.exit()

    display_functions.display_solution(result, sensors, saving_path)
    mst, mst_cost = minimum_spanning_tree(result)
    display_functions.display_mst(mst, result, saving_path)
    display_functions.display_full_solution(mst, result, sensors, saving_path)

    funzione_obiettivo = greedy_cost + mst_cost

    print(f"\n\nIl costo totale è {round(funzione_obiettivo)}")

    # TODO: Aggiungere alla greedy il calcolo del minimum spanning tree
    # La greedy deve poter considerare anche il costo di installare un dispositivo in un determinato sito in
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
