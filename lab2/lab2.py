import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random

# Constants
V = 20  # Number of vertices in the graph
m = 1500  # Average packet size in bits
T_max = 0.1  # Maximum acceptable average packet delay
initial_p = 0.9 # Probability that an edge is not damaged
trials = 100 # Number of trials for the simulation
steps = 10 # Number of steps for modifying network parameters


class NetworkSimulation:
    def __init__(self, graph):
        """Initialize the network simulation with a given graph and traffic intensity matrix."""
        self.graph = graph  # Network topology
        self.N_matrix = np.zeros((V, V), dtype=int)   # Traffic intensity matrix
        self.a_values = np.zeros((graph.number_of_nodes(), graph.number_of_nodes()), dtype=int)  # Flow on each edge

    def populate_N_matrix(self):
        """Populate the N matrix with random values for existing edges only."""
        for u in range(1, V + 1):
            for v in range(u + 1, V + 1):  # Start from u+1 to avoid self-loops and redundant calculations
                    traffic = random.randint(1, 10)  # Random traffic for this pair
                    self.N_matrix[u - 1][v - 1] = traffic  # Assign traffic from u to v
                    self.N_matrix[v - 1][u - 1] = traffic  # Mirror for v to u since it's undirected


    def compute_a_values(self,graph):
        """Compute flow values (a_values) for each edge based on shortest paths."""
        # Reset a_values to zero
        self.a_values = np.zeros((self.graph.number_of_nodes(), self.graph.number_of_nodes()), dtype=int)

        paths = dict(nx.all_pairs_dijkstra_path(graph))
        for i in range(1, V + 1):
            for j in range(1, V + 1):
                if i != j:
                    path = paths[i][j]
                    flow = self.N_matrix[i - 1][j - 1]  # Adjust index for 0-based array access
                    for k in range(len(path) - 1):
                        u, v = path[k], path[k + 1]
                        self.a_values[u - 1][v - 1] += flow  # Adjust index for 0-based array access
                        self.a_values[v - 1][u - 1] += flow  # Symmetric since the graph is undirected

    def simulate_reliability(self, p, m):
        """Simulate the reliability of the network over multiple trials."""
        count_reliable = 0
        for _ in range(trials):
            damaged_graph = self.graph.copy()
            self.randomly_remove_edges(damaged_graph, p)
            if nx.is_connected(damaged_graph):
                self.compute_a_values(damaged_graph)
                is_not_overloaded = True
                for (i, j) in damaged_graph.edges():
                    a_value = 2*self.a_values[i - 1][j - 1] * m
                    c_value = self.graph[i][j]['c']
                    if a_value > c_value:
                        is_not_overloaded = False
                if is_not_overloaded:
                    T = self.calculate_T(damaged_graph,m)
                    if T < T_max:
                        count_reliable += 1


        return count_reliable / trials

    def randomly_remove_edges(self, graph, probability):
        """Randomly remove edges from the graph based on a given probability."""
        for (i, j) in list(graph.edges()):
            random_ri = random.random()
            if random_ri > probability:
                graph.remove_edge(i, j)


    def calculate_T(self,graph, m):
        """Calculate the average packet delay T across the network."""
        G_value = np.sum(self.N_matrix)
        total_delay = 0
        counter = 0
        self.compute_a_values(graph)
        for (i, j) in graph.edges():
            a = 2*self.a_values[i - 1][j - 1]
            c = graph[i][j]['c']
            if c / m - a <= 0:
                return float('inf')
            total_delay += (a / (c / m - a))
            counter = counter+1
        return total_delay / G_value

    def increase_N_values(self, increment):
        """Incrementally increase the values in the traffic matrix."""
        non_zero_mask = self.N_matrix != 0
        self.N_matrix[non_zero_mask] += increment

    def increase_capacities(self, percentage_increment):
        """Incrementally increase the capacities of all edges in the graph."""
        for (i, j) in self.graph.edges():
            increment_amount = self.graph[i][j]['c'] * percentage_increment / 100
            self.graph[i][j]['c'] += increment_amount
            self.compute_a_values(self.graph)

    def add_random_edges(self, additional_edges_count, mean_capacity):
        """Add new edges with average capacities to modify the network topology."""
        added_edges = 0
        while added_edges < additional_edges_count:
            i, j = np.random.randint(1, V + 1, size=2)
            if i != j and not self.graph.has_edge(i, j):
                self.graph.add_edge(i, j, c=mean_capacity)
                added_edges += 1

    def reset_capacities(graph, initial_capacities):
        """Reset the capacities of all edges to their initial values."""
        for (u, v), capacity in initial_capacities.items():
            graph[u][v]['c'] = capacity

    def average_capacity(self):
        """Calculate the average capacity of all the edges in the graph."""
        total_capacity = sum(self.graph[u][v]['c'] for u, v in self.graph.edges())
        num_edges = self.graph.number_of_edges()
        return total_capacity / num_edges if num_edges > 0 else 0


# Graph setup
G = nx.Graph()
G.add_nodes_from(range(1, V + 1))
base_edges = [
    (1, 2), (2, 3), (3, 4), (4, 5),
    (5, 6), (6, 7), (7, 8), (1, 8),
    (2, 9), (4, 10), (5, 11), (7, 12),
    (9, 10), (10, 11), (11, 12), (12, 9),
    (9, 13), (11, 14), (10, 15), (12, 16),
    (13, 17), (14, 18), (15, 19), (16, 20),
    (17, 18), (18, 19), (19, 20), (20, 17)
]
# Adding edges with individual random capacities
edge_labels = {}
for u, v in base_edges:
    capacity = random.randint(7000000, 10000000)  # Random capacity for each edge
    G.add_edge(u, v, c=capacity)
    edge_labels[(u, v)] = str(capacity)

# Draw the graph
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, seed=42)  # Layout for consistent positioning
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=800, font_size=15)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title('Topologia Grafu')
plt.show()


simulation = NetworkSimulation(G)
simulation.populate_N_matrix() # Initial N matrix
simulation.compute_a_values(simulation.graph)

# Experiment 1: Increase N values
reliabilities_1 = []
N_copy = simulation.N_matrix.copy()
for step in range(steps):
    simulation.increase_N_values(10)  # Incrementally increasing N matrix values
    simulation.compute_a_values(simulation.graph)
    reliability = simulation.simulate_reliability(initial_p, m)
    reliabilities_1.append(reliability)
    print(f"Reliability after increasing N by {step + 1} increments: {reliability}")

simulation.N_matrix = N_copy
simulation.compute_a_values(simulation.graph)

# Experiment 2: Increase capacities
reliabilities_2 = []
initial_capacities = {(u, v): G[u][v]['c'] for u, v in G.edges()}
for step in range(steps):
    simulation.increase_capacities(10)  # Incrementally increasing capacities
    reliability = simulation.simulate_reliability(initial_p, m)
    reliabilities_2.append(reliability)
    print(f"Reliability after increasing capacities by {step + 10} % increments: {reliability}")

NetworkSimulation.reset_capacities(G, initial_capacities)
# Experiment 3: Add random edges
reliabilities_3 = []
for step in range(steps):
    mean_capacity = simulation.average_capacity()
    simulation.add_random_edges(2, mean_capacity)
    # Adding 2 new edges per step
    reliability = simulation.simulate_reliability(initial_p, m)
    reliabilities_3.append(reliability)
    print(f"Reliability after adding {2 * (step + 1)} new edges: {reliability}")
# Create a figure and a set of subplots
fig, axs = plt.subplots(3, 1, figsize=(8, 12))  # 3 plots, each one stacked vertically

# Plot each reliability graph on a separate subplot
axs[0].plot(reliabilities_1, label='Reliability vs N', color='blue')
axs[0].set_title('Reliability vs N')
axs[0].set_xlabel('Step')
axs[0].set_ylabel('Reliability')
axs[0].legend()

axs[1].plot(reliabilities_2, label='Reliability vs Capacities', color='green')
axs[1].set_title('Reliability vs Capacities')
axs[1].set_xlabel('Step')
axs[1].set_ylabel('Reliability')
axs[1].legend()

axs[2].plot(reliabilities_3, label='Reliability vs Topology Changes', color='red')
axs[2].set_title('Reliability vs Topology Changes')
axs[2].set_xlabel('Step')
axs[2].set_ylabel('Reliability')
axs[2].legend()

# Adjust layout to prevent overlapping
plt.tight_layout()

# Show the plot
plt.show()

