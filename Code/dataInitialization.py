import os
import math
from random import Random

import networkx as nx
from matplotlib import *
from pylab import *
import datetime

from matplotlib import collections  as mc

from calendarColoring import CalendarColoring

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

if __name__ == "__main__":
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

    if file_index == 2:
        instance = CalendarColoring(adjmat, nodes, available_slots, num_championship=2, champ_size=[14,56])
    else: 
        instance = CalendarColoring(adjmat, nodes, available_slots)
    #print(nodes)
    print(instance.championships)  
    solution = instance.constructor(Random(), [])
    sol_string = "["
    for i in range(len(solution)):
        if solution[i] is None:
            sol_string = sol_string + nodes[i] + ": None"
        else:
            sol_string = sol_string + nodes[i] + ": " + str(available_slots[solution[i]])
        if(i!=len(solution)-1):
            sol_string = sol_string + ", "
    sol_string = sol_string + "]"
    print(sol_string)
    print(solution)
    print(max(solution))
    print(instance.evaluator([solution], []))