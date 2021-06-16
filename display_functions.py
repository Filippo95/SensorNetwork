import folium
import random as rn
from matplotlib import pyplot as plt
from deprecated import deprecated
from utility_functions import get_verbosity, find_sensor_by_id


# Inutilizzato.
# Metodo creato in origine per plottare il nostro scenario, ora si
# utilizza la rappresentazione tramite mappa (pacchetto folium).
# I raggi dei sensori non saranno disegnati correttamente.
@deprecated(reason="Utilizzare il metodo display_solution()")
def plot_graph_old(min_x, max_x, min_y, max_y, sensors):
    x = []
    y = []
    colors = []
    labels = []
    color_map_name = "viridis"
    num_sensori = len(sensors)

    ax = plt.axes(xlim=(min_x, max_x), ylim=(min_y, max_y))
    for index, a_sens in enumerate(sensors):
        x.append(a_sens.longitudine)
        y.append(a_sens.latitudine)

        radius = a_sens.portata

        colors.append(a_sens.id)

        if get_verbosity().verbose:
            center = "center: x={} y={}".format(round(a_sens.longitudine), round(a_sens.latitudine))
            coords = "range: x={}-{} | y={}-{}".format(round(a_sens.longitudine - radius),
                                                       round(a_sens.longitudine + radius),
                                                       round(a_sens.latitudine - radius),
                                                       round(a_sens.latitudine + radius))
            labels.append("id={} r={}\n{}\n{}".format(a_sens.id, round(radius), center, coords))
        elif get_verbosity().quiet:
            labels.append("{}".format(a_sens.id))
        else:
            labels.append("id:{} r={}".format(a_sens.id, round(radius)))

        ax.add_artist(plt.Circle((a_sens.longitudine, a_sens.latitudine), radius,
                                 color=plt.cm.get_cmap(color_map_name).colors[index * round(256 / num_sensori)],
                                 fill=True, alpha=0.5))  # Disegna i raggi dei sensori

    ax.scatter(x, y, c=colors, s=5, cmap=color_map_name, alpha=1.0)  # Disegna i centri dei sensori

    for x_pos, y_pos, label in zip(x, y, labels):
        ax.annotate(label, xy=(x_pos, y_pos), xytext=(7, 0), textcoords='offset points',
                    ha='left', va='center')

    ax.set_aspect('equal', anchor="C")
    ax.set_xbound(lower=min_x, upper=max_x)
    ax.set_ybound(lower=min_y, upper=max_y)
    plt.grid()
    plt.show()


def display_sensors(sensors, dest_folder="./"):
    m = folium.Map(location=[44.50, 11], tiles="OpenStreetMap", zoom_start=8.5)

    for i in range(len(sensors)):
        temp_sensor = sensors[i]
        folium.Circle(
            location=(temp_sensor.latitudine, temp_sensor.longitudine),
            popup='id: ' + str(temp_sensor.id) + 'lat: ' + str(temp_sensor.latitudine) + 'long: ' + str(
                temp_sensor.longitudine),
            radius=float(temp_sensor.portata),
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)
    m.save(dest_folder + '1-sensors.html')


def display_solution(solution, dest_folder="./"):
    color_palette = ["#F72585", "#B5179E", "#7209B7", "#560BAD", "#480CA8",
                     "#3A0CA3", "#3F37C9", "#4361EE", "#4895EF", "#4CC9F0"]

    m = folium.Map(location=[44.50, 11], tiles="OpenStreetMap", zoom_start=8.5)
    for gateway in solution:
        color = rn.choice(color_palette)
        folium.Marker(
            location=[solution.get(gateway)['latitudine'], solution.get(gateway)['longitudine']],
            popup='id: ' + str(solution.get(gateway)['sensor_id']) +
                  ' latitudine: ' + str(solution.get(gateway)['latitudine']) +
                  ' longitudine: ' + str(solution.get(gateway)['longitudine']) +
                  ' sensori coperti: ' + str(solution.get(gateway)['sensor_covered']),
        ).add_to(m)
        for sensor in solution.get(gateway)['sensor_covered']:
            sensore = find_sensor_by_id(sensor)
            folium.Circle(
                location=(sensore.latitudine, sensore.longitudine),
                popup='id: ' + str(sensore.id) + ' lat: ' + str(sensore.latitudine) + ' long: ' + str(
                    sensore.longitudine),
                radius=float(sensore.portata),
                color=color,
                labels=str(sensore.id),
                fill=True,
                fill_color=color
            ).add_to(m)

    m.save(dest_folder + '2-greedy.html')


def display_mst(tree, soluzione, dest_folder="./"):
    mst_color = "#F72585"

    m = folium.Map(location=[44.50, 11], tiles="OpenStreetMap", zoom_start=8.5)

    for index, gateway in enumerate(soluzione):
        folium.Marker(
            location=[soluzione.get(gateway)['latitudine'], soluzione.get(gateway)['longitudine']],
            icon=folium.DivIcon(
                html=f"""<div style=" font-weight: bold; font-size: large;">{"{:.0f}".format(index)}</div>"""),
            popup='id: ' + str(index) + '<br>'
                                        ' latitudine: ' + str(soluzione.get(gateway)['latitudine']) +
                  ' longitudine: ' + str(soluzione.get(gateway)['longitudine']) +
                  ' sensori coperti: ' + str(soluzione.get(gateway)['sensor_covered']),
        ).add_to(m)

    for arco in tree:
        id_gateway1 = arco["node_one"]
        id_gateway2 = arco["node_two"]
        gateway1 = soluzione[id_gateway1]
        gateway2 = soluzione[id_gateway2]
        loc = [(gateway1["latitudine"], gateway1["longitudine"]),
               (gateway2["latitudine"], gateway2["longitudine"])]

        folium.PolyLine(loc,
                        color=mst_color,
                        weight=5,
                        opacity=0.8).add_to(m)

    m.save(dest_folder + '/3-mst.html')


def display_full_solution(tree, soluzione, dest_folder="./"):
    mst_color = "#4CC9F0"
    color_palette = ["#F72585", "#B5179E", "#7209B7", "#560BAD", "#480CA8",
                     "#3A0CA3", "#3F37C9", "#4361EE", "#4895EF"]

    m = folium.Map(location=[44.50, 11], tiles="OpenStreetMap", zoom_start=8.5)

    for index, gateway in enumerate(soluzione):
        folium.Marker(
            location=[soluzione.get(gateway)['latitudine'], soluzione.get(gateway)['longitudine']],
            icon=folium.DivIcon(
                html=f"""<div style=" font-weight: bold; font-size: large;">{"{:.0f}".format(index)}</div>"""),
            popup='id: ' + str(index) + '<br>'
                                        ' latitudine: ' + str(soluzione.get(gateway)['latitudine']) +
                  ' longitudine: ' + str(soluzione.get(gateway)['longitudine']) +
                  ' sensori coperti: ' + str(soluzione.get(gateway)['sensor_covered']),
        ).add_to(m)

    for arco in tree:
        id_gateway1 = arco["node_one"]
        id_gateway2 = arco["node_two"]
        gateway1 = soluzione[id_gateway1]
        gateway2 = soluzione[id_gateway2]
        loc = [(gateway1["latitudine"], gateway1["longitudine"]),
               (gateway2["latitudine"], gateway2["longitudine"])]

        folium.PolyLine(loc,
                        color=mst_color,
                        weight=5,
                        opacity=0.8).add_to(m)

    for gateway in soluzione:
        sensor_color = rn.choice(color_palette)
        for sensor in soluzione.get(gateway)['sensor_covered']:
            sensore = find_sensor_by_id(sensor)
            folium.Circle(
                location=(sensore.latitudine, sensore.longitudine),
                popup='id: ' + str(sensore.id) + ' lat: ' + str(sensore.latitudine) + ' long: ' + str(
                    sensore.longitudine),
                radius=float(500),
                color=sensor_color,
                labels=str(sensore.id),
                fill=True,
                fill_color=sensor_color
            ).add_to(m)
            loc = [(soluzione.get(gateway)["latitudine"], soluzione.get(gateway)["longitudine"]),
                   (sensore.latitudine, sensore.longitudine)]

            folium.PolyLine(loc,
                            color=sensor_color,
                            weight=2,
                            opacity=0.8).add_to(m)

    m.save(dest_folder + '4-full.html')


def display_difference_between_solutions(nuova_soluzione, mst_new, vecchia_sol, mst_old, dest_folder):
    mst_color = "#b70909"  # rosso
    color = "#b70909"

    mst_new_color = "#095ab7"  # blu
    color_new = "#095ab7"

    m = folium.Map(location=[44.50, 11], tiles="OpenStreetMap", zoom_start=8.5)

    for index, gateway in enumerate(nuova_soluzione):
        folium.Marker(
            location=[nuova_soluzione.get(gateway)['latitudine'], nuova_soluzione.get(gateway)['longitudine']],
            icon=folium.DivIcon(
                html=f"""<div style=" font-weight: bold; font-size: large;">{"{:.0f}".format(index)}</div>"""),
            popup='id: ' + str(index) + '<br>'
                                        ' latitudine: ' + str(nuova_soluzione.get(gateway)['latitudine']) +
                  ' longitudine: ' + str(nuova_soluzione.get(gateway)['longitudine']) +
                  ' sensori coperti: ' + str(nuova_soluzione.get(gateway)['sensor_covered']),
        ).add_to(m)

    for arco in mst_new:
        id_gateway1 = arco["node_one"]
        id_gateway2 = arco["node_two"]
        gateway1 = nuova_soluzione[id_gateway1]
        gateway2 = nuova_soluzione[id_gateway2]
        loc = [(gateway1["latitudine"], gateway1["longitudine"]),
               (gateway2["latitudine"], gateway2["longitudine"])]

        folium.PolyLine(loc,
                        color=mst_color,
                        weight=10,
                        opacity=0.5).add_to(m)

    for gateway in nuova_soluzione:
        sensor_color = color
        for sensor in nuova_soluzione.get(gateway)['sensor_covered']:
            sensore = find_sensor_by_id(sensor)
            folium.Circle(
                location=(sensore.latitudine, sensore.longitudine),
                popup='id: ' + str(sensore.id) + ' lat: ' + str(sensore.latitudine) + ' long: ' + str(
                    sensore.longitudine),
                radius=float(500),
                color=sensor_color,
                labels=str(sensore.id),
                fill=True,
                fill_color=sensor_color
            ).add_to(m)
            loc = [(nuova_soluzione.get(gateway)["latitudine"], nuova_soluzione.get(gateway)["longitudine"]),
                   (sensore.latitudine, sensore.longitudine)]

            folium.PolyLine(loc,
                            color=sensor_color,
                            weight=2,
                            opacity=0.8).add_to(m)

    for arco in mst_old:
        id_gateway1 = arco["node_one"]
        id_gateway2 = arco["node_two"]
        gateway1 = vecchia_sol[id_gateway1]
        gateway2 = vecchia_sol[id_gateway2]
        loc = [(gateway1["latitudine"], gateway1["longitudine"]),
               (gateway2["latitudine"], gateway2["longitudine"])]

        folium.PolyLine(loc,
                        color=mst_new_color,
                        weight=10,
                        opacity=0.5).add_to(m)

    for gateway in vecchia_sol:
        sensor_color = color_new
        for sensor in vecchia_sol.get(gateway)['sensor_covered']:
            sensore = find_sensor_by_id(sensor)
            folium.Circle(
                location=(sensore.latitudine, sensore.longitudine),
                popup='id: ' + str(sensore.id) + ' lat: ' + str(sensore.latitudine) + ' long: ' + str(
                    sensore.longitudine),
                radius=float(500),
                color=sensor_color,
                labels=str(sensore.id),
                fill=True,
                fill_color=sensor_color
            ).add_to(m)
            loc = [(vecchia_sol.get(gateway)["latitudine"], vecchia_sol.get(gateway)["longitudine"]),
                   (sensore.latitudine, sensore.longitudine)]

            folium.PolyLine(loc,
                            color=sensor_color,
                            weight=2,
                            opacity=0.5).add_to(m)

    m.save(dest_folder + '5-full-differences.html')
