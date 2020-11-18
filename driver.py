from agent import Agent

from definitionsForAgent import MineSweeper
from copy import deepcopy
import json

from random import randint

def computePerformanceOfAgent(results):
    totalSum = 0
    for result in results:
        totalSum += result
    avg = totalSum/(len(results))
    return avg #(round(avg,2) * 100)

def computeMineDensityPerformance(results):
    density_result_avg = {}
    for density_, test_results in results.items():
        # print(test_results)
        density_result_avg[density_] = computePerformanceOfAgent(test_results)
    return density_result_avg

dimensions = 6
density = 0.1

density_offset = 0.025

trials = 1
subTrials = 1

minimize = MineSweeper.NONE

mines = int((dimensions ** 2) * density)
mine_densities = [density]
numberOfMines = [mines]

mineDensityIndex = 0
trialsConducted = 0

improved_res_v2_5 = {}
improved_res_v2_5_sub_trial = []

copyCacheState = False
# if subTrials == 1:
#     copyCacheState = True
# else:
#     copyCacheState = False

if copyCacheState:
    agentCachedState = []
while trialsConducted < trials:

    mineDensityIndex = len(numberOfMines) - 1

    (x_o, y_o) = (randint(0, dimensions - 1), randint(0, dimensions - 1))
    starting_coord = (x_o, y_o)

    improved_performance_v2_5 = Agent(dimensions, numberOfMines[mineDensityIndex], starting_coord, -1, minimize)

    i_perf_v2_5 = (numberOfMines[mineDensityIndex] - improved_performance_v2_5.agent_died) / numberOfMines[mineDensityIndex]
    improved_res_v2_5_sub_trial.append(i_perf_v2_5)
    if copyCacheState:
        agentCachedState = deepcopy(improved_performance_v2_5.agentStateCache)
    # improved_performance_v2_5.output_agent_map()


    print("Completed trial #%d" % trialsConducted, " with mine density %.2f" % density)

    trialsConducted = trialsConducted + 1

    if trialsConducted % subTrials == 0:
        try:
            improved_res_v2_5[density].extend(improved_res_v2_5_sub_trial)

        except KeyError:
            improved_res_v2_5[density] = improved_res_v2_5_sub_trial

        improved_res_v2_5_sub_trial = []

        density = density + density_offset
        if density > 0.75:
            break
            # density = 0.1
        mines = int((dimensions ** 2) * density)
        numberOfMines.append(mines)

'''
improved_avg_v2_5 = computePerformanceOfAgent(improved_res_v2_5)
print(mine_densities)
print(numberOfMines)
print(improved_res_v2_5)
print("Average Performance of v2.5 : %.2f" % improved_avg_v2_5,end='')
print("%")
'''
print(numberOfMines)
# print(improved_res_v2_5)
# print(basic_res_v2)
improved_avg_v2_5 = computeMineDensityPerformance(improved_res_v2_5)
print("Average Performance of v2.5 : ", improved_avg_v2_5)

if copyCacheState:
    states = 0
    for state in agentCachedState:
        print("Current State: ", states, end=" | ")
        print(state)
        states += 1
    data = {}
    data['agent_states'] = agentCachedState
    data['dimensions'] = dimensions
    data['mine_density'] = numberOfMines[0]
    with open('agentState.json', 'w') as jsonAgentStateFile:
        json.dump(data, jsonAgentStateFile)