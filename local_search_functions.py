import math
import random

from greedy_functions import greedy_optimization, calcola_scenario
from graph_functions import minimum_spanning_tree
from utility_functions import get_gateways_classes
from display_functions import find_sensor_by_id
from feasibility_functions import controlla_ammisibilita

tasso_distruzione = 30  # In percentuale, ad es. 10, o 30
temperature = 100

def costo_totale_soluzione(solution):
    costo_totale = 0
    for a_gateway in solution.values():
        costo_totale += a_gateway["costo"]

    mst, costo_mst = minimum_spanning_tree(solution)

    return costo_totale + costo_mst


def destroy(solution, method='costo'):
    # Ordino la soluzione per costo del dispositivo decrescente
    if method == 'costo':
        solution = {k: v for k, v in sorted(solution.items(),
                                        key=lambda item: item[1]["costo"],
                                        reverse=True)}

    else:
        shuffled = list(solution.values())
        random.shuffle(shuffled)
        solution = dict(zip(solution, shuffled))


    quanti_distruggere = round(len(solution) * tasso_distruzione / 100)
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


def repair(destroyed_solution, sensori_scoperti, gateways):
    sens_dict = calcola_scenario(sensori_scoperti, gateways)
    new_solution, new_cost = greedy_optimization(sensori_scoperti, gateways, sens_dict)
    # Unisco la soluzione distrutta e il pezzo appena riparato
    repaired_solution = destroyed_solution.copy()
    for a_gateway in new_solution.keys():
        index = max(repaired_solution.keys()) + 1
        repaired_solution[index] = new_solution[a_gateway]

    ammissibile, reason = controlla_ammisibilita(repaired_solution)
    if not ammissibile:
        print("Questa soluzione NON è ammissibile!!! "+reason)

    return repaired_solution


# Ricerca Locale tramite Destroy and Repair
def accept(costo_soluzione_corrente, costo_migliore_soluzione,num_iter):
    global temperature

    # se non è migliore deevo acceettare il peeggiormanto con una certa probabilità (Simulated Annealing)
    delta=costo_migliore_soluzione-costo_soluzione_corrente

    prob_accettata = math.exp((delta)/temperature) #è un valore tra 0 e unp perchè c'è il meno all'esponente

    if random.uniform(0, 1) < prob_accettata:
        temperature = temperature * (1/100 ** (1.0/num_iter))
        return True
    temperature = temperature * (1/100 ** (1.0/num_iter))
    return False

def large_neighborhood_search(initial_solution, gateways, num_iterazioni=10,destroy_method='costo'):
    soluzione_corrente = initial_solution
    migliore_soluzione = soluzione_corrente  # Ottimo candidato (migliore finora)
    costo_migliore_soluzione = costo_totale_soluzione(soluzione_corrente)
    migliore_in_assoluto = initial_solution
    costo_migliore_in_assoluto = costo_migliore_soluzione
    k = 0

    while k < num_iterazioni :  # 3 ricerche consecutive senza miglioramento, max "n" iterazioni
        print(f"--------RICERCA LOCALE: ITERAZIONE {k+1}--------")
        destroyed_solution, sensori_scoperti, classe_gateway_tolti = destroy(migliore_soluzione,destroy_method)
        # Aggiungo al listino i gateway che ho rimosso con la destroy
        for a_gateway in classe_gateway_tolti:
            gateways.append(get_gateways_classes()[a_gateway])
        gateways = sorted(gateways, key=lambda item: item.costo, reverse=False)

        soluzione_corrente = repair(destroyed_solution, sensori_scoperti, gateways)

        costo_soluzione_corrente = costo_totale_soluzione(soluzione_corrente)
        stringa = "Attuale" if costo_soluzione_corrente < costo_migliore_soluzione else "Migliore"
        print(f"Migliore: {round(costo_migliore_soluzione)} | Attuale: {round(costo_soluzione_corrente)} | "
              f"Scelgo {stringa}\n")
        if costo_soluzione_corrente < costo_migliore_soluzione:
            migliore_soluzione = soluzione_corrente
            costo_migliore_soluzione = costo_soluzione_corrente
            if costo_soluzione_corrente < costo_migliore_in_assoluto:
                costo_migliore_in_assoluto = costo_soluzione_corrente
                migliore_in_assoluto = soluzione_corrente

        if accept(costo_soluzione_corrente,  costo_migliore_soluzione, num_iterazioni):
            migliore_soluzione = soluzione_corrente
            costo_migliore_soluzione = costo_soluzione_corrente

        k += 1

    return migliore_in_assoluto, costo_migliore_in_assoluto
