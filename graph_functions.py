from utility_functions import distance_by_coord


def find_reachable_vertices(edge_list, a_vertex):
    reachable_vertices = []
    for edge in edge_list:
        if edge["node_one"] == a_vertex:
            reachable_vertices.append(edge["node_two"])
        elif edge["node_two"] == a_vertex:
            reachable_vertices.append(edge["node_one"])
    return reachable_vertices


def depth_first_visit(edge_list, this_vertex, visited_vertices, opened_vertices, vertices_left):
    visited_vertices.append(this_vertex)
    vertices_left.remove(this_vertex["vertex"])

    # Trovo i vertici raggiungibili partendo dal vertice attuale
    vertici_raggiungibili = find_reachable_vertices(edge_list, this_vertex["vertex"])
    # Per ogni vertice raggiungibile, se non è già stato aperto e se non è il genitore di questo vertice,
    # lo aggiungo in testa alla lista dei vertici aperti
    temp_vertex_list = [item["vertex"] for item in opened_vertices]
    for a_vertex in vertici_raggiungibili:
        if a_vertex not in temp_vertex_list and a_vertex != this_vertex["parent"]:
            opened_vertices.insert(0, {
                "vertex": a_vertex,
                "parent": this_vertex["vertex"]
            })

    # Verifico se fra i vertici raggiungibili (a parte il parent, che non viene inserito)
    # c'è uno dei vertici già visitati, se ciò è verificato, allora ho trovato un ciclo
    temp_vertex_list = [item["vertex"] for item in opened_vertices]
    visited_vertices_list = [item["vertex"] for item in visited_vertices]
    for a_vertex in temp_vertex_list:
        if a_vertex in visited_vertices_list:
            return True

    # Sennò proseguo la visita in profondità.

    # Può darsi che la lista di vertici aperti sia nulla, ad esempio in casi in cui ho
    # selezionato due archi che collegano due coppie di vertici diversi. Quindi devo controllare se
    # la lista dei vertici aperti è vuota, e in quel caso effettuare una nuova visita.
    if len(opened_vertices) > 0:
        next_vertex = opened_vertices[0]
        opened_vertices.pop(0)
    else:
        # Se sono riuscito a visitare tutti i nodi del grafo, non ho trovato nessun ciclo
        if len(vertices_left) == 0:
            return False
        next_vertex = {
            "vertex": vertices_left[0],
            "parent": None
        }
    return depth_first_visit(edge_list, next_vertex, visited_vertices, opened_vertices, vertices_left)


def ha_cicli(edge_list):
    vertices_to_visit = []
    for an_edge in edge_list:
        n1 = an_edge["node_one"]
        n2 = an_edge["node_two"]
        if n1 not in vertices_to_visit:
            vertices_to_visit.append(n1)
        if n2 not in vertices_to_visit:
            vertices_to_visit.append(n2)
    starting_vertex = {
        "vertex": edge_list[0]["node_one"],
        "parent": None
    }

    return depth_first_visit(edge_list, starting_vertex, [], [], vertices_to_visit)


def esiste_arco(edges, node_one, node_two):
    for item in edges:
        if (item["node_one"] == node_one and item["node_two"] == node_two) or \
                (item["node_one"] == node_two and item["node_two"] == node_one):
            return True
    return False


def minimum_spanning_tree(result):
    # Costruisco il grafo dei dispositivi, che è un grafo
    # completamente connesso i cui nodi rappresentano i dispositivi
    vertices = []  # i nodi del grafo
    edges = []  # gli archi del grafo

    for gateway in result:
        vertices.append(gateway)
        temp_result = result.copy()  # creo una copia del dizionario
        temp_result.pop(gateway)  # e ne elimino l'elemento attuale
        for node in temp_result:
            if not esiste_arco(edges, gateway, node):  # se non esiste già l'arco che connette il gateway attuale
                # con il nodo attuale (cioè qualsiasi altro gateway), lo aggiungo al grafo (senza questo check avrei
                # un multigrafo, noi invece vogliamo creare un grafo semplice)
                edges.append({
                    "node_one": gateway,
                    "node_two": node,
                    "costo": distance_by_coord((result.get(gateway)['latitudine'],  # Vengono passate delle tuple
                                                result.get(gateway)['longitudine']),  # di coordinate
                                               (result.get(node)['latitudine'],
                                                result.get(node)['longitudine']))  # * rn.uniform(0.75, 1.25)
                    # La funzione costo è proporzionale alla distanza fra i due dispositivi,
                    # ma moltiplicata per un fattore casuale (per fare in modo che non dipenda
                    # esclusivamente dalla distanza)
                })

    # Algoritmo di Kruskal:
    # 1) Seleziono l'arco di costo minimo fra quelli non ancora considerati e lo aggiungo alla soluzione
    # 2) Se il grafo risultante contiene un ciclo lo rimuovo dalla soluzione e continuo
    # 3) Se il grafo, invece, è aciclico, lo mantengo nella soluzione e continuo
    # 4) Mi fermo se ho esaminato tutti gli archi o se len(soluzione) == n-1 (numero di vertici, o nodi, -1)

    # ordino gli archi per costo
    edges = sorted(edges,
                   key=lambda item: item["costo"],
                   reverse=False)  # dal più basso al più alto
    print(edges)
    # creo un array che contiene gli archi che ho selezionato
    selected = []
    while len(edges) > 0 and len(selected) < len(vertices) - 1:
        # aggiungo l'arco alla soluzione (il primo elemento di edges
        # è sempre quello con costo minore)
        selected.append(edges[0])
        # verifico che il grafo attuale non contenga cicli
        # Devo passare una copia del dizionario "selected" o la
        # funzione modifica il dizionario originale
        selected_copy = selected.copy()
        if ha_cicli(selected_copy):
            # ha cicli, quindi lo rimuovo
            selected.pop(-1)
        # in ogni caso, elimino l'arco appena considerato
        edges.pop(0)

    # Stampo gli archi selezionati
    print("Archi selezionati per il MST:")
    for selected_edge in selected:
        print("{} - {} - {}".format(selected_edge["node_one"], selected_edge["node_two"], selected_edge["costo"]))
    return selected
