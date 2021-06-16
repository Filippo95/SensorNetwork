# Progetto Ricerca Operativa - n.46 "Sensor Network" - A.A. 2020-21
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import pprint
import sys
import os
import random as rn
from math import ceil
from display_functions import display_sensors, display_solution, display_mst, display_full_solution, display_difference_between_solutions
from graph_functions import minimum_spanning_tree
from utility_functions import print_scenario, get_seed, set_seed, get_verbosity, set_verbosity, set_gateways_classes,\
    set_global_sensors
from greedy_functions import calcola_scenario, greedy_optimization
from feasibility_functions import controlla_ammisibilita
from local_search_functions import large_neighborhood_search, costo


# -----------------------------------
# VARIABILI GLOBALI
# -----------------------------------

num_sensori = 50  # Quanti sensori generare (di default; si può
# controllare tramite i parametri da riga di comando)

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
    # python main.py <numsensori> <seed> <order_by> <pack_by> [-v] [-vv] [-q]
    # O passo sia il numero dei sensori sia il seed, oppure
    # il programma utilizzerà entrambi i valori di default.
    # In questo caso devo passare anche il parametro order_by e pack_by
    # Passare uno solo dei modificatori dell'output (-v, -vv o -q).

    order_by = "rapp_cap_costo"
    pack_by = "distanza_capacita"

    if len(sys.argv) > 5:
        num_sensori = int(sys.argv[1])
        set_seed(int(sys.argv[2]))
        order_by = str(sys.argv[3])
        pack_by = str(sys.argv[4])
        num_iter_local_search = int(sys.argv[5])
        # L'ordinamento può essere fatto per:
        # rapp_cap_costo | rapp_numsensori_costo
        # pack_by può essere:
        # distanza_capacita | capacita

    set_verbosity(
        "-q" in sys.argv,
        "-v" in sys.argv,
        "-vv" in sys.argv
    )

    # Imposto il seed
    rn.seed(get_seed())

    # Creiamo i sensori in maniera pseudo-casuale
    sensors = []
    for i in range(num_sensori):
        sensors.append(Sensor(i))
    set_global_sensors(sensors)

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
    set_gateways_classes([classe_0, classe_1, classe_2, classe_3, classe_4])
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

    # Preparo le cartelle per le soluzioni
    saving_path = f"./solutions/{get_seed()}/{num_sensori}/"
    saving_path_ls = saving_path+"localsearch/"
    if not os.path.isdir("./solutions"):
        os.mkdir("./solutions")
    if not os.path.isdir(f"./solutions/{get_seed()}"):
        os.mkdir(f"./solutions/{get_seed()}")
    if not os.path.isdir(saving_path):
        os.mkdir(saving_path)
    if not os.path.isdir(saving_path_ls):
        os.mkdir(saving_path_ls)

    # -----------------------------------
    # COSTRUZIONE DELLO SCENARIO
    # -----------------------------------

    # Crea un dizionario dei sensori con le relative proprietà, di default i sensori vengono ordinati
    # secondo il rapporto capacità/costo (quanta capacità totale posso coprire posizionando un gateway in
    # quel sito / il costo del gateway che può coprire quella capacità (o il gateway con capacità massima,
    # se non ce ne fosse uno che riesce a coprirla tutta)).
    # In alternativa lo si può ordinare per il rapporto fra il numero di sensori coperti e il costo
    # di installazione del gateway che può coprire la capacità richiesta.
    sens_dict = calcola_scenario(sensors, gateways, order_by=order_by)
    if get_verbosity().verbose:
        print("\n\n\n\n\n---------------------------------------------------\n\n\n\n\n")
        print("SCENARIO - ORDINATO PER: "+order_by)
        print_scenario(sens_dict)

    # creo il file .html che mostra i sensori sulla mappa
    display_sensors(sensors, saving_path)

    # -----------------------------------
    # GREEDY
    # -----------------------------------
    print("-----------------GREEDY-----------------")

    # Con il parametro pack_by è possibile modificare il comportamento della greedy in quei casi in cui
    # un gateway non riesca a coprire tutta la capacità di un sito, di default viene risolto uno zaino binario
    # con una greedy che seleziona i sensori da coprire per primi secondo il loro rapporto capacità/distanza
    # (ossia si coprono per primi i sensori che hanno capacità grandi e sono vicini al gateway che stiamo installando).
    # eseguo la greedy passando lo scenario ordinato per rapporto capacità/costo
    result, greedy_cost = greedy_optimization(sensors, gateways, sens_dict, order_by, pack_by)

    ammissibile, reason_of_failure = controlla_ammisibilita(result)
    if ammissibile:
        print("\n\nLa soluzione trovata è ammissibile\n\n")
        print(f"Il costo della greedy è {greedy_cost}")
    else:
        print("\n\n\n-----------------LA SOLUZIONE TROVATA !!!!!NON!!!!! E' AMMISSIBILE-----------------\n\n\n")
        print(reason_of_failure)
        print("\n\n\n-----------------COMPUTAZIONE INTERROTTA-----------------\n\n\n")
        sys.exit()

    # Stampo il dizionario che mostra dove e quali dispositivi ho installato
    if not get_verbosity().quiet:
        print("\n\n\n")
        pp = pprint.PrettyPrinter(indent=3)
        pp.pprint(result)

    # creo il file .html che mostra la soluzione ovvero dove ho installato i vari gateway
    display_solution(result, saving_path)

    # -----------------------------------
    # MINIMUM SPANNING TREE
    # -----------------------------------

    # calcolo  il MST del risultato
    mst, mst_cost = minimum_spanning_tree(result)
    # stampo gli archi selezionati e i relativi costi
    if not get_verbosity().quiet:
        print("Archi selezionati per il MST:\n")
        for edge in mst:
            print("{} - {} - {}".format(edge["node_one"], edge["node_two"], edge["costo"]))
    print(f"\nIl costo del MST è {round(mst_cost)}")
    # creo il file .html che mostra il MST
    display_mst(mst, result, saving_path)

    # -----------------------------------
    # COSTO TOTALE
    # -----------------------------------

    # creo il file .html che mostra l'intera soluzione
    display_full_solution(mst, result, saving_path)

    funzione_obiettivo = greedy_cost + mst_cost

    print(f"\nIl costo totale è {round(funzione_obiettivo)}")

    # -----------------------------------
    # RICERCA LOCALE
    # -----------------------------------

    print("\n\n\n-----------------RICERCA LOCALE-----------------\n\n\n")
    nuova_soluzione = large_neighborhood_search(result, gateways, num_iter_local_search)

    display_solution(nuova_soluzione, saving_path_ls)
    mst_new, mst_cost_new = minimum_spanning_tree(nuova_soluzione)
    display_mst(mst_new, nuova_soluzione, saving_path_ls)
    display_full_solution(mst_new, nuova_soluzione, saving_path_ls)

    funzione_obiettivo_new = costo(nuova_soluzione)
    print(f"\n\nIl costo totale della soluzione dopo la ricerca locale è {round(funzione_obiettivo_new)}")

    print(f"\n\nCosto iniziale: {round(funzione_obiettivo)}, Costo finale: {round(funzione_obiettivo_new)}, "
          f"la funzione obiettivo è scesa di {round(funzione_obiettivo-funzione_obiettivo_new)}")
    display_difference_between_solutions(nuova_soluzione, mst_new, result, mst, saving_path_ls)

    # TODO: Aggiungere output su file di testo (simile a greedy_output)
    # Possibilmente un file di riepilogo sulla cartella dove salvo la prima soluzione e un altro
    # nella cartella localsearch

    # TODO: Idee di cui non siamo troppo convinti:
    # - Per il test di ammissibilità, fare anche qualche controllo sul minimum spanning tree?
    # - Considerare anche il costo del MST durante la greedy?
    # - Aggiungere come criterio nella greedy non solo il massimo rapporto capacità/costo,
    # ma anche un ulteriore valore che considera quanti sensori sto coprendo, ossia: se ho un solo sensore di
    # capacità 8 e un gateway di capacità 8, il rapporto capacità/costo è 1.0 (il massimo). Però vorrei mettere
    # in testa al nostro dizionario di siti da considerare quelli che hanno un rapporto capacità/costo elevato
    # e che contemporaneamente coprono molti sensori, così "sfoltisco" il prima possibile i siti molto densi.
    # E' un po' una combinazione del rapporto capacità/costo e numsensori/costo.
