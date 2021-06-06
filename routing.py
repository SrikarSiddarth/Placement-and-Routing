from placement import Circuit, Block, Pin
import Astar
import numpy as np
import sys, getopt
from copy import deepcopy as dc
import pickle
import matplotlib.pyplot as plt
from collections import defaultdict
from random import choice

class Route():
	def __init__(self):
		self.inputBlock = None
		self.outputBlock = None
		self.inputPin = None
		self.outputPin = None
		# self.fullPath = None
		# self.path excludes the uncommon paths from the net
		self.path = None


class Router(Circuit):
	def __init__(self,config,netlist):
		Circuit.__init__(self)
		# self.readConfigFile(config)
		# self.readNetlist(netlist)
		
		# self.getGraphFromCircuit()
		# self.simulatedAnnealing()

		# loading saved placement object
		with open('s27_placed.pkl', 'rb') as i:
			self.__dict__ = dc(pickle.load(i).__dict__)
		# [print(b.name, b.inputs, b.outputs) for b in self.blocks.values()]
		self.grid_orig = dc(self.grid)				# contains the initial configuration
		self.grid_route = dc(self.grid)				# this layer contains the routing
		self.clearance = 4							# clearance for the block
		self.pinClearance = 3 						# clearance for the pin
		self.routes = []
		self.removed_routes = []					# stores the start and end of the removed paths
		self.net = defaultdict(set)

	def route(self):
		# route all the block inputs to the block outputs
		# Assuming only single outputs for now
		route = Astar.Astar()
		route.rows = self.grid.shape[0]
		route.columns = self.grid.shape[1]
		fig = plt.figure()
		ax = fig.add_subplot(111)
		count = 0
		routeCount = 0
		# sort the edges based on half perimeter
		self.edges.sort(key=self.halfPerimeter, reverse=True)
		# self.edges.sort(key=self.halfPerimeter)
		# the outputs of the input block go into the inputs of the output block
		while True:
			try:
				for currRoute in range(len(self.edges)):

					# when rerouting, then continue from the most recent routed block
					if currRoute < routeCount:
						continue

					# regenerating clearance grid as the union of routing layer and the grid
					self.grid = dc(self.grid_route)

					

					# generating clearance for blocks
					for b in self.blocks.keys():
						# expand all blocks except the input and output blocks
						if b==self.edges[currRoute][0] or b==self.edges[currRoute][1]:
							continue
						# convert the expanded part to non reachable
						x1, x2 = self.blocks[b].pos[0] - self.clearance, self.blocks[b].pos[0] + self.blocks[b].dim[0] + self.clearance
						y1, y2 = self.blocks[b].pos[1] - self.clearance, self.blocks[b].pos[1] + self.blocks[b].dim[1] + self.clearance
						self.grid[x1:x2,y1:y2] = 1

					r = Route()
					r.inputBlock = self.blocks[self.edges[currRoute][0]]
					r.outputBlock = self.blocks[self.edges[currRoute][1]]


					print('route count: ',currRoute)
					print('routing: ',self.blocks[self.edges[currRoute][0]].name,' to ',self.blocks[self.edges[currRoute][1]].name)
					r.inputPin = self.blocks[self.edges[currRoute][0]].OutputPins[0]
					
					selectFlag = 1
					pinCount = 0
					numOfInputPins = self.blocks[self.edges[currRoute][1]].inputSize

					# randomly selecting the pin
					r.outputPin = choice(self.blocks[self.edges[currRoute][1]].InputPins)
					
					for p in self.blocks[self.edges[currRoute][1]].InputPins:
						print(p.pin, p.available)
						if p == r.outputPin:
							selectFlag = 0
						else:
							# generating clearance spots for gates with multiple inputs of the output gate
							x = self.blocks[self.edges[currRoute][1]].pos[0]+int(p.pin[1])
							y = self.blocks[self.edges[currRoute][1]].pos[1] - 1

							if selectFlag:								
								self.grid[x,y - 2*pinCount-self.pinClearance+1:y+1] = 1
								print(x,y - 2*(pinCount)-1)
							else:
								print(x,y - 2*(numOfInputPins-pinCount-1)-1)
								self.grid[x,y - 2*(numOfInputPins-pinCount-1)-self.pinClearance+1:y+1] = 1
						pinCount += 1

					# creating clearance at the outputs of the output gate
					pinCount = 0
					numOfOutputPins = self.blocks[self.edges[currRoute][1]].outputSize
					for pin in self.blocks[self.edges[currRoute][1]].OutputPins:
						x = self.blocks[self.edges[currRoute][1]].pos[0]+int(pin.pin[1])
						y = self.blocks[self.edges[currRoute][1]].pos[1] + self.blocks[self.edges[currRoute][1]].dim[1] + 1
						self.grid[x,y-1:y + 2*(numOfOutputPins-pinCount-1)+self.pinClearance -1] = 1
						pinCount += 1

					# creating clearance at the inputs of the input gate
					pinCount = 0
					numOfInputPins = self.blocks[self.edges[currRoute][0]].inputSize
					for p in self.blocks[self.edges[currRoute][0]].InputPins:
						x = self.blocks[self.edges[currRoute][0]].pos[0]+int(p.pin[1])
						y = self.blocks[self.edges[currRoute][0]].pos[1] - 1
						self.grid[x,y -self.pinClearance:y+1] = 1

					print('input pin: ',r.inputPin.pin)
					print('output pin: ', r.outputPin.pin)
					# select the outer pin that is closer to the  input pin
					# if self.blocks[self.edges[0]].pos[0]>self.blocks[self.edges[1]].pos[0]:
						# outputPin = 
					



					start = [self.blocks[self.edges[currRoute][0]].pos[0]+int(r.inputPin.pin[1])]
					print('input block location: ',self.blocks[self.edges[currRoute][0]].pos)
					print('output block location: ',self.blocks[self.edges[currRoute][1]].pos)



					if r.inputPin.pin[0]=='1':
						start.append(self.blocks[self.edges[currRoute][0]].pos[1] + self.blocks[self.edges[currRoute][0]].dim[1] )
						print('start: ',start)
					elif r.inputPin.pin[0]=='3':
						start.append(self.blocks[self.edges[currRoute][0]].pos[1] - 1)

					end = [self.blocks[self.edges[currRoute][1]].pos[0]+int(r.outputPin.pin[1])]
					if r.outputPin.pin[0]=='1':
						end.append(self.blocks[self.edges[currRoute][1]].pos[1] + self.blocks[self.edges[currRoute][1]].dim[1] + 1)
					elif r.outputPin.pin[0]=='3':
						end.append(self.blocks[self.edges[currRoute][1]].pos[1] - 1)
						print('end: ',end)


					if len(self.net[self.edges[currRoute][0]])>0:
						print('Continuation of Net')
						for point in self.net[self.edges[currRoute][0]]:
							self.grid[point[0],point[1]]=2
					else:
						self.grid[start[0],start[1]] = 2
					self.grid[end[0],end[1]] = 3

					ax.imshow(self.grid, interpolation='nearest',cmap='gray')
					plt.savefig('route/debug_grid_'+str(count)+'.png')
					

					route.reInit()
					route.init_grid(self.grid)
					# main routing process
					route_path, route_length = route.search()
					# routing completed

					# disabling the pins for further use
					r.outputPin.available = 0
					r.inputPin.available = 0

					route_path = [tuple(start)] + route_path
					# r.fullPath = dc(route_path)
					print('route: ',route_path)
					for point in route_path:
						self.grid_route[point[0],point[1]] = 1
					
					route_path = set(route_path).difference(self.net[self.edges[currRoute][0]])
					r.path = dc(route_path)
					self.net[self.edges[currRoute][0]] = self.net[self.edges[currRoute][0]].union(route_path)
					print('count: ',count)
					# if count>3:
					# 	print('net: ',self.net[self.edges[currRoute][0]])

					ax.imshow(self.grid_route, interpolation='nearest',cmap='gray')
					plt.savefig('route/grid_'+str(count)+'.png')
					count += 1
					self.routes.append(r)

			except Exception as e:
				# print('routing was not successful due to: ', end='')
				print(e)
				
				routeCount = currRoute - 1
				for k in reversed(range(currRoute)):
					if self.edges[k][2] in self.removed_routes:
						self.edges[k-1],self.edges[k] = self.edges[k],self.edges[k-1]
				self.edges[currRoute-1],self.edges[currRoute] = self.edges[currRoute],self.edges[currRoute-1]
				r = self.routes.pop(-1)

				# print('removing previous route and rerouting the current.')
				for point in r.path:
						self.grid_route[point[0],point[1]] = 0
				# self.net[self.edges[i-1][0]].difference_update(r.path)
				self.net[self.edges[currRoute][0]] = {(x,y) for (x,y) in self.net[self.edges[currRoute][0]] if (x,y) not in r.path}
				# if count>3:
				# 	print('path to be removed: ',r.path)
				# 	print('net after removal: ',self.net[self.edges[i][0]])

				# adding the route ID to the removed edges array
				self.removed_routes.append(self.edges[routeCount][2])
				self.updatePins(currRoute-1)
				continue

			
			print('Routing completed!!')
			break


	def updatePins(self, i):

		# inputs of the output pin
		for p in self.blocks[self.edges[i][1]].InputPins:
			x = self.blocks[self.edges[i][1]].pos[0]+int(p.pin[1])
			y = self.blocks[self.edges[i][1]].pos[1] - 1
			if self.grid_route[x,y]:
				p.available = 0
			else:
				p.available = 1

		# outputs of the input pin
		for p in self.blocks[self.edges[i][0]].OutputPins:
			x = self.blocks[self.edges[i][0]].pos[0]+int(p.pin[1])
			y = self.blocks[self.edges[i][0]].pos[1] + self.blocks[self.edges[i][0]].dim[1]
			if self.grid_route[x,y]:
				p.available = 0
			else:
				p.available = 1




	def halfPerimeter(self,edge):
		return abs(self.blocks[edge[0]].pos[0]-self.blocks[edge[1]].pos[0]) + abs(self.blocks[edge[0]].pos[1]-self.blocks[edge[1]].pos[1])

		

	def debug_route(self):
		# test route between G0 and G14
		self.grid[0,10] = 2
		block = 2
		print(self.blocks[block].pos[0]+1,self.blocks[block].pos[1]-1)
		self.grid[self.blocks[block].pos[0]+1,self.blocks[block].pos[1]-1] = 3
		route = Astar.Astar()
		route.rows = self.grid.shape[0]
		route.columns = self.grid.shape[1]
		route.init_grid(self.grid)
		route_path, route_length = route.search()
		print('route length: ',route_length)
		# route_path = [[0,10]]+route_path
		# print(route_path)
		for point in route_path:
			self.grid[point[0],point[1]] = 1
		# print(self.grid.shape)
		fig = plt.figure()
		ax = fig.add_subplot(111)
		ax.imshow(self.grid, interpolation='nearest',cmap='gray')
		plt.savefig('route/grid_test.png')
		# print('plot')
		



if __name__ == '__main__':
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

	R = Router(config,netlist)
	R.route()
	# R.debug_route()
	
	