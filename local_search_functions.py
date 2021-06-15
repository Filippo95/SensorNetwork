from greedy_functions import greedy_optimization, calcola_scenario
from graph_functions import minimum_spanning_tree
from utility_functions import get_gateways_classes
from display_functions import find_sensor_by_id
from feasibility_functions import controlla_ammisibilita

tasso_distruzione = 30  # In percentuale, ad es. 10, o 30


def costo(solution):
    costo_totale = 0
    for a_gateway in solution.values():
        costo_totale += a_gateway["costo"]

    mst, costo_mst = minimum_spanning_tree(solution)

    return costo_totale + costo_mst


def destroy(solution, sensors):
    # Ordino la soluzione per costo del dispositivo decrescente
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


def repair(destroyed_solution, sensori_scoperti, gateways, sensors):
    sens_dict = calcola_scenario(sensori_scoperti, gateways)
    new_solution, new_cost = greedy_optimization(sensori_scoperti, gateways, sens_dict)
    # Unisco la soluzione distrutta e il pezzo appena riparato
    repaired_solution = destroyed_solution.copy()
    for a_gateway in new_solution.keys():
        index = max(repaired_solution.keys()) + 1
        repaired_solution[index] = new_solution[a_gateway]

    ammissibile, reason = controlla_ammisibilita(repaired_solution, sensors)
    if not ammissibile:
        print("Questa soluzione NON è ammissibile!!! "+reason)

    return repaired_solution


# Ricerca Locale tramite Destroy and Repair
def large_neighborhood_search(initial_solution, gateways, sensors):
    soluzione_corrente = initial_solution
    migliore_soluzione = soluzione_corrente  # Ottimo candidato (migliore finora)
    costo_migliore_soluzione = costo(soluzione_corrente)
    k = 0
    while k < 10:  # Per ora la StopCondition è fare "n" iterazioni
        print(f"--------RICERCA LOCALE: ITERAZIONE {k}--------")
        destroyed_solution, sensori_scoperti, classe_gateway_tolti = destroy(soluzione_corrente, sensors)
        # Aggiungo al listino i gateway che ho rimosso con la destroy
        for a_gateway in classe_gateway_tolti:
            gateways.append(get_gateways_classes()[a_gateway])
        gateways = sorted(gateways, key=lambda item: item.costo, reverse=False)

        soluzione_corrente = repair(destroyed_solution, sensori_scoperti, gateways, sensors)

        # Per ora non consideriamo la funzione "accept"
        # if accept(new_solution, soluzione_corrente):
        #     soluzione_corrente = new_solution
        #     k += 1
        costo_soluzione_corrente = costo(soluzione_corrente)
        stringa = "Attuale" if costo_soluzione_corrente < costo_migliore_soluzione else "Migliore"
        print(f"Migliore: {round(costo_migliore_soluzione)} | Attuale: {round(costo_soluzione_corrente)} | "
              f"Scelgo {stringa}")
        if costo_soluzione_corrente < costo_migliore_soluzione:
            migliore_soluzione = soluzione_corrente
            costo_migliore_soluzione = costo_soluzione_corrente

        k += 1

    return migliore_soluzione
