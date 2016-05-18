Groutrian diagram generator. Plots energy level scheme from a given data file.

------------
Data File format
------------
The format of the data file is two columns. The first is the energy of the level, and the second
is the label for the level. The default format is comma separated values, but the delimiter 
character may be set using --separator argument.
	---------
	label format
	---------
		The format for the labels is in a pseudo LaTeX style code for the term
		symbols. The ground state of hydrogen, for example, is:
		1^2S_1/2
		The program will attempt to read the j (total resultant angular momentum)
		value, n (principle quantum number) value, and l (orbital angular momentum
		quantum number)	value from this label, so it must be properly formatted
		for the dipole and quadrupole options to work.

The data file can also contain options on how to format the graph.
	---------
	Format Options
	---------
	Options can also be specified in the data file on a line separate from a level definition.
	
	Format parameters:
	
	$TITLE=Example Graph Title
	$SCALE=Y Axis Unit

---------
Specifying Transitions
---------
You can either generate transitions automatically using the --dipole or --quadrupole arguments,
or you can specify them explicitly in the data file

	----------
	Example Transition
	----------
	This will include in the level diagram a transition from the state listed first to
	the state listed third with the label "Some Transition From Ground", in blue color
	and also showing the transition wavelength:

	$TRANSITION,0,2,$LABEL=Some Transition From Ground,$COLOR=blue,$SHOW-NM=1

------------
Files included in this repo
------------
-levelTest.py
	Short script to illustrate basic workings. No datafile is loaded and everything is
	defined in the script. Easy to use, but limited.
-groutrian.py
	Main program. Loads data and parameters from input file.
-data_files/
	Some example input files that can be loaded using the --input argument
