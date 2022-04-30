# Placement-and-Routing
usage :
```sh
python placement.py -c c27.txt -n s27.txt
```
Details of the Config (c27.txt) file:
```
all the details about the blocks will be mentioned in the config file
gate name, no. of inputs, no. of outputs, dimensions, pin locations
the numbering of the sides

		0
		--
   	     3 |  | 1
		--
		2

say the not gate is of 4 x 4 size, then its pin locations can be given by 
00,01,02,03,10,11,12,13 ..... 33 

syntax 
<gate> <name> <number_of_inputs> <number_of_outputs> <x_dim> <y_dim> <pin_locations_separated_by_,> <pin_location_vdd> <pin_location_ground>
```
## Placement of ISCAS s298 netlist
![alt-text](https://github.com/SrikarSiddarth/Placement-and-Routing/blob/main/Placement_best_298.png)\
## Routing of ISCAS s27 netlist
![alt-text](https://github.com/SrikarSiddarth/Placement-and-Routing/blob/main/routing2.png)\

