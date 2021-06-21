import math
import random as rn
import sys
from greedy_functions import greedy_optimization, calcola_scenario
from graph_functions import minimum_spanning_tree
from utility_functions import get_gateways_classes, set_verbosity
from display_functions import find_sensor_by_id
from feasibility_functions import controlla_ammisibilita


def costo_totale_soluzione(solution):
    costo_totale = 0
    for a_gateway in solution.values():
        costo_totale += a_gateway["costo"]

    mst, costo_mst = minimum_spanning_tree(solution)

    return costo_totale + costo_mst


def destroy(solution, method='costo'):
    tasso_distruzione = 30  # In percentuale, originale: 30
    quanti_distruggere = round(len(solution) * tasso_distruzione / 100)

    # Se il metodo è "costo" ordino la soluzione per costo del dispositivo decrescente.
    # Per aggiungere non-determinismo alla destroy, aggiungo un valore casuale
    # che indica quali dispositivi non di costo massimo distruggere.
    # Nello specifico: l'ordinamento della soluzione viene effettuato su due campi,
    # prima per classe (ossia per costo), poi i dispositivi della stessa
    # classe allora si ordinano per un valore casuale fra 0 e 1.
    if method == 'costo':
        # for a_gateway in solution.values():
        #     a_gateway["random_factor"] = rn.uniform(0, 1)

        solution = {k: v for k, v in sorted(solution.items(),
                                            key=lambda item: (item[1]["classe"], rn.uniform(0, 1)),
                                            reverse=True)}
    else:  # Sennò viene effettuata una destroy random
        shuffled = list(solution.values())
        rn.shuffle(shuffled)
        solution = dict(zip(solution, shuffled))

    sensori_scoperti = []
    classe_gateway_tolti = []
    i = 0
    while i < quanti_distruggere:
        key, a_gateway = list(solution.items())[0]
        for sens in a_gateway["sensor_covered"]:
            sensori_scoperti.append(find_sensor_by_id(sens))
        classe_gateway_tolti.append(a_gateway["classe"])
        solution.pop(key)
        i += 1

    return solution, sensori_scoperti, classe_gateway_tolti


def repair(destroyed_solution, sensori_scoperti, gateways, order_by, pack_by):
    sens_dict = calcola_scenario(sensori_scoperti, gateways)
    new_solution, new_cost = greedy_optimization(sensori_scoperti, gateways, sens_dict, order_by, pack_by)
    # Unisco la soluzione distrutta e il pezzo appena riparato
    repaired_solution = destroyed_solution.copy()
    for a_gateway in new_solution.keys():
        index = max(repaired_solution.keys()) + 1
        repaired_solution[index] = new_solution[a_gateway]

    ammissibile, reason = controlla_ammisibilita(repaired_solution)
    if not ammissibile:
        print("Questa soluzione NON è ammissibile!!! " + reason)
        return None

    return repaired_solution


# Ricerca Locale tramite Destroy and Repair
def accept(delta, temperatura):
    # se non è migliore devo accettare il peggioramento con una certa probabilità (Simulated Annealing)
    prob_accettata = math.exp(-delta / temperatura)  # è un valore tra 0 e 1
    return rn.uniform(0, 1) < prob_accettata


def large_neighborhood_search(initial_solution, gateways, order_by, pack_by, destroy_method='costo', num_iterazioni=10):
    temperatura = 100  # Valore iniziale della temperatura

    soluzione_corrente = initial_solution
    costo_soluzione_corrente = costo_totale_soluzione(soluzione_corrente)

    migliore_soluzione = soluzione_corrente  # Ottimo candidato (migliore finora)
    costo_migliore_soluzione = costo_soluzione_corrente

    k = 0
    while k < num_iterazioni:  # Effettuiamo "n" iterazioni
        print(f"\n--------RICERCA LOCALE '{destroy_method}': ITERAZIONE {k + 1}--------\n")
        destroyed_solution, sensori_scoperti, classe_gateway_tolti = destroy(soluzione_corrente, destroy_method)
        # Aggiungo al listino i gateway che ho rimosso con la destroy
        for a_gateway in classe_gateway_tolti:
            gateways.append(get_gateways_classes()[a_gateway])
        gateways = sorted(gateways, key=lambda item: item.costo, reverse=False)

        soluzione_tentativo = repair(destroyed_solution, sensori_scoperti, gateways, order_by, pack_by)
        if soluzione_tentativo is None:
            set_verbosity(quiet=True)
            print("\n\n\n-----------------LA SOLUZIONE TROVATA !!!!!NON!!!!! E' AMMISSIBILE-----------------\n\n\n")
            print("\n\n\n-----------------COMPUTAZIONE INTERROTTA-----------------\n\n\n")
            sys.exit()

        costo_soluzione_tentativo = costo_totale_soluzione(soluzione_tentativo)
        delta = costo_soluzione_tentativo - costo_soluzione_corrente

        print("Pre-accept:")
        print(f"Migliore: {round(costo_migliore_soluzione)} | Tentativo: {round(costo_soluzione_tentativo)} | "
              f"Corrente: {round(costo_soluzione_corrente)} | "
              f"Delta: {round(delta)} | Temperatura: {round(temperatura)}")

        # ACCEPT
        if delta < 0:
            soluzione_corrente = soluzione_tentativo
            costo_soluzione_corrente = costo_soluzione_tentativo
            print("ACCETTO la soluzione tentativo (costo minore della corrente)\n")
        elif accept(delta, temperatura):
            soluzione_corrente = soluzione_tentativo
            costo_soluzione_corrente = costo_soluzione_tentativo
            print("ACCETTO la soluzione tentativo (accetto il peggioramento)\n")
        else:
            print("NON ACCETTO la soluzione tentativo (costo maggiore della corrente)\n")

        print("Post-accept:")
        print(f"Migliore: {round(costo_migliore_soluzione)} | Tentativo: {round(costo_soluzione_tentativo)} | "
              f"Corrente: {round(costo_soluzione_corrente)}")

        if costo_soluzione_corrente < costo_migliore_soluzione:
            migliore_soluzione = soluzione_corrente
            costo_migliore_soluzione = costo_soluzione_corrente
            print(f"Soluzione migliore AGGIORNATA -> Migliore: {round(costo_migliore_soluzione)}\n")
        else:
            print(f"Soluzione migliore NON AGGIORNATA -> Migliore: {round(costo_migliore_soluzione)}\n")

        # Dopo ogni iterazione aggiorniamo la temperatura (La formula fa in modo che la temperatura
        # parta da 100 alla prima iterazione e arrivi a 1 all'ultima iterazione, indipendentemente
        # dal numero di iterazioni)
        temperatura = temperatura * (1 / 100 ** (1.0 / num_iterazioni))
        k += 1

    return migliore_soluzione, costo_migliore_soluzione
