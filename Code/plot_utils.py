from pylab import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import pandas as pd
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

def plot_solution(solution, nodes, available_slots):
    days = set()
    for slot in available_slots:
        days.add(slot.date)
    days = list(days)
    #print(days)
    d = {'game_id':[], 'date':[], 'period':[]}
    for i in range(len(solution)):
        slot = available_slots[solution[i]]
        d['game_id'].append(nodes[i])
        d['date'].append(pd.to_datetime(slot.date))
        d['period'].append("afternoon" if slot.pm else "morning")

    df = pd.DataFrame(data=d)
    # Generate start and end times for each period

    def generate_times(period):
        if period == 'morning':
            return pd.Timestamp('09:00:00'), pd.Timestamp('12:00:00')
        else:
            return pd.Timestamp('12:30:00'), pd.Timestamp('15:30:00')

    df['start_time'], df['end_time'] = zip(*df['period'].apply(generate_times))

    # Generate a random color map for game_id
    unique_game_ids = df['game_id'].unique()
    color_set = set()
    while len(color_set) != len(unique_game_ids):
        color = tuple(random.random() for _ in range(3))
        if color in color_set:
            continue
        color_set.add(color)
    color_map = {}
    for i in range(len(unique_game_ids)):
        color_map[unique_game_ids[i]] = color_set.pop()

    # Plotting the timetable
    fig, ax = plt.subplots(figsize=(12, 8))

    # Get unique dates and assign them an index
    dates = df['date'].dt.date.unique()
    dates.sort()
    date_labels = [date.strftime('%Y-%m-%d') for date in dates]
    date_to_index = {date: idx for idx, date in enumerate(dates)}

    # Track the position for each date
    position_tracker = {date: 0 for date in dates}

    # Create the timetable
    for idx, row in df.iterrows():
        date_index = date_to_index[row['date'].date()]
        position = position_tracker[row['date'].date()]
        color = color_map[row['game_id']]
        
        start = row['start_time'].hour + row['start_time'].minute / 60
        end = row['end_time'].hour + row['end_time'].minute / 60
        
        rect = patches.Rectangle((date_index + position * 0.2, start), 0.2, end - start, edgecolor='black', facecolor=color, lw=1)
        ax.add_patch(rect)
        
        #ax.text(date_index + position * 0.2 + 0.1, (start + end) / 2, f"{row['game_id']}", ha='center', va='center', rotation='vertical', color='black')
        
        # Update position tracker for the date
        position_tracker[row['date'].date()] += 1

    
    # Set the labels
    ax.set_xticks(range(len(date_labels)))
    ax.set_xticklabels(date_labels, rotation=45)
    ax.set_yticks([10.5, 14])
    ax.set_yticklabels(['Morning', 'Afternoon'])
    ax.set_xlim(-0.5, len(date_labels) - 0.5)
    ax.set_ylim(9, 15)
    ax.set_xlabel('Date')
    ax.set_ylabel('Period')
    ax.set_title('Games schedule')

    plt.grid(True)
    plt.show()