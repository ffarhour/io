# io Scripts

This folder contains the scripts to generate visual representation of graph engine outputs.

The main scripts are listed below, with a brief description of their functionality:
* **text2json.py**: Parses the engine outputs (in txt format) and generates jsons containing important information regarding the output results.
* **testvl.py**: A test script that uses the engine output jsons (converted with text2json.py) to generate vega-spec jsons to be able to visualize the data.
* **json2vega.py**: Converts JSON outputs from graph algorithms to vega-spec json files to be plotted.
* **test_json2vega.py**: Sample code to test json2vega.py. Contains sample code that shows how to call the functions in json2vega.py as intended.

#### List of Dependencies:
* python:
	* pandas (pip install pandas)
	* numpy (pip install numpy)
* nodejs:
	* vega (sudo npm install vega)
	* vega-lite (sudo npm install vega-lite)

## How to generate vega-spec JSONs from input JSONs
Note that the following assumes that text2json.py has already been run to generate the JSON files containing the outputs of the graph engines.

One can plot a specific graph by using vega. Vega docs can be found at https://github.com/vega/vega/wiki .
The first step is to generate JSONs with a vega format. In order to do so you will need to use **json2vega.py**. Once the JSONs are created, one can simply use the command vg2png or vg2svg to generate the plot from the JSON.

The main file to look at is json2vega.py which takes in json outputs in a specific folder and spits out a graph based on your preferences.

#### Summary of what the code does and how it is structured

* There is a base class, which contains the main methods used for file IO, plus some other functionalities that would overlap across child classes
* The child classes which inherit all the methods of the base class will be responsible for the specific details of each type of graph that needs to be outputted. So there is a child class for every type of graph to be made. At the moment there is only 1 child class for creating bar graphs.
* Each child class has a set of attributes, which are required for construction:
	* **output_path**: the output directory to write the vega-spec json files to.
	* **input_path**: the input path containing the input json files to be processed.
	* **config_path**: the directory containing the json config files relevant to each plot type.
		Each config file will need to have a specific name of the format: '<plot type>\_config.json'
	* **labels**: a dictionary containing the relevant nouns required for naming the file and the axes of the plots created. The names dictionary should contain 5 keys and their corresponding values. They are:
		* **engine_name**: the name of the engine used to run the algorithm (e.g. Gunrock). This is used to name the output files.
		* **algorithm_name**: the name of the algorithm (e.g. BFS). This is used to name the output files.
		* **x_axis**: the label for the x_axis
		* **y_axis**: the label for the y_axis
		* **file_suffix**: the suffix to put at the end of the file being generated.

	e.g. labels = {'engine_name':'g','algorithm_name':'BFS','x_axis':'Datasets','y_axis':'MTEPS','file_suffix':'0'}

	* **conditions_dict**: a dictionary containing the conditions to limit the input files to a specific category. For instance choosing files that were outputs of a BFS algorith.

		For instance the following dictionary limits the inputs to BFS algorithms that are undirected and mark_predecessors is true:
		`{"algorithm" : "BFS","undirected" : True ,"mark_predecessors" : True}`
	* **axes_vars**: a dictionary of the variables to be evaluated for the x and y axes. There are 2 keys: 'x' and 'y'.For instance:
	`{'x':'dataset','y':'m_teps'} would specify to the program to plot m_teps (on y-axis) vs. dataset (on x-axis)`

* In order to generate the vega-spec JSONs, the program takes in a config file, one specific for each type of graph. The _config file_ which is  a json with vega-lite specs, details how the graph should look visually!
* The python library **argparse** is used to process input commandline arguments. It is very easy to implement new arguments.
* as an extra touch  a class for coloring the commandline outputs with ANSI colors is added!!

#### How to use json2vega.py
1. import json2vega
2. Create an object of a child class by calling the class name. Make sure you do so by calling the constructor with the above attributes as arguments.

	For example, in order to create a bargraph, create an object of `VegaGraphBar`:
	```
	import json2vega
	# Create required arguments and instantite bar class object for testing.
	conditions = {"algorithm" : "BFS","undirected" : True ,"mark_predecessors" : True}
	axes_vars = {'x':'dataset','y':'m_teps'}
	labels = {'engine_name':'g','algorithm_name':'BFS','x_axis':'Datasets','y_axis':'MTEPS','file_suffix':'0'}
	bar1 = json2vega.VegaGraphBar(output_path="",input_path="",config_dir="",labels=labels,conditions_dict=conditions,axes_vars=axes_vars)
	```
	The above code imports json2vega, creates the required dictionaries for **labels**,**conditions** and **axes_vars**, and creates an object of type **VegaGraphBar** named **bar1**.
	Note that it is assumed that the output_path, input_path, and config_dir are at current directory.
	Furthermore, the engine_name is given as "g", and algorithm_name is given as "BFS".
3. Read the input JSONs by calling the `read_json()` method of the object **bar1**:

	```
	bar1.read_json()
	```
4. Parse the JSONs by calling the `parse_jsons()` method of the object **bar1**:

	```
	parsed = bar1.parse_jsons()
	```
5. Write the output vega-spec JSONs to file by calling the `write_json(json_in,suffix="",verbose=True)` method of the object **bar1**.

	```
	bar1.write_json(parsed,"0")
	```

	Note that the parsed JSONs (**bar**) are passed in as an argument to the `wirte_json` method. The second argument passed is the suffix of the file being written. In this case it is "0".

**Complete example**:
```
import
conditions = {"algorithm" : "BFS","undirected" : True ,"mark_predecessors" : True}
axes_vars = {'x':'dataset','y':'m_teps'}
bar1 = json2vega.VegaGraphBar(args.o,args.d,"config_files/","g","BFS",conditions,axes_vars)
bar1.read_json()
bar = bar1.parse_jsons()
bar1.write_json(bar,"0")
```

#### How to use json2vega.py part II
A new method has been implemented to make it easier to use json2vega.py. Now, instead of reading, parsing and writing manually, one can call the method `run` to do all that. Example given below:

**Complete example**:
```
import
conditions = {"algorithm" : "BFS","undirected" : True ,"mark_predecessors" : True}
axes_vars = {'x':'dataset','y':'m_teps'}
names = {'engine_name':'g','algorithm_name':'BFS','x_axis':'Datasets','y_axis':'MTEPS','file_suffix':'0'}
bar1 = json2vega.VegaGraphBar(output_path=args.o,input_path=args.d,config_dir="config_files",labels=names,conditions_dict=conditions,axes_vars=axes_vars)
bar1.run(verbose=True)
```

Note that the `run` method takes in 1 argument, which is **verbose**. This specifies whether to output what is happening to terminal. By default verbose is off.
