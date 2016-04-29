#!/usr/bin/env python
"""Converts JSON outputs from graph algorithms to vega-spec json files to be plotted.

Author: Farmehr Farhour f.farhour@gmail.com
Some code refactored and re-used from testvl.py script written by JDO

This file contains a base class, and a child class for each type of graph to be plotted.

Dependencies:
    python:
        pandas (pip install pandas)
        numpy (pip install numpy)
    nodejs:
        vega (sudo npm install vega)
        vega-lite (sudo npm install vega-lite)

"""

import pandas, numpy
import json, os, argparse          #built-in
from subprocess import Popen, PIPE, STDOUT          #built-in

#Base class to produce vega-spec jsons
class VegaGraphBase(object):
    """Base class for converting json outputs of different algorithms to vega-specific graph json files.

    This class is the base class, and the child classes inherit the methods and variables of this class.
    The purpose of this class is to centralise the main functionalities shared by all child classes.

    Attributes:
        output_path: the output directory to write the vega-spec json files to.
        input_path: the input path containing the input json files to be processed.
        config_dir: the directory containing the json config files relevant to each plot type.
            Each config file will need to have a specific name of the format: '<plot type>_config.json'
        labels: a dictionary containing the relevant nouns required for naming the file and the axes of the
            plots created. The names dictionary should contain 5 keys and their corresponding values.
            They are:
                engine_name: the name of the engine used to run the algorithm (e.g. Gunrock). This is
                    used to name the output files.
                algorithm_name: the name of the algorithm (e.g. BFS). This is used to name the
                    output files.
                x_axis: the label for the x_axis
                y_axis: the label for the y_axis
                file_suffix: the suffix to put at the end of the file being generated.
                e.g. labels = {'engine_name':'g','algorithm_name':'BFS','x_axis':'Datasets','y_axis':'MTEPS','file_suffix':'0'}

    """

    #list containing all jsons
    __input_jsons = []

    def __init__(self,output_path,input_path,config_dir,labels):
        """Initis base class with provided atrributes."""
        self.output_path = output_path
        self.input_path = input_path
        self.config_dir = config_dir
        self.engine_name = labels['engine_name']
        self.algorithm_name = labels['algorithm_name']
        self.file_suffix = labels['file_suffix']


    def read_json(self):
        """Reads json files wiht the right specs into __input_jsons list

        Does not take any arguments.
        Does not return any variables.
        """
        #read in all json files in the input_path, that match the algorithm_name and are not outputs
        for f in os.listdir(self.input_path):
            if(os.path.splitext(f)[1]==".json") and (os.path.basename(f).startswith(self.algorithm_name)) and (not os.path.basename(f).startswith("_")):
                self.__input_jsons += [json.load(open(self.input_path + f))]

    def run(self,verbose=False):
        """calls the relevant methods to convert input jsons to vega-spec jsons

        Arguments:
            verbose: If True, prints out what is happening. Default=False.
        """
        self.read_json()
        graph = self.parse_jsons()
        self.write_json(graph,self.file_suffix,verbose)

#TODO method to check whether config files exist. If not use default.
    def read_config(self):
        """Returns the json config file as a python object"""
        return json.load(open(self.config_dir +"/" + "bar_config.json"))


    def parse_jsons(self):
        """Parses the input json files using Pandas.

        Returns: a pandas dataframe containting the data processed from input jsons.
        """
        #store all data in a pandas DataFrame
        pandas_df = pandas.DataFrame(self.__input_jsons)
        return pandas_df


    def write_json(self,json_in,suffix="",verbose=False):
        """Output json to the output_path and with a specific name.

        The filename is in the format: '_<engine_name>_<algorithm_name>_suffix.json'.
        This method uses vega-lite to produce the final vega-spec output.

        Arguments:
            json_in: the input json file to be outputted to file.
            suffix: the suffix to name the output files with. default is ""
        """

        # pipe it through vl2vg to turn it into vega
        file = open('%s_%s_%s_%s.json' %(self.output_path,self.engine_name,self.algorithm_name,suffix), 'w')
        p = Popen(["vl2vg"], stdout=file, stdin=PIPE,shell=True)
        vg = p.communicate(input=json.dumps(json_in))[0]
        if(verbose): print("Created " + file.name)
        file.close()


class VegaGraphBar(VegaGraphBase):
    """Class for converting json outputs of different algorithms to vega-specific bar graph json files.

    This class is a child class of VegaGraphBase and inherits all the methods and variables.

    Attributes:
        output_path: the output directory to write the vega-spec json files to.
        input_path: the input path containing the input json files to be processed.
        config_dir: the directory containing the json config files relevant to each plot type.
            Each config file will need to have a specific name of the format: '<plot type>_config.json'
        labels: a dictionary containing the relevant nouns required for naming the file and the axes of the
            plots created. The names dictionary should contain 5 keys and their corresponding values.
            They are:
                engine_name: the name of the engine used to run the algorithm (e.g. Gunrock). This is
                    used to name the output files.
                algorithm_name: the name of the algorithm (e.g. BFS). This is used to name the
                    output files.
                x_axis: the label for the x_axis
                y_axis: the label for the y_axis
                file_suffix: the suffix to put at the end of the file being generated.
                e.g. labels = {'engine_name':'g','algorithm_name':'BFS','x_axis':'Datasets','y_axis':'MTEPS','file_suffix':'0'}
        conditions_dict: a dictionary containing the conditions to limit the input files to a
            specific category. For instance choosing files that were outputs of a BFS algorith.
            For instance the following dictionary limits the inputs to BFS algorithms that are undirected and
            mark_predecessors is true:
            {"algorithm" : "BFS","undirected" : True ,"mark_predecessors" : True}
        axes_vars: a dictionary of the variables to be evaluated for the x and y axes. There are 2 keys: 'x' and 'y'.
            For instance:
            {'x':'dataset','y':'m_teps'} would specify to the program to plot m_teps (on y-axis) vs. dataset (on x-axis)

    """


    def __init__(self,output_path,input_path,config_dir,labels,conditions_dict,axes_vars):
        """Instantiate the input arguments. References the base class __init__ to instantiate recurring ones."""
        self.conditions_dict = conditions_dict
        self.axes_vars = axes_vars
        self.x_axis_label = labels['x_axis']
        self.y_axis_label = labels['y_axis']
        super(VegaGraphBar,self).__init__(output_path,input_path,config_dir,labels)


    def parse_jsons(self):
        """Parses the input json files using Pandas.

        Returns: the json file to be written to file.
        """
        pandas_df = super(VegaGraphBar,self).parse_jsons()
        #restricted bar graph, based on conditions_dict provided
        df_restricted = pandas_df
        for key,value in self.conditions_dict.iteritems():
            df_restricted = df_restricted.loc[df_restricted[key]==value]

        # delete everything except dataset (index) and the desired variable
        df_restricted = pandas.DataFrame(df_restricted.set_index(self.axes_vars['x'])[self.axes_vars['y']])
        #turn dataset back to vanilla column instead of index
        df_restricted = df_restricted.reset_index()
        #complete vega-lite bar description
        bar = self.read_config()
        # add extracted data to json
        bar["data"] = {"values":df_restricted.to_dict(orient='records')}
        # add relevant attributes to y and x axes based on input data
        bar["encoding"]["y"]["field"]=self.axes_vars['y']
        bar["encoding"]["y"]["axis"] = {"title":self.y_axis_label}
        #check whether axis is quantitative or ordinal. add respective attributes to json
        for key in self.axes_vars:
            if(df_restricted[self.axes_vars[key]].dtype=='float64'):
                bar["encoding"][key]["type"]="quantitative"
            else:
                bar["encoding"][key]["type"]="ordinal"
        bar["encoding"]["x"]["field"]=self.axes_vars['x']
        bar["encoding"]["x"]["axis"] = {"title":self.x_axis_label}

        #return json
        return bar
