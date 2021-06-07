from utility_functions import distance


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
        # if more_verbose:
        #     print("\nIl sensore " + str(this_sens.id) + " è nel raggio di " + str(num_sensori) + " sensori," +
        #           " che hanno una capacità totale di " + str(tot_capacita) + " " + this_sens.send_rate_unit)

    return {k: v for k, v in sorted(sens_dictionary.items(),
                                    key=lambda item: item[1][order_by],
                                    reverse=True)}
