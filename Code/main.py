import time
import os
import argparse
from dataInitialization import *
from calendarColoring import *
from plot_utils import plot_observer, plot_solution
import matplotlib.pyplot as plt
import inspyred

import collections
collections.Iterable = collections.abc.Iterable
collections.Sequence = collections.abc.Sequence

def _is_valid_file(arg):
    """
    Checks whether input PDDL files exist and are validate
    """

    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('{} not found!'.format(arg))
    elif not os.path.splitext(arg)[1] == ".csv":
        raise argparse.ArgumentTypeError('{} is not a valid CSV file!'.format(arg))
    else:
        return arg

def parse_args():
    parser = argparse.ArgumentParser(description="Sports Game Scheduling")

    parser.add_argument("--graph_path", help='Path to graph file', type=_is_valid_file, required=True)

    parser.add_argument("--slots_file", help='Path to available slots file', type=_is_valid_file, required=True)

    parser.add_argument("--ground_truth", help='Path to ground truth', type=_is_valid_file, required=True)

    parser.add_argument("--max_generations", type=int, default=50, help="Number of max generations")
    parser.add_argument("--pop_size", type=int, default=50, help="Population size")
    parser.add_argument("--learning_rate", type=float, default=0.1, help="Learning rate for ACS")
    parser.add_argument("--evaporation_rate", type=float, default=0.1, help="Evaporation rate for ACS")
    parser.add_argument("--random_seed", type=int, default=None, help="Fix random seed")
    parser.add_argument("--display_graph", action='store_true', help="Display graph representing the calendar")
    parser.add_argument("--num_championship", type=int,  help="Number of championships present in the graph", required=True)
    parser.add_argument("--championship_structure", nargs='+', help="Number of games per championship. The number of arguments must be equal to the number of --num_championship argument", required=True)

    args = parser.parse_args()
    return args

command_args = parse_args()
graph_file = command_args.graph_path
slots_file = command_args.slots_file
gt_file = command_args.ground_truth

# common parameters
pop_size = command_args.pop_size
max_generations = command_args.max_generations
seed = command_args.random_seed
prng = Random(seed)
display = True
# ACS specific parameters
evaporation_rate = command_args.evaporation_rate
learning_rate = command_args.learning_rate

num_championship = command_args.num_championship
championship_structure = [int(i) for i in command_args.championship_structure]

args = {}
args["fig_title"] = "ACS"

nodes, adjmat = getGraphNodesAndAdjacencyMatrix(graph_file)
available_slots = getSlots(slots_file)
ground_truth = getGroundTruth(gt_file, nodes, available_slots)



# run ACS
problem = CalendarColoring(adjmat, nodes, available_slots, num_championship, championship_structure)
ac = inspyred.swarm.ACS(prng, problem.components)
ac.terminator = ec.terminators.generation_termination
ac.observer = [plot_observer]
ac.archiver = coloring_archive
start_time = time.time()
final_pop = ac.evolve(generator=problem.constructor, 
                      evaluator=problem.evaluator, 
                      bounder=problem.bounder,
                      maximize=problem.maximize, 
                      pop_size=pop_size,
                      max_generations=max_generations,
                      evaporation_rate=evaporation_rate,
                      learning_rate=learning_rate,**args)
execution_time = (time.time() - start_time)
print("Execution time: ",execution_time)
#print(ac.archive)
best_ACS = min(ac.archive)

for i in range(len(nodes)):
    node_slot = available_slots[best_ACS.candidate[i]]
    neighbours_indexs = problem.get_neighbours(i)
    for j in range(len(neighbours_indexs)):
        neighbour_slot = available_slots[best_ACS.candidate[neighbours_indexs[j]]]
        same_champ = False
        if len(problem.championships)>1:
            for championship in problem.championships:
                if nodes[i] in championship and nodes[neighbours_indexs[j]] in championship:
                    same_champ = True
        else:
            same_champ = True
        if same_champ:
            if problem.weights[i][neighbours_indexs[j]] == 1:
                if(abs((neighbour_slot.date-available_slots[best_ACS.candidate[i]].date).days) < 6):
                    print("Node: ",nodes[i],"neighbour",nodes[neighbours_indexs[j]],"Is ",neighbour_slot.date,"6 days in advance w.r.t. ", available_slots[best_ACS.candidate[i]].date)
                    print("CONFLICT IN SAME CHAMPIONSHIP")
        else:
            if problem.weights[i][neighbours_indexs[j]] == 1:
                if(abs((neighbour_slot.date-available_slots[best_ACS.candidate[i]].date).days) < 1):
                    print("Node: ",nodes[i],"neighbour",nodes[neighbours_indexs[j]],"Is ",neighbour_slot.date,"1 days in advance w.r.t. ", available_slots[best_ACS.candidate[i]].date)
                    print("CONFLICT IN SAME CHAMPIONSHIP")
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

ioff()
plt.show()
if(command_args.display_graph):
    print("Plotting graph representation of the problem")
    visualize_graph(adjmat=adjmat, nodes=nodes)
print("Plotting solution")
plot_solution(best_ACS.candidate, nodes, available_slots)
print("Plotting ground truth schedule")
plot_solution(ground_truth, nodes, available_slots, "Ground Truth Schedule")