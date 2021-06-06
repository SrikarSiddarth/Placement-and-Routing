import cv2
import numpy as np
import heapq
from copy import deepcopy as dc




class Cell(object):
	def __init__(self, x, y, reachable):
		# setting some parameters for each cell
		self.reachable = reachable
		self.x = x
		self.y = y
		self.parent = None
		self.cost = 0
		self.heuristic = 0
		# net_cost=cost+heuristic
		self.net_cost = 0

	def __lt__(self,other):
		# if comparing equal elements
		return True



class Astar(object):
	def __init__(self):
		# list of unchecked neighbour cells
		self.open = []
		# keeps cells with lowest total_cost at top
		heapq.heapify(self.open)
		# list of already checked cells
		self.closed = set()
		# list of neighbour cells
		self.cells = []
		# no of rows and columns in grid
		self.rows = 0
		self.columns = 0
		self.best_cost = float('inf')
		self.weight = 0.5
		# self.bends = 0

	def reInit(self):
		# list of unchecked neighbour cells
		self.open = []
		# keeps cells with lowest total_cost at top
		heapq.heapify(self.open)
		# list of already checked cells
		self.closed = set()
		# list of neighbour cells
		self.cells = []

	def init_grid(self, grid):
		self.start = []
		for i in range(self.rows):
			for j in range(self.columns):
				# detecting the obstacles
				# detecting the start and end
				if grid[i,j] == 2:
					reachable = True
				elif grid[i,j] == 3:
					reachable = True
				elif (grid[i,j] == 1) or (i >0 and i<self.rows-1 and grid[i+1,j] ==1)  or (j >0 and j<self.columns-1 and grid[i,j+1] ==1)  :
					reachable = False
				elif (grid[i,j] == 1) or (i >0 and i<self.rows-1 and grid[i-1,j] ==1)  or (j >0 and j<self.columns-1 and grid[i,j-1] ==1) :
					reachable = False
				elif (grid[i,j] == 1) or (j >0 and j<self.columns-1 and i >0 and i<self.rows-1 and grid[i-1,j-1] ==1)  or (i >0 and i<self.rows-1 and j >0 and j<self.columns-1 and grid[i+1,j-1] ==1) or (j >0 and j<self.columns-1 and i >0 and i<self.rows-1 and grid[i-1,j+1] ==1)  or (i >0 and i<self.rows-1 and j >0 and j<self.columns-1 and grid[i+1,j+1] ==1) :
					reachable = False
				else:
					reachable = True
				self.cells.append(Cell(i, j, reachable))

				# detecting the start and end
				if(grid[i,j] == 2):
					self.start.append(self.cell(i, j))
					reachable = True
				if(grid[i,j] == 3):
					# print('om')
					self.end = self.cell(i, j)
					reachable = True

				
				

	def cell(self, x, y):
		# returns the location to identify each cell
		return self.cells[x*self.rows+y]

	def cell_heuristic(self, cell):
		# returns the heuristic for astar algo
		# print(cell.x,self.end.x,cell.y,self.end.y)
		return abs(cell.x-self.end.x)+abs(cell.y-self.end.y)

	def neighbour(self, cell):
		cells = []
		# returns a list of neigbours of a cell
		# print(cell.x,cell.y)
		if cell.x < self.columns - 1:
			cells.append(self.cell(cell.x+1, cell.y))
		if cell.x > 0:
			cells.append(self.cell(cell.x-1, cell.y))
		if cell.y < self.rows-1:
			cells.append(self.cell(cell.x, cell.y+1))
		if cell.y > 0:
			cells.append(self.cell(cell.x, cell.y-1))
		return cells

	def update_cell(self, adj, cell):
		# update the details about the selected neigbour cell
		# print('cell cost: ',cell.cost)
		# debug = 'om'
		if cell.parent is not None:
			# debug = 'bheem'
			if abs(cell.parent.x - adj.x)==1 and abs(cell.parent.y - adj.y)==1:
				# bend cost of 2 units
				adj.cost = cell.cost + 100
				# debug = 'kleem'
				# self.bends += 1
			else:
				# print(abs(cell.parent.x - adj.x),abs(cell.parent.y - adj.y))
				adj.cost = cell.cost + 1
		else:
			adj.cost = cell.cost + 1
		adj.heuristic = self.cell_heuristic(adj)
		adj.parent = cell
		# if cell.parent is not None:
		# 	if abs(cell.parent.x - adj.x)==1 and abs(cell.parent.y - adj.y)==1:
		# 		print(adj.cost, debug)
		# print('adj cost: ',adj.cost)
		# print('heuristic cost: ',adj.heuristic)
		adj.net_cost = self.weight*adj.cost + (1-self.weight)*adj.heuristic
		# adj.net_cost = adj.heuristic
		# print(adj.net_cost)

	def tracePathCost(self,cell):
		cost = 0
		while cell.parent is not None:
			cost += cell.cost
			# print(cell.x,cell.y,cell.cost,cell.heuristic,cell.net_cost)
			cell = cell.parent
		return cost

	def display_path(self):
		# list for storing the path
		route_path = []
		# flag to determine length of path
		count = 0
		cell = self.end
		total_cost = 0
		while cell.parent is not None:
			# storing the parents in list from end to start
			route_path.append((cell.x, cell.y))
			cell = cell.parent
			# print(cell.cost, cell.heuristic, cell.net_cost)
			total_cost += cell.net_cost
			count += 1
		# print('total cost: ',total_cost)
		return route_path, count

	def search(self):
		# pushing the first element in open queue
		for c in self.start:
			heapq.heappush(self.open, (c.net_cost, c))
		while(len(self.open)):
			#  selecting the path with least cost
			net_cost, cell = heapq.heappop(self.open)
			# print('tracked cost: ',self.tracePathCost(cell))
			# adding the checked cell to closed list
			self.closed.add(cell)
			if cell is self.end:
				# store path and path legth
				route_path3, route_length = self.display_path()
				route_path3.reverse()
				break
			# getting the adjoint cells
			neighbours = self.neighbour(cell)
			for path in neighbours:
				# print('neighbours: ',path.x,path.y)
				# if cell is not an obstacle and has not been already checked
				if path.reachable and path not in self.closed:
					if (path.net_cost, path) in self.open:
						# selecting the cell with least cost
						if path.cost > cell.cost + 1:
							self.update_cell(path, cell)
					else:
						self.update_cell(path, cell)
						# print(path.net_cost,path.__dict__)
						heapq.heappush(self.open, (path.net_cost, path))
		# print('bends: ',self.bends)
		return route_path3, route_length


def play(img, start_coords, end_coords):
	
	
	_, roi = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
	
	imrows, imcols = roi.shape
	rw = float(imrows)/(2*rows)							#half of row width
	cw = float(imcols)/(2*columns)							#half of column width

	# map the grid in an array
	grid = grid_map(roi, rw, cw, start_coords, end_coords)
	# executing A*
	solution = Astar()
	solution.init_grid(grid, rw, cw)
	route_path, route_length = solution.search()


	print("OUTPUT FOR SINGLE IMAGE (IMAGE 1)...")
	print("route length = ", route_length)
	

	finalArray = []
	# code for checking output for all images
	for i in range (route_length) :
		finalArray.append([route_path[i][0]*rw*2 - rw, route_path[i][1]*cw*2-cw])
		#cv2.circle(roi, ((2*route_path[i][0])*row_width, (2*route_path[i][1])*col_width), 3, 125, -1)
		# cv2.circle(roi, (finalArray[i][0], finalArray[i][1]), 3, 125, -1)
		#return finalArray[0]
	# print ("route path   = " + str(finalArray))
	# print(imrows,rw) 
	# cv2.imshow('dsfr',cv2.resize(roi, (0,0), fx=.9, fy=.9))
	# cv2.waitKey()
	# cv2.destroyAllWindows()
	return finalArray

	
	



#	arena 	start 	end
#	2	  (14,14)	(14,28)
#	3	  (14,14)	(5,0)
#	4	  (14,14)	(14,28)
#	5	  (14,14)	()	
