import matplotlib.pyplot as plt
from operator import add
import os


# Struttura:
# seed,numsensori,order_by,pack_by,num_iter_ls,first_greedy,first_mst,first_tot,ls_greedy,ls_mst,ls_tot,risparmio,num_gw_class_1

def plot(save_directory, num_sensori):
    x_values = []
    y_values = []
    y_values_2 = []

    with open("./solutions/graph_data.csv", "r") as f:
        instestazione = f.readline()
        a_line = f.readline()
        while a_line != "":
            items = a_line.split(",")
            if items[1] == str(num_sensori):
                x_values.append(f"Seed: {items[0]}\n{items[2]}\n{items[3]}")
                y_values.append(int(items[10]))
                y_values_2.append(int(items[7]) - int(items[10]))
            a_line = f.readline()

    fig, ax = plt.subplots()

    ax.bar(x_values, y_values, label="Dopo la ricerca locale")
    ax.bar(x_values, y_values_2, bottom=y_values, label="Prima della ricerca locale")
    ax.legend()
    ax.set_ylabel('Costo')
    ax.set_title(f'{num_sensori} Sensori')
    ax.set_ylim(0, max(map(add, y_values, y_values_2)) + 300)
    plt.xticks(rotation=45, fontsize=8)

    figure = plt.gcf()
    figure.set_size_inches(32, 18)
    plt.savefig(f"{save_directory}{num_sensori}", bbox_inches='tight')


if __name__ == "__main__":
    save_dir = "./plots/"
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    plot(save_dir, 100)
    plot(save_dir, 200)
    plot(save_dir, 300)
    plot(save_dir, 400)
    plot(save_dir, 500)
