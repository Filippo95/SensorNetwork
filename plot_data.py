import matplotlib.pyplot as plt
import os


# Struttura:
#  0        1        2        3       4             5          6        7          8            9             10
# seed,numsensori,order_by,pack_by,num_iter_ls,greedy_cost,mst_cost,first_tot,first_ls_tot,second_ls_tot,num_gw_class_1

# S=seed
# O=0 -> order_by = rapp_cap_costo
# O=1 -> order_by = rapp_numsensori_costo
# P=0 -> pack_by = distanza_capacita
# P=1 -> pack_by = capacita

def plot(save_directory, num_sensori):
    x_values = []
    y_values = []
    y_values_2 = []
    y_values_3 = []

    with open("./solutions/graph_data.csv", "r") as f:
        instestazione = f.readline()
        a_line = f.readline()
        while a_line != "":
            items = a_line.split(",")
            if items[1] == str(num_sensori):
                seed = f"S={items[0]}"
                order_by = "O=0" if items[2] == "rapp_cap_costo" else "O=1"
                pack_by = "P=0" if items[3] == "distanza_capacita" else "P=1"
                x_values.append(f"{seed},{order_by},{pack_by}")
                y_values.append(int(items[9]))  # second_ls_tot
                y_values_2.append(int(items[8]))  # first_ls_tot
                y_values_3.append(int(items[7]))  # first_tot
            a_line = f.readline()

    fig, ax = plt.subplots()

    ax.bar(x_values, y_values, label="Dopo la seconda ricerca locale", zorder=2, facecolor="#4895EF")
    ax.bar(x_values, y_values_2, label="Dopo la prima ricerca locale", zorder=1, facecolor="#560BAD")
    ax.bar(x_values, y_values_3, label="Prima della ricerca locale", zorder=0, facecolor="#B5179E")
    ax.legend()
    ax.set_ylabel('Costo')
    ax.set_title(f'{num_sensori} Sensori\n'
                 f'O=0 -> order_by = rapp_cap_costo | '
                 f'O=1 -> order_by = rapp_numsensori_costo | '
                 f'P=0 -> pack_by = distanza_capacita | '
                 f'P=1 -> pack_by = capacita')
    plt.xticks(rotation=90, fontsize=10)

    figure = plt.gcf()
    figure.set_size_inches(32, 18)
    plt.savefig(f"{save_directory}{num_sensori}", bbox_inches='tight')


if __name__ == "__main__":
    save_dir = "./plots/"
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    # plot(save_dir, 100)
    # plot(save_dir, 200)
    # plot(save_dir, 300)
    plot(save_dir, 400)
    # plot(save_dir, 500)
    # plot(save_dir, 600)
