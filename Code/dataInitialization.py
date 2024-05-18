import os
from inspyred import benchmarks
from inspyred import swarm
from inspyred.benchmarks import Benchmark
from inspyred import ec
import itertools
import math
from random import Random

import networkx as nx
from matplotlib import *
from pylab import *
import datetime

from matplotlib import collections  as mc

def getGraphNodesAndAdjacencyMatrix(file):
    with open(file) as f:
        lines = f.read().splitlines()
        adjmat = []
        nodes = [node for node in lines[0].split(";")[1:]]
        for line in lines[1:]:
            row = []
            for value in line.split(";")[1:]:
                row.append(float(value))
            adjmat.append(row)
        
        return nodes,adjmat 

def getSlots(file):
    with open(file) as f:
        lines = f.read().splitlines()
        slots = []
        for line in lines:
            for value in line.split(";"):
                split_val = value.split(" ")
                if len(split_val) == 1:
                    slot = TimeSlot(split_val[0])
                else:
                    slot = TimeSlot(split_val[0], pm= False if split_val[1]=="am" else True)
                slots.append(slot)
        return slots

def getGroundTruth(file, nodes, slots):
    with open(file) as f:
        lines = f.read().splitlines()
        ground_truth = [None]*len(nodes)
        for line in lines:
            row = line.split(";")
            node_index = nodes.index(row[0])
            slot_split = row[1].split(" ")
            if len(slot_split) == 1:
                slot = TimeSlot(slot_split[0])
            else:
                slot = TimeSlot(slot_split[0], pm= False if slot_split[1]=="am" else True)
            slot_index = slots.index(slot)
            ground_truth[node_index] = slot_index
        return ground_truth

class GraphVisualization: 
   
    def __init__(self): 
          
        # visual is a list which stores all  
        # the set of edges that constitutes a 
        # graph 
        self.visual = [] 
          
    # addEdge function inputs the vertices of an 
    # edge and appends it to the visual list 
    def addEdge(self, a, b): 
        temp = [a, b] 
        self.visual.append(temp) 
          
    # In visualize function G is an object of 
    # class Graph given by networkx G.add_edges_from(visual) 
    # creates a graph with a given list 
    # nx.draw_networkx(G) - plots the graph 
    # plt.show() - displays the graph 
    def visualize(self): 
        G = nx.Graph() 
        G.add_edges_from(self.visual) 
        nx.draw_networkx(G) 
        plt.show()  

class TimeSlot:
    def __init__(self, date, pm: bool = False) -> None:
        self.date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        self.pm = pm

    def __str__(self) -> str:
        ret_str = str(self.date)
        return ret_str + " afternoon" if self.pm else ret_str + " morning"
    
    def __eq__(self, value: object) -> bool:
        if self is value:
            return True
        elif type(self) != type(value):
            return False
        else:
            return self.date == value.date and self.pm == value.pm
    
    def __gt__(self, value: object) -> bool:
        if(self.date>value.date):
            return True
        elif(self.date<value.date):
            return False
        else:
            if(self.pm == value.pm):
                return False
            elif(self.pm and not value.pm):
                return True
            else:
                return False

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
        self.components = [swarm.TrailComponent((i, j), value=(1 / weights[i][j]) if weights[i][j]!=0 else 0) for i, j in itertools.permutations(range(len(weights)), 2)]
        self.bias = 0.5
        self.bounder = ec.DiscreteBounder([i for i in range(len(weights))])
        self.maximize = True
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
                            for championship in self.championships:
                                if self.nodes[feasible_components[0]] in championship and self.nodes[neighbours_indexs[n_slot_index]] in championship:
                                    same_champ = True
                            # cambiare controllo per includere il discorso dei campionati differenti
                            # ciclo sui campionati. Se entrambi appartengono allo stesso campionato +6, altrimenti, se non appartengono allo stesso, +1
                            if same_champ:
                                if(abs((n_slot.date-slot.date).days) < 6):
                                    usable_slot = False
                            else:
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
                    print("Solution resetted for bad coloring")
                else: 
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
                            # NO DOVREBBE ESSERE CON LA PARTITA
                            for championship in self.championships:
                                if self.nodes[feasible_components[self.current_index]] in championship and self.nodes[neighbours_indexs[n_slot_index]] in championship:
                                    same_champ = True
                            if same_champ:
                                if(abs((n_slot.date-slot.date).days) < 6):
                                    usable_slot = False
                            else:
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
                    print("Solution resetted for bad coloring")
                else: 
                    if random.random() <= self.bias:
                        candidate[feasible_components[random_f_c_index]] = available_slots[0]
                    else:
                        random_index = random.randint(0,len(available_slots)-1)
                        candidate[feasible_components[random_f_c_index]] = available_slots[random_index]
        return candidate

    def get_neighbours(self, index):
        neighbours = []
        for i in range(len(self.weights)):
            if self.weights[index][i] == 1:
                neighbours.append(i)
        return neighbours

file_index = 1

if(file_index==0):
    graph_file="./Data/OneTeamGraph.csv"
    slots_file="./Data/OneTeamSlots.csv"
    gt_file="./Data/OneTeamGT.csv"
elif(file_index==1):
    graph_file="./Data/OneChampionshipGraph.csv"
    slots_file="./Data/OneChampionshipSlots.csv"
    gt_file="./Data/OneChampionshipGT.csv"
else:
    graph_file="./Data/TwoChampionshipOneTeamGraph.csv"
    slots_file="./Data/TwoChampionshipOneTeamSlots.csv"
    gt_file="./Data/TwoChampionshipOneTeamGT.csv"

nodes, adjmat = getGraphNodesAndAdjacencyMatrix(graph_file)
G = GraphVisualization()
for i in range(len(adjmat)):
    for j in range(len(adjmat[i])):
        if adjmat[i][j]>0:
            G.addEdge(nodes[i], nodes[j])
#G.visualize()

available_slots = getSlots(slots_file)
av_slots_str = "["
for i in available_slots:
    av_slots_str = av_slots_str + str(i)
    if(available_slots.index(i)!=len(available_slots)-1):
        av_slots_str = av_slots_str+", "
av_slots_str = av_slots_str + "]"
print(av_slots_str)
    
ground_truth = getGroundTruth(gt_file, nodes, available_slots)
print(ground_truth)

instance = CalendarColoring(adjmat, nodes, available_slots)#, num_championship=2, champ_size=[14,56])
#print(nodes)
print(instance.championships)  
solution = instance.constructor(Random(), [])
sol_string = "["
for i in range(len(solution)):
    sol_string = sol_string + nodes[i] + ": " + str(available_slots[solution[i]])
    if(i!=len(solution)-1):
        sol_string = sol_string + ", "
sol_string = sol_string + "]"
print(sol_string)