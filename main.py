# Progetto Ricerca Operativa - n.46 "Sensor Network" - A.A. 2020-21
# Andrea Benini, Giacomo Bettini, Filippo Luppi
import sys
import random as rn
from math import ceil
from display_functions import display_sensors, display_solution, display_mst, display_full_solution, \
    display_difference_between_solutions
from graph_functions import minimum_spanning_tree
from utility_functions import print_scenario, get_seed, set_seed, get_verbosity, set_verbosity, \
    set_gateways_classes, set_global_sensors, prepara_cartelle_e_file, print_greedy_result, print_mst_result
from greedy_functions import calcola_scenario, greedy_optimization
from feasibility_functions import controlla_ammisibilita
from local_search_functions import large_neighborhood_search
import time

# -----------------------------------
# VARIABILI GLOBALI
# -----------------------------------

num_sensori = 100  # Quanti sensori generare (di default; si può
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
        self.portata = rn.uniform(5000, 15000)  # raggio di copertura in metri
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
    start_time = time.time()
    # Come far partire il programma da riga di comando:
    # python main.py <numsensori> <seed> <order_by> <pack_by> <num_iter_ls> <fattore_riduzione>
    # [-v] [-vv] [-q] [--no-display]
    # I parametri fra parentesi angolari vanno passati tutti.
    # Passare al massimo uno solo dei modificatori dell'output (-v, -vv o -q).

    order_by = "rapp_cap_costo"
    pack_by = "distanza_capacita"
    num_iter_local_search = 50
    no_display = False
    fattore_riduzione = 4

    if len(sys.argv) > 6:
        try:
            num_sensori = int(sys.argv[1])
            set_seed(int(sys.argv[2]))
            order_by = str(sys.argv[3])  # order_by può essere: rapp_cap_costo | rapp_numsensori_costo
            pack_by = str(sys.argv[4])  # pack_by può essere: distanza_capacita | capacita
            num_iter_local_search = int(sys.argv[5])
            fattore_riduzione = int(sys.argv[6])
        except ValueError as e:
            print(e)
            print("\nUso:")
            print("python main.py <numsensori> <seed> <order_by> <pack_by> <num_iter_ls> [-v|-vv|-q] [--no-display]")
            print("I parametri fra parentesi angolari vanno passati tutti.")
            print("Passare al massimo uno solo dei modificatori dell'output (-v, -vv o -q).")
            sys.exit(-1)

    no_display = "--no-display" in sys.argv

    set_verbosity(
        "-q" in sys.argv,
        "-v" in sys.argv,
        "-vv" in sys.argv
    )

    # Imposto il seed
    rn.seed(get_seed())

    # Per la stampa su file
    original_stdout = sys.stdout

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

    num_class_1 = 500  # Originale: 500
    num_class_2 = ceil(num_class_1 / fattore_riduzione)
    num_class_3 = ceil(num_class_1 / fattore_riduzione**2)
    num_class_4 = ceil(num_class_1 / fattore_riduzione**3)
    gateways.append(classe_0)  # Gateway di classe 0
    for i in range(num_class_1):
        gateways.append(classe_1)  # Gateway di classe 1
    for i in range(num_class_2):
        gateways.append(classe_2)  # Gateway di classe 2
    for i in range(num_class_3):
        gateways.append(classe_3)  # Gateway di classe 3
    for i in range(num_class_4):
        gateways.append(classe_4)  # Gateway di classe 4

    print("-----------------INIZIALIZZAZIONE-----------------")
    print(f"Numero di sensori: {num_sensori} | Seed: {get_seed()}")
    print(f"Order-by: {order_by} | Pack-by: {pack_by}\n\n")
    print("Listino dei dispositivi:")
    print(f"Classe 0 -> Costo: {classe_0.costo}, Disponibilità: \u221e")
    print(f"Classe 1 -> Costo: {classe_1.costo}, Disponibilità: {num_class_1}")
    print(f"Classe 2 -> Costo: {classe_2.costo}, Disponibilità: {num_class_2}")
    print(f"Classe 3 -> Costo: {classe_3.costo}, Disponibilità: {num_class_3}")
    print(f"Classe 4 -> Costo: {classe_4.costo}, Disponibilità: {num_class_4}")
    print("\n")

    # Preparo le cartelle e i file per le soluzioni
    saving_path, saving_path_ls, text_output_path, text_output_path_grafici = \
        prepara_cartelle_e_file(num_sensori, order_by, pack_by, num_iter_local_search, no_display)

    init_time = time.time() - start_time
    if not get_verbosity().quiet:
        print(f"Inizializzazione completata in {round(init_time)} secondi")

    # -----------------------------------
    # COSTRUZIONE DELLO SCENARIO
    # -----------------------------------
    greedy_time_start = time.time()

    # Crea un dizionario dei sensori con le relative proprietà, di default i sensori vengono ordinati
    # secondo il rapporto capacità/costo (quanta capacità totale posso coprire posizionando un gateway in
    # quel sito / il costo del gateway che può coprire quella capacità (o il gateway con capacità massima,
    # se non ce ne fosse uno che riesce a coprirla tutta)).
    # In alternativa lo si può ordinare per il rapporto fra il numero di sensori coperti e il costo
    # di installazione del gateway che può coprire la capacità richiesta.
    sens_dict = calcola_scenario(sensors, gateways, order_by=order_by)
    if get_verbosity().verbose:
        print_scenario(sens_dict, order_by)

    # creo il file .html che mostra i sensori sulla mappa
    if not no_display:
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

    if not no_display:
        with open(text_output_path, 'a') as f:
            if ammissibile:
                sys.stdout = f
                print(f"Prima esecuzione:")
                print(f"Il costo della greedy è {greedy_cost}")
                sys.stdout = original_stdout
            else:
                sys.stdout = f
                print("Sono rimasti sensori da coprire. Nessuna soluzione ammissibile trovata!")
                sys.stdout = original_stdout

    # Stampo il dizionario che mostra dove e quali dispositivi ho installato
    print_greedy_result(result)

    # creo il file .html che mostra la soluzione (ovvero dove ho installato i vari gateway)
    if not no_display:
        display_solution(result, saving_path)

    if not get_verbosity().quiet:
        greedy_time = time.time() - greedy_time_start
        print(f"Prima greedy completata in {round(greedy_time)} secondi")

    # -----------------------------------
    # MINIMUM SPANNING TREE
    # -----------------------------------
    mst_time_start = time.time()

    # calcolo il MST del risultato
    mst, mst_cost = minimum_spanning_tree(result)
    # stampo gli archi selezionati e i relativi costi
    print(f"\nIl costo del MST è {round(mst_cost)}")
    print_mst_result(mst)

    if not no_display:
        with open(text_output_path, 'a') as f:
            sys.stdout = f
            print(f"Il costo del MST è {round(mst_cost)}")
            sys.stdout = original_stdout

    # creo il file .html che mostra il MST
    if not no_display:
        display_mst(mst, result, saving_path)

    if not get_verbosity().quiet:
        mst_time = time.time() - mst_time_start
        print(f"Primo MST completato in {round(mst_time)} secondi")

    # -----------------------------------
    # COSTO TOTALE
    # -----------------------------------

    # creo il file .html che mostra l'intera soluzione
    if not no_display:
        display_full_solution(mst, result, saving_path)

    funzione_obiettivo = greedy_cost + mst_cost

    print(f"\nIl costo totale è {round(funzione_obiettivo)}")

    if not no_display:
        with open(text_output_path, 'a') as f:
            sys.stdout = f
            print(f"Il costo totale è {round(funzione_obiettivo)}")
            sys.stdout = original_stdout

    # -----------------------------------
    # RICERCHE LOCALI
    # -----------------------------------
    local_search_time_start = time.time()

    print("\n\n\n----------------------RICERCHE LOCALI----------------------\n")
    print("\tNota: Tutti i valori stampati sono arrotondati.")
    print("\tNota: Delta negativo -> Miglioramento.\n\n")
    print("----------------------RICERCA LOCALE PER COSTO----------------------\n")

    # Ricerca locale Destroy and Repair effettuata in base ai dispositivi di costo massimo
    prima_nuova_soluzione, prima_nuova_funzione_obiettivo = large_neighborhood_search(result, gateways,
                                                                                      order_by, pack_by, 'costo',
                                                                                      num_iter_local_search)

    primo_nuovo_mst, primo_nuovo_costo_mst = minimum_spanning_tree(prima_nuova_soluzione)
    prima_nuova_greedy_cost = prima_nuova_funzione_obiettivo - primo_nuovo_costo_mst
    primo_risparmio = funzione_obiettivo - prima_nuova_funzione_obiettivo

    if not no_display:
        with open(text_output_path, 'a') as f:
            sys.stdout = f
            print(f"\nDopo la ricerca locale Destroy and Repair per costo massimo "
                  f"con {num_iter_local_search} iterazioni:")
            print(f"Il costo della greedy è {round(prima_nuova_greedy_cost)}")
            print(f"Il costo del MST è {round(primo_nuovo_costo_mst)}")
            print(f"Il costo totale è {round(prima_nuova_funzione_obiettivo)}")
            print(f"La funzione obiettivo è scesa di {round(primo_risparmio)} "
                  f"rispetto alla soluzione iniziale")
            sys.stdout = original_stdout

    print("\n\n\n----------------------RICERCA LOCALE RANDOM----------------------\n\n\n")
    # Ricerca locale Destroy and Repair effettuata con metodo random
    nuova_soluzione, funzione_obiettivo_new = large_neighborhood_search(prima_nuova_soluzione, gateways,
                                                                        order_by, pack_by, 'random',
                                                                        num_iter_local_search)
    if not no_display:
        display_solution(nuova_soluzione, saving_path_ls)

    mst_new, mst_cost_new = minimum_spanning_tree(nuova_soluzione)

    if not no_display:
        display_mst(mst_new, nuova_soluzione, saving_path_ls)
        display_full_solution(mst_new, nuova_soluzione, saving_path_ls)

    greedy_cost_new = funzione_obiettivo_new - mst_cost_new
    risparmio_dopo_greedy = prima_nuova_funzione_obiettivo - funzione_obiettivo_new
    risparmio_totale = funzione_obiettivo - funzione_obiettivo_new

    if not no_display:
        with open(text_output_path, 'a') as f:
            sys.stdout = f
            print(f"\nDopo la ricerca locale Destroy and Repair casuale con {num_iter_local_search} iterazioni:")
            print(f"Il costo della greedy è {round(greedy_cost_new)}")
            print(f"Il costo del MST è {round(mst_cost_new)}")
            print(f"Il costo totale è {round(funzione_obiettivo_new)}")
            print(f"La funzione obiettivo è scesa di {round(risparmio_dopo_greedy)} "
                  f"rispetto alla prima ricerca locale")
            print(f"La funzione obiettivo è scesa di {round(risparmio_totale)} "
                  f"rispetto alla soluzione iniziale")
            sys.stdout = original_stdout

    print(f"\n\nIl costo totale della soluzione dopo la ricerca locale è {round(funzione_obiettivo_new)}")

    print(f"\n\nCosto iniziale: {round(funzione_obiettivo)}, Costo finale: {round(funzione_obiettivo_new)}, "
          f"la funzione obiettivo si è ridotta di {round(risparmio_totale)}")
    if not no_display:
        display_difference_between_solutions(nuova_soluzione, mst_new, result, mst, saving_path_ls)

    if not get_verbosity().quiet:
        local_search_time = time.time() - local_search_time_start
        print(f"\nRicerche locali completate in {round(local_search_time)} secondi")

    # Stampa sul file csv il riepilogo dell'esecuzione, si potrà usare per creare grafici e statistiche
    # Non vengono inserite righe duplicate
    with open(text_output_path_grafici, 'r+') as f:
        output_string = \
            f"{get_seed()},{num_sensori},{order_by},{pack_by},{num_iter_local_search}," + \
            f"{round(greedy_cost)},{round(mst_cost)},{round(funzione_obiettivo)}," + \
            f"{round(prima_nuova_funzione_obiettivo)},{round(funzione_obiettivo_new)}," + \
            f"{num_class_1},{fattore_riduzione}"

        a_line = f.readline()[:-1]  # viene letto anche il carattere \n, che va ignorato
        already_written = False
        while a_line != '' and not already_written:
            if a_line == output_string:
                already_written = True
            a_line = f.readline()[:-1]

        if not already_written:
            sys.stdout = f
            print(output_string)
            sys.stdout = original_stdout
            print("\nSoluzione aggiunta al file .csv")
        else:
            print("\nSoluzione non aggiunta al file .csv, è già presente")

    if not get_verbosity().quiet:
        end_time = time.time() - start_time
        print(f"\nComputazione completata in {round(end_time)} secondi")
