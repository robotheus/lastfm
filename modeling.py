import networkx as nx
import random
import matplotlib.pyplot as plt

uat = {}
tag_id = {}
au_n = {}
all_gens = None

with open("dataset/dados/artist_tag_id.txt", "r", encoding='iso-8859-1') as file_artists:
    content = file_artists.readlines()

    for line in content:
        data = line.strip().split(",")
        tag_id[data[2]] = data[1]
    
    all_gens = set(tag_id.values())
    #{'0': 'rock', '1': 'rock', '2': 'electronic', '3': 'pop', '4': 'rap-hiphop'...}

with open("dataset/dados/user_artist_totalistening_periodlength.txt", "r") as file_listening:
    content = file_listening.readlines()

    for line in content:
        data = line.strip().split("::")
        
        if data[0] not in uat:
            uat[data[0]] = [(data[1], tag_id[data[1]], data[2])]
        else:
            uat[data[0]].append((data[1], tag_id[data[1]], data[2]))

        #'39258': [('266', 'electronic', '26'), ('182', 'electronic', '26')]
        # user: [artist, genre, number_listened]

        au_n[(data[1], data[0])] = data[2]
        #(266, 39258) = 26

#SA E SG DEFINEM PESO
def gender_similarity(graph):
    SG = {}
    num_simi = []

    for edge in graph.edges():
        gen_source = []
        gen_target = []

        info_source = uat[edge[0]]
        info_target = uat[edge[1]]
        
        for info in info_source:
            gen_source.append(info[1])
        
        for info in info_target:
            gen_target.append(info[1])

        set_aux_1 = set(gen_source)
        set_aux_2 = set(gen_target)

        TG = len(set_aux_1.union(set_aux_2))
        IG = len(set_aux_1.intersection(set_aux_2))
        
        if IG == 0:
            num_simi.append(edge)

        SG[edge] = IG/TG
        
    c = 0
    for edge in num_simi:
        if graph.degree(edge[0]) <= 1:
            c += 1
        
        if graph.degree(edge[1]) <= 1:
            c += 1

        # ('956', '58499'): 0.5
        # edge: similaridade de genero
    
    print(str(len(SG) - len(num_simi)) + ' arestas possuem SG')
    print(str(c) + ' não possuem outras conexões')   

    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = SG[edge]

    return graph

def artist_similarity(graph):
    SA = {}
    num_simi = {}
    g_um = []

    for edge in graph.edges():
        num_sim = 0
        den_sim = 0

        art_source = []
        art_target = []

        info_source = uat[edge[0]]
        info_target = uat[edge[1]]

        for info in info_source:
            art_source.append(info[0])
        
        for info in info_target:
            art_target.append(info[0])

        set_aux_1 = set(art_source)
        set_aux_2 = set(art_target)
        intersection_artist = set_aux_1.intersection(set_aux_2)
        
        if len(intersection_artist) > 0:
            num_simi[edge] = len(intersection_artist)
            for artist in intersection_artist:
                num_sim += min(float(au_n[(artist, edge[0])]), float(au_n[(artist, edge[1])]))
                den_sim += max(float(au_n[(artist, edge[0])]), float(au_n[(artist, edge[1])]))
                
                s = num_sim/den_sim
                if edge not in SA:
                    SA[edge] = s
                else:
                    SA[edge] += s
        else:
            SA[edge] = 0
    
    for edge in SA:
        if edge in num_simi:
            SA[edge] = (SA[edge] / num_simi[edge])

    for edge in SA:
        if edge not in num_simi:
            if graph.degree(edge[0]) <= 1:
                g_um.append(edge[0])
            
            if graph.degree(edge[1]) <= 1:
                g_um.append(edge[1])
    
    print(str(len(num_simi)) + ' arestas possuem SA')
    print(str(len(g_um)) + ' vértices não possuem outras conexões')

    # ('956', '58499'): 0.5
    # edge: similaridade de artista
    
    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = SA[edge]
    
    return graph

#GD E GP definem threshold
def gender_diversity(graph):
    user_div_gen = {}
    threshold = {}
    
    for user in uat:
        gen_listened = []

        for tupla in uat[user]:
            gen_listened.append(tupla[1])
        
        gen_listened = set(gen_listened)

        user_div_gen[user] = (1 - (len(gen_listened)/len(all_gens)))

    for user in uat:
        threshold[user] = user_div_gen[user]

    for node in graph.nodes():
        graph.nodes[node]['threshold'] = threshold[node]

    return graph

def gender_popularity(graph):
    pop_genres = {}
    threshold = {}

    for user in uat:
        for x in uat[user]:
            if x[1] not in pop_genres:
                pop_genres[x[1]] = int(x[2])
            else:
                pop_genres[x[1]] += int(x[2])
    
    sum = 0
    for value in pop_genres.values():
        sum += value

    for genre in pop_genres:
        pop_genres[genre] = (pop_genres[genre]/sum)
    
    for user in uat:
        generos = []
        u = 0
        
        for x in uat[user]:
            generos.append(x[1])
    
        generos_set = set(generos)

        for genero in generos_set:
        	u += pop_genres[genero]

        threshold[user] = 1 - u

    for node in graph.nodes():
        graph.nodes[node]['threshold'] = threshold[node]

    return graph

def clear(graph):
    s_atv = []
    
    for node in graph.nodes():
        if node not in uat:
            s_atv.append(node)
    
    for node in s_atv:
        graph.remove_node(node)
    
    isolates = list(nx.isolates(graph))

    for node in isolates:
        graph.remove_node(node)

    return graph

def generic(graph):
    degrees = dict(graph.degree()) 

    for edge in graph.edges():
        g1 = degrees[edge[0]]  
        g2 = degrees[edge[1]]  

        graph[edge[0]][edge[1]]['weight'] = 1 / ((g1 + g2) / 2)

    for node in graph.nodes():
        graph.nodes[node]['threshold'] = random.random()  # Correção na atribuição dos valores

    return graph

def normalize(graph):
    vertex_weights = {node: 0 for node in graph.nodes}
    
    for edge in graph.edges():
        vertex_weights[edge[1]] += graph[edge[0]][edge[1]]['weight'] 
        vertex_weights[edge[0]] += graph[edge[0]][edge[1]]['weight']

    for edge in graph.edges():
        u, v = edge
        if vertex_weights[v] > 1:
            graph[u][v]['weight'] = graph[u][v]['weight'] / vertex_weights[v]
        
        if vertex_weights[u] > 1:
            graph[u][v]['weight'] = graph[u][v]['weight'] / vertex_weights[u]

    return graph
    
if __name__ == '__main__':
    graph_origin = nx.read_gml("dataset/grafos/network.gml")
    print(graph_origin)

    print("----------------------------SA_GD--------------------------------")
    clear(graph_origin)
    graph_SA_GD = artist_similarity(graph_origin)
    graph_SA_GD = gender_diversity(graph_SA_GD)
    graph_SA_GD = normalize(graph_SA_GD)
    nx.write_gml(graph_SA_GD, "dataset/grafos/graph_SA_GD.gml")
    print(graph_SA_GD)
    
    
    print("----------------------------SA_GP--------------------------------")
    graph_origin = nx.read_gml("dataset/grafos/network.gml")
    clear(graph_origin)
    graph_SA_GP = artist_similarity(graph_origin)
    graph_SA_GP = gender_popularity(graph_SA_GP)
    graph_SA_GP = normalize(graph_SA_GP)
    nx.write_gml(graph_SA_GP, "dataset/grafos/graph_SA_GP.gml")
    print(graph_SA_GP)
    
    
    print("----------------------------SG_GD--------------------------------")
    graph_origin = nx.read_gml("dataset/grafos/network.gml")
    clear(graph_origin)
    graph_SG_GD = gender_similarity(graph_origin)
    graph_SG_GD = gender_diversity(graph_SG_GD)
    graph_SG_GD = normalize(graph_SG_GD)
    nx.write_gml(graph_SG_GD, "dataset/grafos/graph_SG_GD.gml")
    print(graph_SG_GD)
    
    
    print("----------------------------SG_GP--------------------------------")
    graph_origin = nx.read_gml("dataset/grafos/network.gml")
    clear(graph_origin)
    graph_SG_GP = gender_similarity(graph_origin)
    graph_SG_GP = gender_popularity(graph_SG_GP)
    graph_SG_GP = normalize(graph_SG_GP)
    nx.write_gml(graph_SG_GP, "dataset/grafos/graph_SG_GP.gml")
    print(graph_SG_GP)
    
    
    print("----------------------------Gener--------------------------------")
    graph_origin = nx.read_gml("dataset/grafos/network.gml")
    clear(graph_origin)
    graph_generic = generic(graph_origin)
    nx.write_gml(graph_generic, "dataset/grafos/graph_generic.gml")
    print(graph_generic)
    
