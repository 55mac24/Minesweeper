import argparse
from definitionsForAgent import MineSweeper

dimension_help_msg = "The dimension for the Minesweeper map"
density_help_msg = "The mine density for the Minesweeper map in the range 0 < density < 1.0"
density_offset_help_msg = "The amount for which the density should increase on the next trial"
trials_help_msg = "The number of trials the agent should conduct"
subtrials_help_msg = "The number of sub-trials the agent should conduct at each mine density"
prediction_type_help_msg = "Whether the agent should minimize cost, risk, or none during its traversal"

parser = argparse.ArgumentParser()


parser.add_argument('-d', '--dimensions', type=int, metavar='dimensions', help=dimension_help_msg)
parser.add_argument('-p', '--density', type=float, metavar='density', nargs='?',help=density_help_msg, default='0.1')
parser.add_argument('-o', '--offset', type=float, metavar='density_offset', nargs='?', help=density_offset_help_msg, default='0.025')
parser.add_argument('-t', '--trials', type=int, metavar='trials', help=trials_help_msg)
parser.add_argument('-s', '--subtrials', type=int, metavar='subtrials', nargs='?', help=subtrials_help_msg, default='1')
parser.add_argument('-m', '--minimize', type=str, metavar='minimize', nargs='?', help=prediction_type_help_msg, default='none')

args = parser.parse_args()

dimensions, density, density_offset, trials, subTrials, minimize = None, None, None, None, None, None

if args.dimensions:

    dimensions = args.dimensions
    print(dimensions * 2)
else:
    dimensions = 10

if args.density:
    print("Density: ", args.density)
    density = args.density
else:
    density = 0.1
if args.offset:
    print("Offset: ", args.offset)
    density_offset = args.offset
else:
    density_offset = 0.025

if args.trials:
    print("Trials: ", args.trials)
    trials = args.trials
else:
    trials = 1
if args.subtrials:
    print("Subtrials: ", args.subtrials)
    subTrials = args.subtrials
else:
    subTrials = 1
arg_minimize = None

if args.minimize:
    print("Minimize: ", args.minimize)
    arg_minimize = args.minimize.upper()
else:
    arg_minimize = MineSweeper.NONE

if arg_minimize == MineSweeper.COST:
    minimize = MineSweeper.COST
elif arg_minimize == MineSweeper.RISK:
    minimize = MineSweeper.RISK
else:
    minimize = MineSweeper.NONE

print("Dimensions: %d | Density: %.2f | Density Offset: %.4f | " % (dimensions, density, density_offset), end='')
print("Trials: %d | Sub-Trials: %d | Minimize: %s" % (trials, subTrials, minimize))