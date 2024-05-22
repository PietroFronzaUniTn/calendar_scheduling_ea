from dataInitialization import *
from calendarColoring import *
import inspyred

import collections
collections.Iterable = collections.abc.Iterable
collections.Sequence = collections.abc.Sequence

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

# common parameters
pop_size = 10
max_generations = 10
seed = 0
prng = Random(seed)
display = True
# ACS specific parameters
evaporation_rate = 0.1
learning_rate = 0.1

args = {}
args["fig_title"] = "ACS"

nodes, adjmat = getGraphNodesAndAdjacencyMatrix(graph_file)
available_slots = getSlots(slots_file)
ground_truth = getGroundTruth(gt_file, nodes, available_slots)

# run ACS
if file_index == 2:
    problem = CalendarColoring(adjmat, nodes, available_slots, num_championship=2, champ_size=[14,56])
else:
    problem = CalendarColoring(adjmat, nodes, available_slots)
ac = inspyred.swarm.ACS(prng, problem.components)
#ac.observer = [plot_observer]
ac.archiver = coloring_archive
ac.terminator = inspyred.ec.terminators.generation_termination
final_pop = ac.evolve(generator=problem.constructor, 
                      evaluator=problem.evaluator, 
                      bounder=problem.bounder,
                      maximize=problem.maximize, 
                      pop_size=pop_size,
                      max_generations=max_generations,
                      evaporation_rate=evaporation_rate,
                      learning_rate=learning_rate,**args)
print(ac.archive)
best_ACS = min(ac.archive)

sol_string = "["
for i in range(len(best_ACS.candidate)):
    if best_ACS.candidate[i] is None:
        sol_string = sol_string + nodes[i] + ": None"
    else:
        sol_string = sol_string + nodes[i] + ": " + str(available_slots[best_ACS.candidate[i]])
    if(i!=len(best_ACS.candidate)-1):
        sol_string = sol_string + ", "
sol_string = sol_string + "]"
print(sol_string)