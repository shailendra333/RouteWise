import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any

class GeneticAlgorithmTSP:
    """
    Advanced Genetic Algorithm implementation for Traveling Salesman Problem (TSP)
    Optimized for logistics route planning with multiple enhancements
    """
    
    def __init__(self, 
                 population_size: int = 100,
                 elite_size: int = 20,
                 mutation_rate: float = 0.01,
                 generations: int = 500,
                 tournament_size: int = 5):
        """
        Initialize the Genetic Algorithm with parameters
        
        Args:
            population_size: Number of individuals in population
            elite_size: Number of elite individuals to preserve
            mutation_rate: Probability of mutation
            generations: Number of generations to evolve
            tournament_size: Size of tournament for selection
        """
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.tournament_size = tournament_size
        self.best_distance_history = []
        self.average_distance_history = []
        
    def calculate_distance(self, city1: Tuple[float, float], city2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two cities"""
        return np.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)
    
    def route_fitness(self, route: List[int], coordinates: List[Tuple[float, float]]) -> float:
        """
        Calculate fitness of a route (inverse of total distance)
        
        Args:
            route: List of city indices representing the route
            coordinates: List of (x, y) coordinates for each city
            
        Returns:
            Fitness value (higher is better)
        """
        total_distance = 0
        for i in range(len(route)):
            from_city = coordinates[route[i]]
            to_city = coordinates[route[(i + 1) % len(route)]]
            total_distance += self.calculate_distance(from_city, to_city)
        
        return 1 / total_distance if total_distance > 0 else 0
    
    def create_route(self, city_list: List[int]) -> List[int]:
        """Create a random route from city list"""
        route = city_list.copy()
        random.shuffle(route)
        return route
    
    def initial_population(self, city_list: List[int]) -> List[List[int]]:
        """Create initial population of routes"""
        population = []
        for _ in range(self.population_size):
            population.append(self.create_route(city_list))
        return population
    
    def rank_routes(self, population: List[List[int]], coordinates: List[Tuple[float, float]]) -> List[Tuple[int, float]]:
        """
        Rank routes by fitness
        
        Returns:
            List of (route_index, fitness) tuples sorted by fitness (descending)
        """
        fitness_results = []
        for i, route in enumerate(population):
            fitness = self.route_fitness(route, coordinates)
            fitness_results.append((i, fitness))
        
        return sorted(fitness_results, key=lambda x: x[1], reverse=True)
    
    def selection(self, ranked_population: List[Tuple[int, float]], population: List[List[int]]) -> List[List[int]]:
        """
        Select parents for mating using tournament selection combined with elitism
        """
        selection_results = []
        
        # Elitism: preserve best routes
        for i in range(self.elite_size):
            selection_results.append(population[ranked_population[i][0]])
        
        # Tournament selection for remaining slots
        for _ in range(len(population) - self.elite_size):
            tournament = random.sample(ranked_population, self.tournament_size)
            winner = max(tournament, key=lambda x: x[1])
            selection_results.append(population[winner[0]])
        
        return selection_results
    
    def breed(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """
        Create offspring using Order Crossover (OX)
        """
        gene_a = int(random.random() * len(parent1))
        gene_b = int(random.random() * len(parent1))
        
        start_gene = min(gene_a, gene_b)
        end_gene = max(gene_a, gene_b)
        
        child_p1 = parent1[start_gene:end_gene]
        child_p2 = [item for item in parent2 if item not in child_p1]
        
        return child_p1 + child_p2
    
    def breed_population(self, mating_pool: List[List[int]]) -> List[List[int]]:
        """Create new population through breeding"""
        children = []
        
        # Keep elite individuals unchanged
        for i in range(self.elite_size):
            children.append(mating_pool[i])
        
        # Breed remaining population
        for _ in range(len(mating_pool) - self.elite_size):
            parent1 = random.choice(mating_pool[:self.elite_size * 2])
            parent2 = random.choice(mating_pool[:self.elite_size * 2])
            child = self.breed(parent1, parent2)
            children.append(child)
        
        return children
    
    def mutate(self, individual: List[int]) -> List[int]:
        """
        Apply mutation using swap mutation
        """
        for swapped in range(len(individual)):
            if random.random() < self.mutation_rate:
                swap_with = int(random.random() * len(individual))
                
                city1 = individual[swapped]
                city2 = individual[swap_with]
                
                individual[swapped] = city2
                individual[swap_with] = city1
        
        return individual
    
    def mutate_population(self, population: List[List[int]]) -> List[List[int]]:
        """Apply mutation to population (skip elite individuals)"""
        mutated_pop = []
        
        # Keep elite individuals unchanged
        for i in range(self.elite_size):
            mutated_pop.append(population[i])
        
        # Mutate remaining population
        for i in range(self.elite_size, len(population)):
            mutated_ind = self.mutate(population[i])
            mutated_pop.append(mutated_ind)
        
        return mutated_pop
    
    def optimize(self, coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Run the genetic algorithm optimization
        
        Args:
            coordinates: List of (x, y) coordinates for cities
            
        Returns:
            Dictionary containing optimization results
        """
        try:
            city_list = list(range(len(coordinates)))
            population = self.initial_population(city_list)
            
            self.best_distance_history = []
            self.average_distance_history = []
            
            print(f"Starting optimization with {len(coordinates)} cities...")
            
            for generation in range(self.generations):
                # Rank current population
                ranked_pop = self.rank_routes(population, coordinates)
                
                # Track progress
                best_fitness = ranked_pop[0][1]
                best_distance = 1 / best_fitness if best_fitness > 0 else float('inf')
                avg_fitness = sum([x[1] for x in ranked_pop]) / len(ranked_pop)
                avg_distance = 1 / avg_fitness if avg_fitness > 0 else float('inf')
                
                self.best_distance_history.append(best_distance)
                self.average_distance_history.append(avg_distance)
                
                # Print progress every 50 generations
                if generation % 50 == 0:
                    print(f"Generation {generation}: Best distance = {best_distance:.2f}")
                
                # Selection
                selection_results = self.selection(ranked_pop, population)
                
                # Breeding
                children = self.breed_population(selection_results)
                
                # Mutation
                population = self.mutate_population(children)
            
            # Get final best route
            final_ranked = self.rank_routes(population, coordinates)
            best_route_index = final_ranked[0][0]
            best_route = population[best_route_index]
            best_distance = 1 / final_ranked[0][1]
            
            # Convert coordinates for the best route
            route_coordinates = [coordinates[i] for i in best_route]
            
            print(f"Optimization completed! Best distance: {best_distance:.2f}")
            
            return {
                'success': True,
                'best_route': best_route,
                'best_distance': best_distance,
                'route_coordinates': route_coordinates,
                'generations_run': self.generations,
                'population_size': self.population_size,
                'best_distance_history': self.best_distance_history,
                'average_distance_history': self.average_distance_history
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def plot_progress(self):
        """Plot the optimization progress"""
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.best_distance_history, label='Best Distance', color='blue')
        plt.plot(self.average_distance_history, label='Average Distance', color='red', alpha=0.7)
        plt.xlabel('Generation')
        plt.ylabel('Distance')
        plt.title('Optimization Progress')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        improvement = [(self.best_distance_history[0] - d) / self.best_distance_history[0] * 100 
                      for d in self.best_distance_history]
        plt.plot(improvement, color='green')
        plt.xlabel('Generation')
        plt.ylabel('Improvement (%)')
        plt.title('Percentage Improvement')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_route(self, coordinates: List[Tuple[float, float]], route: List[int], title: str = "Optimized Route"):
        """Plot the optimized route"""
        plt.figure(figsize=(10, 8))
        
        # Plot cities
        x_coords = [coord[0] for coord in coordinates]
        y_coords = [coord[1] for coord in coordinates]
        plt.scatter(x_coords, y_coords, c='red', s=100, zorder=5)
        
        # Plot route
        route_x = [coordinates[i][0] for i in route] + [coordinates[route[0]][0]]
        route_y = [coordinates[i][1] for i in route] + [coordinates[route[0]][1]]
        plt.plot(route_x, route_y, 'b-', linewidth=2, alpha=0.7)
        
        # Add city labels
        for i, (x, y) in enumerate(coordinates):
            plt.annotate(f'C{i}', (x, y), xytext=(5, 5), textcoords='offset points')
        
        plt.title(title)
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()

def demo_optimization():
    """Demonstration of the genetic algorithm"""
    # Sample coordinates for 10 cities (logistics delivery points)
    coordinates = [
        (40.7829, -73.9654),  # Central Park
        (40.7580, -73.9855),  # Times Square
        (40.7061, -73.9969),  # Brooklyn Bridge
        (40.7484, -73.9857),  # Empire State Building
        (40.7074, -74.0113),  # Wall Street
        (40.7505, -73.9934),  # Herald Square
        (40.7282, -73.9942),  # Washington Square Park
        (40.7614, -73.9776),  # Columbus Circle
        (40.7691, -73.9563),  # Guggenheim Museum
        (40.7407, -73.9906),  # Union Square
    ]
    
    # Initialize and run optimization
    ga = GeneticAlgorithmTSP(
        population_size=100,
        elite_size=20,
        mutation_rate=0.02,
        generations=300,
        tournament_size=5
    )
    
    result = ga.optimize(coordinates)
    
    if result['success']:
        print(f"Optimization successful!")
        print(f"Best route: {result['best_route']}")
        print(f"Best distance: {result['best_distance']:.2f}")
        print(f"Generations: {result['generations_run']}")
        
        # Plot results
        ga.plot_progress()
        ga.plot_route(coordinates, result['best_route'])
    else:
        print(f"Optimization failed: {result['error']}")

if __name__ == "__main__":
    demo_optimization()