import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scipy import stats

def distribuition(graph, name, g):
    vertex_weights = {node: 0 for node in graph.nodes}
    
    for edge in graph.edges():
        vertex_weights[edge[0]] += graph[edge[0]][edge[1]]['weight']
        vertex_weights[edge[1]] += graph[edge[0]][edge[1]]['weight']
    
    sum_weights = list(vertex_weights.values())
    
    thresholds = [data['threshold'] for node, data in graph.nodes(data=True)]

    def add_normal_curve(ax, data, color):
        mu, std = np.mean(data), np.std(data)
        xmin, xmax = ax.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        p = stats.norm.pdf(x, mu, std)
        n, bins, _ = ax.hist(data, bins=20, edgecolor='black', alpha=0) 
        bin_width = bins[1] - bins[0]
        ax.plot(x, p * bin_width * len(data), color=color, linewidth=2)

    fig, axs = plt.subplots(2, 1, figsize=(8, 8))

    axs[0].hist(sum_weights, bins=20, edgecolor='black', color='skyblue', alpha=0.6)
    axs[0].set_title(f'Distribuição das influências - {name}')
    axs[0].set_xlabel('Influência cumulativa aplicada em um vértice')
    axs[0].set_ylabel('Frequência')
    axs[0].set_xlim(0, 1) 
    add_normal_curve(axs[0], sum_weights, 'red')

    axs[1].hist(thresholds, bins=20, edgecolor='black', color='lightgreen', alpha=0.6)
    axs[1].set_title(f'Distribuição dos Thresholds - {name}')
    axs[1].set_xlabel('Threshold')
    axs[1].set_ylabel('Frequência')
    axs[1].set_xlim(0, 1) 
    add_normal_curve(axs[1], thresholds, 'blue')

    plt.tight_layout()
    plt.savefig(f'results/distribuicao_{g}.jpeg', format='png')
    plt.show()

if __name__ == '__main__':
    g = ["SA_GD", "SA_GP", "SG_GD", "SG_GP"]

    for x in g:
        graph = nx.read_gml(f'dataset/grafos/graph_{x}.gml')
        distribuition(graph, f'Peso = {x[0] + x[1]}; Threshold = {x[3] + x[4]}', x)
    
    graph = nx.read_gml(f'dataset/grafos/graph_generic.gml')
    distribuition(graph, f'Peso = Média do grau; Threshold = Aleatório', "generica")
