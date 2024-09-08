import networkx as nx
import random
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import json
from concurrent.futures import ProcessPoolExecutor, as_completed

population_size = 49                    # numero de cromossomos #50
num_seeds = [50, 60, 70, 80, 90, 100]   # quantidade de genes/tamanho das sementes
mutation_rate = 0.1
tournament_size = 2
generations = 100                    

def initialize_population(graph, population_size, num_seeds):

    population = {}
    nodes = list(graph.nodes)
    
    for i in range(population_size):
        individual = random.sample(nodes, num_seeds)
        population[i] = individual
    
    degree = nx.degree_centrality(graph)
    top = sorted(degree.items(), key=lambda item: item[1], reverse=True)[:num_seeds]
    
    i = []
    for seed in top:
        i.append(seed[0])
    
    population[50] = i
    
    return population

def evaluate_individual(individual, population, graph):
    model = ep.ThresholdModel(graph)
    config = mc.Configuration()

    config.add_model_initial_configuration("Infected", population[individual])
    
    for node in graph.nodes():
        config.add_node_configuration("threshold", node, thresholds[node])
    
    model.set_initial_status(config)

    iterations = model.iteration_bunch(100)
    best_value = 0

    for x in iterations:
        if x['node_count'][1] > best_value:
            best_value = x['node_count'][1]
    
    return individual, best_value

def fitness(population, graph):
    fit_values = {}
    with ProcessPoolExecutor() as executor:
        future_to_individual = {
            executor.submit(evaluate_individual, individual, population, graph): individual
            for individual in population
        }

        for future in as_completed(future_to_individual):
            individual, best_value = future.result()
            fit_values[individual] = best_value
    
    return fit_values

def one_point_crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    
    return child1, child2

def mutate(graph, individual):
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            available_nodes = list(set(graph.nodes()) - set(individual))
            if available_nodes:
                individual[i] = random.choice(available_nodes)
    
    return individual

def elitism(population, population_fitness):
    sorted_population = sorted(population.keys(), key=lambda ind: population_fitness[ind], reverse=True)
    best_individuals = sorted_population[:2]
    
    return [population[ind] for ind in best_individuals]

def tournament_selection(population, population_fitness):
    selected_individuals = {}

    elite_individuals = elitism(population, population_fitness)

    for i in range(0, len(population) - 2, 2):
        tournament_1 = random.sample(list(population.keys()), tournament_size)
        tournament_2 = random.sample(list(population.keys()), tournament_size)

        tournament_fitness_1 = {key: population_fitness[key] for key in tournament_1}
        tournament_fitness_2 = {key: population_fitness[key] for key in tournament_2}
        
        winner_key_1 = max(tournament_fitness_1, key=tournament_fitness_1.get)
        winner_key_2 = max(tournament_fitness_2, key=tournament_fitness_2.get)

        parent1 = population[winner_key_1]
        parent2 = population[winner_key_2]
        
        child1, child2 = one_point_crossover(parent1, parent2)

        child1 = mutate(graph, child1)
        child2 = mutate(graph, child2)
        
        selected_individuals[i] = child1
        if i + 1 < len(population) - 2:
            selected_individuals[i + 1] = child2

    selected_individuals[len(population) - 2] = elite_individuals[0]
    selected_individuals[len(population) - 1] = elite_individuals[1]
    
    return selected_individuals

if __name__ == '__main__':

    list_graphs = ['SG_GP', 'SA_GP']

    for graph_name in list_graphs:
        graph = nx.read_gml(f'dataset/grafos/graph_{graph_name}.gml')
        thresholds = {node: graph.nodes[node]['threshold'] for node in graph.nodes()}
        for seed in num_seeds:
            for x in range(10):
                population = initialize_population(graph, population_size, seed)
                population_fitness = fitness(population, graph)

                best_anterior = 0
                best_atual = 0
                count = 0

                for generation in range(generations):
                    best_anterior = best_atual
                    best_atual = max(population_fitness.values())
                    
                    print(f'Geração {generation}: Melhor aptidão = {max(population_fitness.values())}')
                    
                    population = tournament_selection(population, population_fitness)
                    population_fitness = fitness(population, graph)

                    if best_anterior == best_atual:
                        count += 1

                        if count > 10:
                            print(f'Encerrada na geração {generation} por não evoluir em 10 gerações.')
                            break
                    else:
                        count = 0

                with open(f'results/diffusions/pop_{graph_name}_{seed}_{str(x+1)}.json', "w") as file1:
                    json.dump(population, file1)
                
                with open(f'results/diffusions/fit_{graph_name}_{seed}_{str(x+1)}.json', "w") as file2:
                    json.dump(population_fitness, file2)
