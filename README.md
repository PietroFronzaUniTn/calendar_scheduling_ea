# Basketball Games Scheduling using Ant Colony System
[\[Report\]](Report.pdf)

The job scheduling problem aims to sort a sequence
of jobs in order for the execution to proceed smoothly and end in the shortest time possible. This concept is taken up in many areas, such as sports. In fact, the sports leagues aim to distribute the matches during the year conclude the championships in the best way possible, in order to possibly prepare new tournaments for the final part of the sport’s season. The purpose of this paper is to evaluate the distribution of the games of some basketball championships and try to create an algorithm that allows an efficient distribution of matches to minimize the risks of overlap and allow some room of movement in case of unforeseen events.

## Requirements
Before getting started, make sure you have installed inspyred and networkx.
```
pip install inspyred
pip install networkx
```

## Structure
The repository is structured as follows:
```
    .
    ├── Data                     # csv files used to test the algorith
    ├── Code                          # Files implementing the code of the project
    ├── Plots                      # Containing the plots for each instance
    └── Results                      # Contains the txt files with the best solution found
```

## Usage
### Execute the algorithms
The following commands can be used to execute the algorithm:
``` shell
python main.py --graph_path ".\data\TwoCampionshipGraph.csv"
    --slots_file ".\data\TwoChampioshipSlots.csv"
    --ground_truth ".\data\TwoChampionshipGT.csv"
    --max_generations 50
    --pop_size = 50
    --learning_rate 0.1
    --evaporation_rate 0.1
    --display_graph
    --num_championship 2
    --championship_structure 54 56
```

## Contribution
Authors:
- Pietro Fronza, MSc Student University of Trento (Italy), pietro.fronza@studenti.unitn.it