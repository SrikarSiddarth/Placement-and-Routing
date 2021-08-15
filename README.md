# Placement-and-Routing
usage :
```sh
python placement.py -c c27.txt -n s27.txt
```
Details of the Config file:
```
all the details about the circuit will be mentioned here
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
<gate> <name> <#i> <#o> <#x> <#y> <pin_locations_separated_by_,> <pin_location_vdd> <pin_location_ground>
```
