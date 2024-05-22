from inspyred import benchmarks
from inspyred import swarm
from inspyred.benchmarks import Benchmark
from inspyred import ec
import itertools

class CalendarColoring(Benchmark):

    def __init__(self, weights, nodes: list, available_slots: list, num_championship=1, champ_size: list=[]):
        Benchmark.__init__(self, len(weights))
        self.weights = weights
        self.nodes = nodes # For championships and neighbourhood retrieval for coloring
        self.slots = available_slots
        # For each node: number of neighbours
        # if max number of neighbours+1 > predecessor
        # check if max number of neighbours+1 > len slot -> value Error, no coloring possible
        max_neighbours = 1
        for i in range(len(self.nodes)):
            num_neighbour = len(self.get_neighbours(i)) + 1
            if num_neighbour > max_neighbours:
                if num_neighbour > len(self.slots):
                    raise ValueError("Number of color too small to generate a valid solution")
                else:
                    max_neighbours = num_neighbour
                    if max_neighbours == len(self.slots):
                        break
        self.num_championship = num_championship
        self.championships=[]
        if self.num_championship==1:
            self.championships.append(nodes)
        else:
            if len(champ_size)+1 == num_championship:
                #self.champ_size = champ_size
                total_matches = 0
                for i in range(len(champ_size)):
                    if i == 0:
                        total_matches = total_matches + champ_size[i]
                        self.championships.append(nodes[:total_matches])
                    else:
                        previous_match = total_matches
                        total_matches = total_matches + champ_size[i]
                        self.championships.append(nodes[previous_match:total_matches])
                        
                if((len(self.weights)-total_matches)>0):
                    self.championships.append(nodes[total_matches:])
                else:
                    raise ValueError("The number of matches per championship is not correct")
            elif len(champ_size)==num_championship:
                total_matches = 0
                for i in range(len(champ_size)):
                    if i == 0:
                        total_matches = total_matches + champ_size[i]
                        self.championships.append(nodes[:total_matches])
                    else:
                        previous_match = total_matches
                        total_matches = total_matches + champ_size[i]
                        self.championships.append(nodes[previous_match:total_matches])
                if(total_matches!=len(self.weights)):
                    raise ValueError("The number of matches per championship is not correct")
            else: 
                raise ValueError("The number of matches doesn't match the one of the championships")            
        # E se cambiassimo i trail components? 1 se non adiacenti, 0 se adiacenti
        self.components = [swarm.TrailComponent((i, j), value=0 if weights[i][j]!=0 else 1) for i, j in itertools.permutations(range(len(weights)), 2)]
        self.bias = 0.5
        self.bounder = ec.DiscreteBounder([i for i in range(len(weights))])
        self.maximize = False
        self._use_ants = False

    def constructor(self, random, args):
        """Return a candidate solution for an ant colony optimization."""
        self._use_ants = True
        candidate = [None]*len(self.weights)
        while None in candidate:
            feasible_components = []
            if candidate.count(None)==len(candidate):
                feasible_components = [c for c in range(len(candidate))]
            else:
                already_visited = [c for c in range(len(candidate)) if candidate[c] is not None] # (servono?)
                feasible_components = [c for c in range(len(candidate)) if candidate[c] is None]
            
            if len(feasible_components) == 0:
                candidate = [None] * len(self.weights)
            elif len(feasible_components) == 1:
                # get neighbours of last component
                neighbours_indexs = self.get_neighbours(feasible_components[0])
                neighbours_slots = [None]*len(neighbours_indexs)
                for i in range(len(neighbours_indexs)):
                    if candidate[neighbours_indexs[i]] is not None:
                        neighbours_slots[i]=candidate[neighbours_indexs[i]]
                # get available slots
                available_slots = []
                for slot in self.slots:
                    if slot not in neighbours_slots:
                        usable_slot = True
                        for n_slot_index in range(len(neighbours_slots)):
                            if neighbours_slots[n_slot_index] is None:
                                continue
                            n_slot = self.slots[neighbours_slots[n_slot_index]]
                            same_champ = False
                            if len(self.championships)>1:
                                for championship in self.championships:
                                    if self.nodes[feasible_components[0]] in championship and self.nodes[neighbours_indexs[n_slot_index]] in championship:
                                        same_champ = True
                            else:
                                same_champ = True
                            # cambiare controllo per includere il discorso dei campionati differenti
                            # ciclo sui campionati. Se entrambi appartengono allo stesso campionato +6, altrimenti, se non appartengono allo stesso, +1
                            if same_champ:
                                if self.weights[feasible_components[0]][neighbours_indexs[n_slot_index]] == 1:
                                    if(abs((n_slot.date-slot.date).days) < 6):
                                        usable_slot = False
                            else:
                                if self.weights[feasible_components[0]][neighbours_indexs[n_slot_index]] == 1:
                                    if(abs((n_slot.date-slot.date).days) < 1):
                                        usable_slot = False
                        if usable_slot == True:
                            available_slots.append(self.slots.index(slot))
                # select first slot between the ones available
                if len(available_slots) == 0:
                    # Since we already checked if there are enough slots for the maximum number of nodes interconnected, if we have
                    # no available slot it means we choose a wrong coloring and we can try another solution
                    for i in self.get_neighbours(feasible_components[0]):
                        candidate[i] = None
                    #print("Solution resetted for bad coloring")
                else: 
                    #candidate[feasible_components[0]] = available_slots[0]
                    if random.random() <= self.bias:
                        candidate[feasible_components[0]] = available_slots[0]
                    else:
                        random_index = random.randint(0,len(available_slots)-1)
                        candidate[feasible_components[0]] = available_slots[random_index]
                # assign slot to node index (feasible_components[0])
            else:
                # Select a feasible component
                if random.random() <= self.bias:
                    # select the first feasible component
                    random_f_c_index = 0
                else:
                    # random index for feasible componen ts
                    random_f_c_index = random.randint(0,len(feasible_components)-1)
                self.current_index = random_f_c_index
                # get neighbours of the selected node
                neighbours_indexs = self.get_neighbours(feasible_components[self.current_index])
                neighbours_slots = [None]*len(neighbours_indexs)
                for i in range(len(neighbours_indexs)):
                    if candidate[neighbours_indexs[i]] is not None:
                        neighbours_slots[i]=candidate[neighbours_indexs[i]]
                # get available slots
                available_slots = []
                for slot in self.slots:
                    if slot not in neighbours_slots:
                        usable_slot = True
                        for n_slot_index in range(len(neighbours_slots)):
                            if neighbours_slots[n_slot_index] is None:
                                continue
                            n_slot = self.slots[neighbours_slots[n_slot_index]]
                            same_champ = False
                            if len(self.championships)>1:
                                for championship in self.championships:
                                    if self.nodes[feasible_components[self.current_index]] in championship and self.nodes[neighbours_indexs[n_slot_index]] in championship:
                                        same_champ = True
                            else:
                                same_champ = True
                            if same_champ:
                                if self.weights[feasible_components[self.current_index]][neighbours_indexs[n_slot_index]] == 1:
                                    # ADD CHECK FOR SAME GYM MATCH THAT ARE NOT OF THE SAME TEAM (example: Virtus Rosso, Virtus Blu and Virtus Bianco)
                                    if(abs((n_slot.date-slot.date).days) < 6):
                                        usable_slot = False
                            else:
                                if self.weights[feasible_components[self.current_index]][neighbours_indexs[n_slot_index]] == 1:
                                    if(abs((n_slot.date-slot.date).days) < 1):
                                        usable_slot = False
                        if usable_slot == True:
                            available_slots.append(self.slots.index(slot))
                # select first slot between the ones available
                if len(available_slots) == 0:
                    # Since we already checked if there are enough slots for the maximum number of nodes interconnected, if we have
                    # no available slot it means we choose a wrong coloring and we can try another solution
                    for i in self.get_neighbours(feasible_components[self.current_index]):
                        candidate[i] = None
                    #print("Solution resetted for bad coloring")
                else:
                    #candidate[feasible_components[random_f_c_index]] = available_slots[0]
                    if random.random() <= self.bias:
                        candidate[feasible_components[random_f_c_index]] = available_slots[0]
                    else:
                        random_index = random.randint(0,len(available_slots)-1)
                        candidate[feasible_components[random_f_c_index]] = available_slots[random_index]
        return candidate

    def evaluator(self, candidates, args):
        """Return the fitness values for the given candidates."""
        fitness = []
        for candidate in candidates:
            different_slots = set(candidate)
            conflict = False
            for i in range(len(candidate)):
                neighbours_indexs = self.get_neighbours(i)
                for j in range(len(neighbours_indexs)):
                    neighbour_slot = self.slots[candidate[neighbours_indexs[j]]]
                same_champ = False
                if len(self.championships)>1:
                    for championship in self.championships:
                        if self.nodes[i] in championship and self.nodes[neighbours_indexs[j]] in championship:
                            same_champ = True
                else:
                    same_champ = True
                if same_champ:
                    if self.weights[i][neighbours_indexs[j]] == 1:
                        if(abs((neighbour_slot.date-self.slots[candidate[i]].date).days) < 6):
                            conflict = True
                            break
                else:
                    if self.weights[i][neighbours_indexs[j]] == 1:
                        if(abs((neighbour_slot.date-self.slots[candidate[i]].date).days) < 1):
                            conflict = True
                            break
            if conflict:
                fitness.append(len(candidate)+1)
            else:
                fitness.append(len(different_slots))
        return fitness

    def get_neighbours(self, index):
        neighbours = []
        for i in range(len(self.weights)):
            if self.weights[index][i] != 0:
                neighbours.append(i)
        return neighbours

def coloring_archive(random, population, archive, args):
    new_archive = archive
    for individual in population:
        if len(new_archive) == 0:
            new_archive.append(individual)
        else:
            should_remove = []
            should_add = True
            for arc_entry in new_archive:
                if individual.candidate == arc_entry.candidate:
                    should_add = False
                    break
                elif individual.fitness < arc_entry.fitness:
                    should_remove.append(arc_entry)
                elif individual.fitness > arc_entry.fitness:
                    should_add = False
            for remove_entry in should_remove:
                new_archive.remove(remove_entry)
            if should_add:
                new_archive.append(individual)
    return new_archive