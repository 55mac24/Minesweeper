from .agent import Agent
from .definitionsForAgent import MineSweeper, MINIMIZE, TYPE
import argparse
from random import randint
import sys

def computePerformanceOfAgent(results):
    totalSum = 0
    for result in results:
        totalSum += result
    avg = totalSum / (len(results))
    return avg  # (round(avg,2) * 100)


def computeMineDensityPerformance(results):
    density_result_avg = {}
    first = None
    for density_, test_results in results.items():
        first = density_
        density_result_avg[density_] = computePerformanceOfAgent(test_results)
    return first, density_result_avg


class MinesweeperSolver:
    def __init__(self, dimensions, density, density_offset,
                 trials, subTrials,
                 minimize, copyCacheState=False,
                 mode=MineSweeper.PRODUCTION):

        self.dimensions, self.density, self.density_offset = dimensions, density, density_offset
        self.minimize = minimize
        self.trials, self.subTrials = trials, subTrials
        self.copyCacheState, self.mode = copyCacheState, mode

        self.conductTrials = conductTrials
        self.improved_res_v2_5, self.improved_res_v2_5_sub_trial = None, None
        self.agentCachedState, self.hidden_map = None, None
        self.mines, self.mine_densities, self.numberOfMines = None, None, None
        self.data = None
        self.initializeParameters()

    def initializeParameters(self):
        self.improved_res_v2_5, self.improved_res_v2_5_sub_trial = {}, []
        self.agentCachedState, self.hidden_map = [], None

        self.mines = int((self.dimensions ** 2) * self.density)
        self.mine_densities = [self.density]
        self.numberOfMines = [self.mines]

    def performance(self):
        print("Number of Mines: ", self.numberOfMines)
        first_density_perf, improved_avg_v2_5 = computeMineDensityPerformance(self.improved_res_v2_5)
        print("Average Performance of v2.5 : ", improved_avg_v2_5)
        return first_density_perf, improved_avg_v2_5

    def createCacheStateCopy(self, hidden_map, agentCachedState):
        mapData = {'clues': [], 'mines': []}
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                if hidden_map[x][y] == TYPE.MINE:
                    mapData['mines'].append((x, y))
                else:
                    mapData['clues'].append((x, y))

        first_density_perf, density_perf = self.performance()
        performance = density_perf[first_density_perf]

        self.data = {'dimensions': self.dimensions, 'mine_density': self.density, 'agent_states': agentCachedState,
                     'performance': performance, 'hidden_map': hidden_map}

    def execute(self):
        for trial in range(self.trials):

            (x_o, y_o) = (randint(0, self.dimensions - 1), randint(0, self.dimensions - 1))
            starting_coord = (x_o, y_o)

            performance_v2_5 = Agent(self.dimensions, self.numberOfMines[-1], starting_coord, -1,
                                     self.minimize, self.mode)

            i_perf_v2_5 = (self.numberOfMines[-1] - performance_v2_5.agent_died) / self.numberOfMines[-1]

            self.improved_res_v2_5_sub_trial.append(i_perf_v2_5)

            # improved_performance_v2_5.output_agent_map()

            print("Completed trial #%d" % trial, " with mine density %.2f" % self.density)

            if trial % self.subTrials == 0:
                try:
                    self.improved_res_v2_5[self.density].extend(self.improved_res_v2_5_sub_trial)

                except KeyError:
                    self.improved_res_v2_5[self.density] = self.improved_res_v2_5_sub_trial

                self.improved_res_v2_5_sub_trial = []

                if self.trials > 1:

                    self.density = self.density + self.density_offset
                    if self.density > 0.75:
                        break

                    mines = int((self.dimensions ** 2) * self.density)
                    self.numberOfMines.append(mines)

            if self.copyCacheState:
                self.createCacheStateCopy(performance_v2_5.hidden_map, performance_v2_5.agentStateCache)


if __name__ == "__main__":
    if len(sys.argv) > 0:
        dimension_help_msg = "The dimension for the Minesweeper map"
        density_help_msg = "The mine density for the Minesweeper map in the range 0 < density < 1.0"
        density_offset_help_msg = "The amount for which the density should increase on the next trial"
        trials_help_msg = "The number of trials the agent should conduct"
        subtrials_help_msg = "The number of sub-trials the agent should conduct at each mine density"
        prediction_type_help_msg = "Whether the agent should minimize cost, risk, or none during its traversal"

        parser = argparse.ArgumentParser()

        parser.add_argument('-d', '--dimensions', type=int, metavar='dimensions', help=dimension_help_msg)
        parser.add_argument('-p', '--density', type=float, metavar='density', nargs='?', help=density_help_msg,
                            default='0.1')
        parser.add_argument('-o', '--offset', type=float, metavar='density_offset', nargs='?', help=density_offset_help_msg,
                            default='0.025')
        parser.add_argument('-t', '--trials', type=int, metavar='trials', help=trials_help_msg)
        parser.add_argument('-s', '--subtrials', type=int, metavar='subtrials', nargs='?', help=subtrials_help_msg,
                            default='1')
        parser.add_argument('-m', '--minimize', type=str, metavar='minimize', nargs='?', help=prediction_type_help_msg,
                            default='none')

        args = parser.parse_args(sys.argv[1:])

        dimensions = args.dimensions if 3 < args.dimensions < 256 else 10
        density = args.density if args.density and 0.0 < args.density < 1.0 else 0.1
        density_offset = args.offset if args.offset and 0.0 < args.offset <= 0.5 else 0.025
        trials = args.trials if args.trials and 0 < args.trials <= 100 else 1

        subTrials = args.subtrials if args.subtrials and 0 < args.subtrials <= 100 else 1

        arg_minimize = None

        if args.minimize:
            arg_minimize = int(args.minimize)
        else:
            arg_minimize = MINIMIZE.NONE

        if arg_minimize == MINIMIZE.COST:
            minimize = MINIMIZE.COST
        elif arg_minimize == MINIMIZE.RISK:
            minimize = MINIMIZE.RISK
        else:
            minimize = MINIMIZE.NONE

        conductTrials = False
        print("Dimensions: %d | Density: %.2f | Density Offset: %.4f | " % (dimensions, density, density_offset), end='')
        print("Trials: %d | Sub-Trials: %d | Minimize: %s" % (trials, subTrials, minimize))

        driver = MinesweeperSolver(dimensions=dimensions, density=density, density_offset=density_offset,
                        trials=trials, subTrials=subTrials, minimize=minimize, copyCacheState=True)
        driver.execute()
