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

import pandas
import numpy
import json  # built-in
import os   # built-in
from subprocess import Popen, PIPE, STDOUT  # built-in
# built-in #to make base class abstract
from abc import ABCMeta, abstractmethod

# Base class to produce vega-spec jsons


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
    __metaclass__ = ABCMeta

    # list containing all jsons
    __input_jsons = []


    def __init__(self, output_path, input_path, config_dir, labels):
        """Initis base class with provided atrributes."""
        self.output_path = output_path
        self.input_path = input_path
        self.config_dir = config_dir
        self.engine_name = labels['engine_name']
        self.algorithm_name = labels['algorithm_name']
        self.file_suffix = labels['file_suffix']
        # the graph type set as the name of the class
        self.graph_type = "base"

    def read_json(self):
        """Reads json files wiht the right specs into __input_jsons list

        Does not take any arguments.
        Does not return any variables.
        """
        # read in all json files in the input_path, that match the
        # algorithm_name and are not outputs
        for f in os.listdir(self.input_path):
            if(os.path.splitext(f)[1] == ".json") and (os.path.basename(f).startswith(self.algorithm_name)) and (not os.path.basename(f).startswith("_")):
                self.__input_jsons += [json.load(open(self.input_path + f))]

    def run(self, verbose=False):
        """calls the relevant methods to convert input jsons to vega-spec jsons

        Arguments:
            verbose: If True, prints out what is happening. Default=False.
        """
        from utils import write_to_file  # function to write json to file
        self.read_json()
        graph = self.parse_jsons()
        json = self.pipe_vl2vg(graph)
        return self.write_to_file(rawinput=json, filetype='json', output_path=self.output_path, engine_name=self.engine_name, algorithm_name=self.algorithm_name, suffix=self.file_suffix, verbose=verbose)

# TODO method to check whether config files exist. If not use default.

    def read_config(self):
        """Returns the json config file as a python object
        Uses self.graphtype , which is a string defining the type of graph, e.g. bar."""
        return json.load(open(self.config_dir + "/" + self.graph_type.lower() + "_config.json"))

    @abstractmethod
    def parse_jsons(self):
        """Parses the input json files using Pandas.

        Returns: a pandas dataframe containting the data processed from input jsons.
        """
        # store all data in a pandas DataFrame
        pandas_df = pandas.DataFrame(self.__input_jsons)
        return pandas_df

    def pipe_vl2vg(self, json_in):
        """Pipes the vega-lite json through vl2vg to generate the vega json output

        Returns: vega-spec json string"""
        p = Popen(["vl2vg"], stdout=PIPE, stdin=PIPE, shell=True)
        vg = p.communicate(input=json.dumps(json_in))[0]
        # f = open('log.json','w')
        # f.write(json.dumps(json_in))
        # f.close()
        return vg


class VegaGraphBarBase(VegaGraphBase):
    """Class for converting json outputs of different algorithms to vega-specific bar or scatter graph json files.

    This class is a child class of VegaGraphBase and inherits all the methods and variables.
    It serves as a base class to VegaGraphBar and VegaGraphScatter.

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

    def __init__(self, output_path, input_path, config_dir, labels, conditions_dict, axes_vars):
        """Instantiate the input arguments. References the base class __init__ to instantiate recurring ones."""
        self.conditions_dict = conditions_dict
        self.axes_vars = axes_vars
        self.x_axis_label = labels['x_axis']
        self.y_axis_label = labels['y_axis']
        super(VegaGraphBarBase, self).__init__(
            output_path, input_path, config_dir, labels)
        # the graph type set as the name of the class
        self.graph_type = "barbase"

    def parse_jsons(self):
        """Parses the input json files using Pandas.

        Returns: the json file to be written to file.
        """
        pandas_df = super(VegaGraphBarBase, self).parse_jsons()
        # restricted bar graph, based on conditions_dict provided
        df_restricted = pandas_df
        for key, value in self.conditions_dict.iteritems():
            df_restricted = df_restricted.loc[df_restricted[key] == value]

        # delete everything except dataset (index) and the desired variable
        df_restricted = pandas.DataFrame(df_restricted.set_index(
            self.axes_vars['x'])[self.axes_vars['y']])
        # turn dataset back to vanilla column instead of index
        df_restricted = df_restricted.reset_index()
        # complete vega-lite bar description
        bar = self.read_config()
        # add extracted data to json
        bar["data"] = {"values": df_restricted.to_dict(orient='records')}
        # add relevant attributes to y and x axes based on input data
        bar["encoding"]["y"]["field"] = self.axes_vars['y']
        bar["encoding"]["y"]["axis"] = {"title": self.y_axis_label}
        # check whether axis is quantitative or ordinal. add respective
        # attributes to json
        for key in self.axes_vars:
            if(df_restricted[self.axes_vars[key]].dtype == 'float64'):
                bar["encoding"][key]["type"] = "quantitative"
            else:
                bar["encoding"][key]["type"] = "ordinal"
        bar["encoding"]["x"]["field"] = self.axes_vars['x']
        bar["encoding"]["x"]["axis"] = {"title": self.x_axis_label}
        # return json
        return bar

class VegaGraphBar(VegaGraphBarBase):
    """Class for converting json outputs of different algorithms to vega-specific bar graph json files.

    This class is a child class of VegaGraphBarBase and inherits all the methods and variables, including those of VegaGraphBase.

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

    def __init__(self, output_path, input_path, config_dir, labels, conditions_dict, axes_vars):
        """Instantiate the input arguments. References the base class __init__ to instantiate recurring ones."""
        super(VegaGraphBar, self).__init__(
            output_path, input_path, config_dir, labels, conditions_dict, axes_vars)
        # the graph type set as the name of the class
        self.graph_type = "bar"

    def parse_jsons(self):
        """Parses the input json files using Pandas.

        Returns: the json file to be written to file.
        """
        return super(VegaGraphBar, self).parse_jsons()


class VegaGraphScatter(VegaGraphBarBase):
    """Class for converting json outputs of different algorithms to vega-specific scatter graph json files.

    This class is a child class of VegaGraphBar and inherits all the methods and variables, including those of VegaGraphBase.

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

    def __init__(self, output_path, input_path, config_dir, labels, conditions_dict, axes_vars):
        """Instantiate the input arguments. References the base class __init__ to instantiate recurring ones."""
        super(VegaGraphScatter, self).__init__(
            output_path, input_path, config_dir, labels, conditions_dict, axes_vars)
        # the graph type set as the name of the class
        self.graph_type = "scatter"

    def parse_jsons(self):
        """Parses the input json files using Pandas.

        Returns: the json file to be written to file.
        """
        return super(VegaGraphScatter, self).parse_jsons()


class VegaGraphHeatmap(VegaGraphBase):
    """ """
    def __init__(self,output_path,input_path,config_dir,labels,conditions_dict,axes_vars):
        """Instantiate the input arguments. References the base class __init__ to instantiate recurring ones."""
        self.conditions_dict = conditions_dict
        self.axes_vars = axes_vars
        self.x_axis_label = labels['x_axis']
        self.y_axis_label = labels['y_axis']
        super(VegaGraphHeatmap,self).__init__(output_path,input_path,config_dir,labels)
        self.graph_type = "heatmap"

    def parse_jsons(self):
        """Parses the input json files using Pandas.

        Returns: the json file to be written to file.
        """
        pandas_df = super(VegaGraphHeatmap, self).parse_jsons()
        # restricted bar graph, based on conditions_dict provided
        df_restricted = pandas_df
        for key, value in self.conditions_dict.iteritems():
            df_restricted = df_restricted.loc[df_restricted[key] == value]
        # delete everything except dataset (index) and the desired variable
        #df_restricted = pandas.DataFrame(df_restricted.set_index(self.axes_vars['x'])[self.axes_vars['y']])
        df_restricted = df_restricted[['dataset', 'm_teps', 'alpha', 'beta']]
        #rint is numpy's vectorized round to into
        df_restricted = df_restricted.assign(m_teps_rounded=numpy.rint(df_restricted['m_teps']))
        print(df_restricted)
        # complete vega-lite bar description
        heatmap = self.read_config()
        heatmap["data"] = {"values": df_restricted.to_dict(orient='records')}
        #print(heatmap)
        return heatmap
