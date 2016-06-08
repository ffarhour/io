#!/usr/bin/env python
"""Contains useful functions that are not necessary for proper functionality of scripts.

Author: Farmehr Farhour f.farhour@gmail.com

Contains:
bcolors class: that can be imported and used to color commandline outputs using ANSI colors.
parseCmdLineArgs function: parses inut commandline arguments
"""


class bcolors:
    """Used to implement ANSI colors without the need to remember the numbers.

    Does not contain any methods. Only contains variables.

    Usage: simply concatenate bcolors.<color> at the start of string to be printed,
        and bcolors.ENDC at the end of the string, to color the string with the
        specified color.
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def write_to_file(rawinput, filetype, output_path, engine_name, algorithm_name, suffix="", verbose=False):
    """Output json to the output_path and with a specific name.

    The filename is in the format: '_<engine_name>_<algorithm_name>_suffix.json'.
    This method uses vega-lite to produce the final vega-spec output.

    Arguments:
        json_in: the input json file to be outputted to file.
        suffix: the suffix to name the output files with. default is ""
    Returns: file path to the file created
    """

    # takes in any json string as 'json_in' and writes it to file. The name
    # format of the file explained above
    file = open('%s_%s_%s_%s.%s' % (output_path, engine_name,
                                    algorithm_name, suffix, filetype), 'w')
    file.write(rawinput)
    if(verbose):
        print("Created " + file.name)
    file_path = file.name
    file.close()
    return file_path

import argparse  # built-in


def is_dictionary(string):
    import ast  # built-in
    try:
        value = ast.literal_eval(string)
    except:
        msg = "%r does not have a dictionary format" % string
        raise argparse.ArgumentTypeError(msg)
    return value


def parseCmdLineArgs(argv, output_choices, plot_choices):
    """Function to process input args.

    The various input arguments are defined here. parser.add_argument
        creates a new argument. The function parses the various input
        args passed, and stores them in a list (args). The argparse
        library automatically takes care of the help command.

    Args:
        argv: the input arguments passed through commandline. Simply
            pass in sys.argv from the main function.
        output_choices: a list containing the output type choices available to the user.
            the user will only be able to enter a value equal to that of one of
            the values in the list.
        plot_choices: a list containing the plot type choices available to the user.
            the user will only be able to enter a value contained in the list
    Returns:
        args: a  populated namespace of all the inputted command-line arguments.

    """

    # parse args
    parser = argparse.ArgumentParser(
        description=bcolors.HEADER + 'IO Options' + bcolors.ENDC,
        epilog=bcolors.HEADER + 'Processing Completed' + bcolors.ENDC)

    # add the arguments available to user
    parser.add_argument('--plottype', metavar='<plot type>', type=str, help='select the plot type. Choices={%(choices)s}', choices=plot_choices, required=True)
    parser.add_argument('--outputtype', metavar='<output type>', type=str, help='select the desired output format. Choices={%(choices)s}',choices=output_choices, required=True)
    parser.add_argument('--inputpath', metavar='<input path>', type=str,
                        help='directory containing input JSON files. Default= gunrock-output/ ',
                        default='gunrock-output/')
    parser.add_argument('-o', metavar='<output path>', type=str,
                        help='directory for output files. Default= output/',
                        default='output/')
    parser.add_argument('--engine', metavar='<engine_name>', type=str, help='the engine name the outputs are from', required=True)
    parser.add_argument('--algorithm', metavar='<algorithm name>', type=str, help='the algorithm name of the datasets. e.g. BFS', required=True)
    parser.add_argument('--xaxis',metavar='<x-axis variable>', type=str, help='the variable used on the x axis', required=True)
    parser.add_argument('--yaxis', metavar='<y-axis variable>', type=str, help='the variable used on the y axis', required=True)
    parser.add_argument('--conds','-c', metavar='<conditions>', type=is_dictionary, help='additional conditions to narrow the results to be graphed. the type needs to be like a dictionary. e.g. {"undirected": True, "mark_predecessors": True}')
    parser.add_argument('--xlabel', metavar ='<x_axis label>', type=str, help='the label for the x axis', default='')
    parser.add_argument('--ylabel', metavar='<y_axis label>', type=str, help='the label for the y axis', default='')
    parser.add_argument('--filesuffix', metavar='<file_suffix>', type=str, help='the suffix used to create the output file. Default=""',default='')
    parser.add_argument('-v',action='store_true',help='verbosity, if included in the args the program will increase verbosity as it executes')
    parser.add_argument('--config', metavar='<config files directory>', type=str, help='the location of the config files can be changed if desired. Default = scripts/config_files', default = 'scripts/config_files')

    args = parser.parse_args()
    return args
