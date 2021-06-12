import sys
import pprint
from utility_functions import distance, get_verbosity, get_seed, set_verbosity


# Questa funzione, dato un sensore in input, trova tutti i sensori
# che possono trasmettergli dati.
# Viene considerato anche il sensore stesso.
def find_senders(sensor_list, a_sensor):
    senders = []

    for this_sens in sensor_list:
        this_dist = distance(a_sensor, this_sens)
        if this_dist <= this_sens.portata:
            senders.append(this_sens)

    return senders


# Data una capacità da "coprire", trova il
# dispositivo/gateway con costo minore possibile
# che la copra interamente, oppure, se non ne
# esiste uno che possa farlo, restituisce il
# dispositivo con capacità massima
def find_best_gateway(capacita, gateway_list):
    for gw in gateway_list:
        if gw.capacita < capacita:
            pass
        else:
            return gw

    return gateway_list[-1]


def find_covered(sensor, senders, capacita_gateway, find_by="distanza_capacita"):
    selected = []

    for sender in senders:
        if find_by == "capacita":
            sender.criterio = sender.send_rate
        else:
            distanza = distance(sensor, sender)
            if distanza == 0:
                distanza = 0.0001
            sender.criterio = sender.send_rate / distanza  # vogliamo prioritizzare i sensori che hanno
            # raggio molto piccolo e capacità molto grande, quindi quelli più vicini con send_rate più grande

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


# Questa funzione, dato l'array di sensori, crea un dizionario ordinato secondo il parametro order_by.
def calcola_scenario(sensor_list, gateway_list, order_by="rapp_cap_costo"):
    sens_dictionary = {}
    for this_sens in sensor_list:
        this_senders = find_senders(sensor_list, this_sens)
        tot_capacita = 0
        num_senders = len(this_senders)
        for temp_sens in this_senders:
            tot_capacita += temp_sens.send_rate
        rapp_cap_costo = tot_capacita / find_best_gateway(tot_capacita, gateway_list).costo
        rapp_numsensori_costo = num_senders / find_best_gateway(tot_capacita, gateway_list).costo
        sens_dictionary[this_sens] = {"senders": this_senders,
                                      "tot_capacita": tot_capacita,
                                      "rapp_cap_costo": rapp_cap_costo,
                                      "rapp_numsensori_costo": rapp_numsensori_costo}
        if get_verbosity().more_verbose:
            print(f"\nIl sensore {this_sens.id} è nel raggio di {num_senders} sensori, " +
                  f"che hanno una capacità totale di {tot_capacita} {this_sens.send_rate_unit}")

    return {k: v for k, v in sorted(sens_dictionary.items(),
                                    key=lambda item: item[1][order_by],
                                    reverse=True)}


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

        if len(which_covered) == 0:  # Non ho abbastanza dispositivi per coprire tutti i sensori!
            set_verbosity(quiet=True)
            break  # In alcuni casi, il dispositivo di classe 0 non ha sufficiente capacità
            # per coprire un singolo sensore

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
        if not get_verbosity().quiet:
            print("\nITERAZIONE: " + str(i - 1))
            for temp in sensors_copy:
                print(temp.id, end=',')
            print("\n")

        # aggiorno lo scenario dopo l'assegnazione, e dopo aver rimosso quelli già assegnati
        sens_dict_ordered = calcola_scenario(sensors_copy, gateways)

    # Stampo l'utilizzo dei dispositivi per classe
    if not get_verbosity().quiet:
        print("\n\n\n")
        print(f"Sono stati utilizzati:\n"
              f"{utilizzo_gateway[0]} dispositivi di classe 0, costo totale {utilizzo_gateway[0] * 6}\n"
              f"{utilizzo_gateway[1]} dispositivi di classe 1, costo totale {utilizzo_gateway[1] * 14}\n"
              f"{utilizzo_gateway[2]} dispositivi di classe 2, costo totale {utilizzo_gateway[2] * 25}\n"
              f"{utilizzo_gateway[3]} dispositivi di classe 3, costo totale {utilizzo_gateway[3] * 75}\n"
              f"{utilizzo_gateway[4]} dispositivi di classe 4, costo totale {utilizzo_gateway[4] * 175}\n")

    # Stampo il dizionario che mostra dove e quali dispositivi ho installato
    if not get_verbosity().quiet:
        print("\n\n\n")
        pp = pprint.PrettyPrinter(indent=3)
        pp.pprint(selected)

    with open('greedy_output.txt', 'a') as f:
        original_stdout = sys.stdout
        if len(sensors_copy) == 0:
            print("Non sono rimasti sensori da coprire. Il costo della soluzione è " + str(costo_totale))
            sys.stdout = f
            print("SEED: " + str(get_seed()))
            print("Non sono rimasti sensori da coprire. Il costo della soluzione è " + str(costo_totale))
            print("\n")
            sys.stdout = original_stdout
        else:
            sys.stdout = f
            print("SEED: " + str(get_seed()))
            print("Sono rimasti sensori da coprire. Nessuna soluzione ammissibile trovata!")
            print("\n")
            sys.stdout = original_stdout
    return selected, costo_totale
