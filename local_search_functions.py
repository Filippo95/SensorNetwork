# TODO: Leggere i commenti sottostanti
# Una delle prime cose da fare per effettuare una ricerca locale è quella di definire innanzitutto
# un intorno di una soluzione. Ad esempio, per noi le soluzioni dell'intorno potrebbero essere quelle ottenute
# rimuovendo dalla soluzione attuale prima 1, poi 2, poi 3, ... dispositivi (eventualmente uno per classe...), oppure
# rimuovere i primi 5 dispositivi più costosi..... A proposito di ciò si veda la slide 558 del pacco di slide unito,
# dove si definisce l'intorno per il Set Covering, problema che ha qualche somiglianza con il nostro problema.
# Successivamente bisogna esplorare l'intorno e decidere quale delle soluzioni scegliere.
# Altro.....

from greedy_functions import greedy_optimization, calcola_scenario
from graph_functions import minimum_spanning_tree
from utility_functions import get_gateways_classes
from display_functions import find_sensor_by_id

tasso_distruzione = 10  # 10%


def costo(solution):
    costo_totale = 0
    for a_gateway in solution.values():
        costo_totale += a_gateway["costo"]

    mst, costo_mst = minimum_spanning_tree(solution)

    return costo_totale + costo_mst


def destroy(solution, sensors):
    # Ordino la soluzione per costo del dispositivo decrescente
    # print(solution)
    # solution = sorted(solution.items(),
    #                  key=lambda item: item[1]["costo"],
    #                  reverse=True)
    solution = {k: v for k, v in sorted(solution.items(),
                                        key=lambda item: item[1]["costo"],
                                        reverse=True)}
    quanti_distruggere = round(len(solution) * tasso_distruzione / 100)
    sensori_scoperti = []
    classe_gateway_tolti = []
    i = 0
    while i < quanti_distruggere:
        key, a_gateway = list(solution.items())[0]
        for sens in a_gateway["sensor_covered"]:
            sensori_scoperti.append(find_sensor_by_id(sens, sensors))
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
        repaired_solution[len(destroyed_solution) + a_gateway] = new_solution[a_gateway]

    return repaired_solution


# Ricerca Locale tramite Destroy and Repair
def large_neighborhood_search(initial_solution, gateways, sensors):
    soluzione_corrente = initial_solution
    migliore_soluzione = soluzione_corrente  # Ottimo candidato (migliore finora)
    k = 0
    while k < 5:  # Per ora la StopCondition è fare 5 iterazioni
        destroyed_solution, sensori_scoperti, classe_gateway_tolti = destroy(soluzione_corrente, sensors)
        for a_gateway in classe_gateway_tolti:
            gateways.append(get_gateways_classes()[a_gateway])
            gateways = sorted(gateways, key=lambda item: item.costo, reverse=False)

        soluzione_corrente = repair(destroyed_solution, sensori_scoperti, gateways)

        # if accept(new_solution, soluzione_corrente):
        #     soluzione_corrente = new_solution
        #     k += 1

        if costo(soluzione_corrente) < costo(migliore_soluzione):
            migliore_soluzione = soluzione_corrente

        k += 1

    return migliore_soluzione
