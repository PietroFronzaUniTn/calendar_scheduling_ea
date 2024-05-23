from pylab import *
import matplotlib.pyplot as plt
import numpy
import inspyred.ec.analysis

def plot_observer(population, num_generations, num_evaluations, args):
    stats = inspyred.ec.analysis.fitness_statistics(population)
    best_fitness = stats['best']
    worst_fitness = stats['worst']
    median_fitness = stats['median']
    average_fitness = stats['mean']
    colors = ['black', 'blue', 'green', 'red']
    labels = ['average', 'median', 'best', 'worst']
    data = []
    if num_generations == 0:
        figure(args["fig_title"] + ' (fitness trend)')
        plt.ion()
        data = [[num_evaluations], [average_fitness], [median_fitness], [best_fitness], [worst_fitness]]
        lines = []
        for i in range(4):
            line, = plt.plot(data[0], data[i+1], color=colors[i], label=labels[i])
            lines.append(line)
        args['plot_data'] = data
        args['plot_lines'] = lines
        plt.xlabel('Evaluations')
        plt.ylabel('Fitness')
    else:
        data = args['plot_data']
        data[0].append(num_evaluations)
        data[1].append(average_fitness)
        data[2].append(median_fitness)
        data[3].append(best_fitness)
        data[4].append(worst_fitness)
        lines = args['plot_lines']
        for i, line in enumerate(lines):
            line.set_xdata(numpy.array(data[0]))
            line.set_ydata(numpy.array(data[i+1]))
        args['plot_data'] = data
        args['plot_lines'] = lines
    ymin = min([min(d) for d in data[1:]])
    ymax = max([max(d) for d in data[1:]])
    yrange = ymax - ymin
    plt.xlim((0, num_evaluations))
    plt.ylim((ymin - 0.1*yrange, ymax + 0.1*yrange))
    plt.draw()
    plt.legend()