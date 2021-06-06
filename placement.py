from collections import defaultdict
from copy import deepcopy as dc
import sys, getopt
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from numpy import ceil, sqrt, zeros, exp, ones
from random import randint, choice, random, shuffle
import pickle
import time
# global variable that contains the data of the blocks
dataBase = {}							# a dictionary of blocks

def save_object(obj, filename):
	with open(filename, 'wb') as output:  # Overwrites any existing file.
		pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

# Pin Class Type used for routing
class Pin():
	def __init__(self, pin):
		self.pin = pin
		self.available = 1

# create a gates class
class BlockData():
	# a class meant to stores all details of gates
	# representing IP Blocks
	# the (0,0) of each block will be on the bottom left
	def __init__(self, name, i, o, x, y, pins, supplyVoltage, ground):
		
		self.name = name 				# unique name of the gate/block
		self.inputSize = int(i)			# number of inputs
		self.outputSize = int(o)			# number of outputs
		self.dim = (int(x),int(y))		# dimension of the block
		self.pins = pins.split(',')		# location of all the pins
		# list of available input and output pins used for routing
		self.InputPins = [Pin(p) for p in self.pins[:int(i)]]
		self.OutputPins = [Pin(p) for p in self.pins[-int(o):]]
		self.high = supplyVoltage		# pin location of vdd
		self.gnd = ground 				# pin loc of the ground pin


# class of an instance of a block
class Block(BlockData):
	def __init__(self, blocktype, count, inputs, outputs):
		if blocktype not in dataBase.keys():
			raise Exception(' '.join(['Unknown Block encountered:',blocktype]))
		self.__dict__ = dc(dataBase[blocktype].__dict__)
		self.name += str(count)			# name of this instance of the gate/block
		self.id = None
		self.inputs = inputs 			# input nodes/points
		self.outputs = outputs 			# output nodes/points
		self.facing = 0					# the direction faced by the block
										# default is 0. 
										# 0-> north, 1-> east, 2-> south, 3-> west
		self.pos = (0,0)				# position of the block on the circuit w.r.t (0,0) of the block 


# create a netlist class
class Circuit():
	# a class maintaining the locations and orientations of all the blocks
	# represents a circuit with input and output
	def __init__(self):
		self.graph = defaultdict(list)				# unidirectional graph with gates as nodes
		self.blockCount = defaultdict(int)			# contains the frequency of each block
		
		self.blocks = {}							# contains all the block instances with ids as index
		self.pos = {}								# contains only locations of the blocks, used for simulated annealing
		self.pos_best = None
		self.pos_old = None
		self.edges = []								# contains edges
		# self.vertices = None						
		# self.adjMat = None
		self.inputs = set()							# inputs to the circuit
		self.outputs = set()							# outputs to the circuit
		self.W, self.H = 0, 0						# width and height of the circuit in pixels
		self.gap = 0								# gap between two consecutive blocks in pixels
		self.img = None 							# image for visualization
		self.grid = None 							# grid for routing
		self.scale = 10

	def addEdge(self,u,v,edgeID,w):
		if v in self.graph[u]:
			for i in range(len(self.edges)):
				if self.edges[i][0]==u and self.edges[i][1]==v:
					self.edges[i][2]+=1
					return
		self.graph[u].append(v)
		self.edges.append([u,v,edgeID,w])

	def getWeight(self,u,v):
		for i in self.edges:
			if (i[0]==u and i[1]==v) or (i[0]==v and i[1]==u):
				return i[2]


# read the config file to get the details about the gates
	def readConfigFile(self, file):
		with open(file) as f:
			lines = f.readlines()
			for line in lines:
				if line[0]=='#':
					continue
				line = line.rstrip('\n')
				if line[:4]=='gate':
					line = line[5:].split(' ')
					b = BlockData(line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7])
					dataBase[line[0]]=b
			f.close()

# read the netlist file to get the circuit
	def readNetlist(self, file):
		with open(file) as f:
			lines = f.readlines()
			count = 0
			index = 1
			for line in lines:
				if line[0]=='#' or line[0]=='\n':
					continue
				line = line.rstrip('\n')
				if line[:5]=='input' or line[:5]=='INPUT':
					
					line = line[6:].replace(' ','')
					for i in line.split(','):
						self.inputs.add(i)
				elif line[:6]=='output' or line[:6]=='OUTPUT':
					line = line[7:].replace(' ','')
					for i in line.split(','):
						self.outputs.add(i)
				else:
					
					line = line.split(' ')
					e = line.index('=')
					self.blockCount[line[e+1]]+=1
					try:
						
						b = Block(line[e+1],self.blockCount[line[e+1]],line[e+2:],line[:e])
						b.id = index
						self.blocks[index] = b
						index += 1
					except Exception as e:
						print(e)
						print('Something wrong in line {}'.format(count))
						break

				count += 1
			f.close()
		l = int(ceil(sqrt(index-1)))
		self.img = zeros([l,l])
		self.W = self.H = l




# get graph from the circuit
	def getGraphFromCircuit(self):
		tempo = [[],[]]				# stores the outputs of the blocks that might be the input of another blocks
		for block in self.blocks.values():
			for o in block.outputs:
				tempo[0].append(block.id)
				tempo[1].append(o)
		edgeID = 0
		for block in self.blocks.values():
			for i in block.inputs:
				if i in tempo[1]:
					self.addEdge(tempo[0][tempo[1].index(i)],block.id,edgeID,1)
					edgeID += 1
	

	def swap(self):
		x = randint(1,list(self.pos.keys())[-1])
		y = randint(1,list(self.pos.keys())[-1])
		while x==y:
			y = randint(1,list(self.pos.keys())[-1])
		self.pos[x], self.pos[y] = self.pos[y],self.pos[x]

# cost is the sum of the HPWLs of all the nets
# A net is k-point if the output of one gate is connected to the input of k-1 other gates
	def getCost(self):
		cost = 0
		for gate in self.graph.keys():
			xmin = min(self.pos[gate][0],min([self.pos[b][0] for b in self.graph[gate]]))
			ymin = min(self.pos[gate][1],min([self.pos[b][1] for b in self.graph[gate]]))
			xmax = max(self.pos[gate][0],max([self.pos[b][0] for b in self.graph[gate]]))
			ymax = max(self.pos[gate][1],max([self.pos[b][1] for b in self.graph[gate]]))
			cost += xmax-xmin + ymax-ymin
		return cost

	def simulatedAnnealing(self, visualize=False):
		cost_list=[]
		T = 1000000
		k = 20
		bestCost = float('inf')
		# place the blocks randomly
		loc = list(range(self.W*self.H))
		shuffle(loc)
		for gate in self.blocks.keys():
			i = loc.pop(0)
			self.pos[gate] = [i//self.W,i%self.W]
		cost = self.getCost()
		print('initial cost: ',cost,'\n')
		if visualize:
			self.visualizeCircuit()
		while T>0.1:
			for i in range(k):
				self.pos_old = dc(self.pos)
				self.swap()
				presentcost=self.getCost()
				
				deltaCost = presentcost - cost
				if deltaCost<=0 or random()<exp(-deltaCost/T):
					cost_list.append(cost)
					if cost<bestCost:
						self.pos_best = dc(self.pos)
						bestCost = cost
					cost += deltaCost
				else:
					self.pos = dc(self.pos_old)
			T = 0.98*T
		plt.plot(cost_list)
		plt.title("Plot of cost at each iteration")
		plt.xlabel("Itertions")
		plt.ylabel("Cost")
		plt.show()
		
		print('final cost: ',bestCost)
		if visualize:
			self.visualizeCircuit('best')
		# return the grid of blocks
		self.genGrid()

	def visualizeCircuit(self, mode=None):
		self.img = ones([self.W*self.scale*2 + 1, self.H*self.scale*2 + 1,3])
		fig = plt.figure()
		ax = fig.add_subplot(111)
		ax.imshow(self.img, interpolation='nearest')
		if mode=='best':
			for gate in self.pos_best.keys():
				# plot rectangles
				ax.add_patch(Rectangle([(2*self.pos_best[gate][0]+0.5)*self.scale,(2*self.pos_best[gate][1]+0.5)*self.scale],self.blocks[gate].dim[0],self.blocks[gate].dim[1],ec='g',fc='none', lw=1))
				# add text
				# ax.text((2*self.pos_best[gate][0]+1)*self.scale,(2*self.pos_best[gate][1]+1)*self.scale,self.blocks[gate].name,fontsize=10)
			for edge in self.edges:
				# plot lines
				ax.plot([(2*self.pos_best[edge[0]][0]+1)*self.scale,(2*self.pos_best[edge[1]][0]+1)*self.scale],[(2*self.pos_best[edge[0]][1]+1)*self.scale,(2*self.pos_best[edge[1]][1]+1)*self.scale],color='green')
			plt.savefig('Placement_best.png')
		else:
			for gate in self.pos.keys():
				# plot rectangles
				ax.add_patch(Rectangle([(2*self.pos[gate][0]+0.5)*self.scale,(2*self.pos[gate][1]+0.5)*self.scale],self.blocks[gate].dim[0],self.blocks[gate].dim[1],ec='r',fc='none', lw=1))
				# add text
				# ax.text((2*self.pos[gate][0]+1)*self.scale,(2*self.pos[gate][1]+1)*self.scale,self.blocks[gate].name,fontsize=10)
			for edge in self.edges:
				# plot lines
				ax.plot([(2*self.pos[edge[0]][0]+1)*self.scale,(2*self.pos[edge[1]][0]+1)*self.scale],[(2*self.pos[edge[0]][1]+1)*self.scale,(2*self.pos[edge[1]][1]+1)*self.scale],color='red')
			plt.savefig('Placement.png')

	def genGrid(self):
		self.grid = zeros([self.W*self.scale*2 + 1, self.H*self.scale*2 + 1])
		fig = plt.figure()
		ax = fig.add_subplot(111)
		for gate in self.pos_best.keys():
			i = int((2*self.pos_best[gate][0]+1)*self.scale)
			j = int((2*self.pos_best[gate][1]+1)*self.scale)
			self.blocks[gate].pos = (i,j)
			# print(i,j,self.blocks[gate].dim[0],self.blocks[gate].dim[1])
			self.grid[i:i+self.blocks[gate].dim[0],j:j+self.blocks[gate].dim[1]] = 1
		
			ax.text(j,i,self.blocks[gate].name,fontsize=10,color='red')
		ax.imshow(self.grid, interpolation='nearest',cmap='gray')
		plt.savefig('grid.png')







def main():
	try:
		opts, _ = getopt.getopt(sys.argv[1:],"hc:n:")
	except getopt.GetoptError:
		print('Usage: \n\tpython '+str(__file__)+' -c config.txt -n netlist.txt\n')
		sys.exit(2)
	if len(opts)<2:
		print('Usage: \n\tpython '+str(__file__)+' -c config.txt -n netlist.txt\n')
		sys.exit()
	for opt, arg in opts:
		if opt=='-c':
			config = arg
		elif opt=='-n':
			netlist = arg
	# print(config,netlist)
	C = Circuit()
	print('reading config file...')
	C.readConfigFile(config)
	print('reading netlist file...')
	C.readNetlist(netlist)
	print('generating graph from netlist...')
	C.getGraphFromCircuit()
	# [print(b.pins) for b in C.blocks.values()]
	# [print(b.OutputPins[0].pin) for b in C.blocks.values()]
	# for b in C.blocks.values():
	# 	for p in b.InputPins:
	# 		print(p.pin,end=' ')
	# 	print()
	# print(len(C.edges))
	# print(C.edges)
	print('Performing Placement...')
	C.simulatedAnnealing()
	print('Saving Circuit Class Object as a pickle file...')
	save_object(C,'s27_placed.pkl')
	# [print(C.blocks[k].name,C.pos[k]) for k in C.blocks.keys()]
	# [print(x) for x in C.pos_best.values()]

if __name__ == '__main__':
	t = time.time()
	main()
	print('Total Time taken: ',time.time()-t)
	print('Placement completed succesfully!!')
