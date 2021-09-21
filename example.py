from pandas import DataFrame
from astar import AStar
import numpy as np
import math
import random

class MapGenerator():
    def __init__(self):
        self.seed = random.seed(100)
        self.gridY = 25
        self.gridX  = 25
        self.smoothingIterations = 3
        self.mapDensity = [1,0,0,0]
        self.matrix = []

    def createMap(self):
        self.matrix = []
        self.populateGrid()
        for i in range(self.smoothingIterations):
            self.smoothGrid()
        return self.matrix

    def populateGrid(self):
        for h in range(self.gridY):
            row = []
            for w in range(self.gridX):
                cell = random.choice(self.mapDensity) #66% empty
                row.append(cell)
            self.matrix.append(row)


    def smoothGrid(self):
        for y in range(self.gridY):
            for x in range(self.gridX):
                neighbourTiles = self.getSurroundingTiles(x,y)
                if neighbourTiles > 4:
                    self.matrix[x][y] = 1
                elif neighbourTiles < 2:
                    self.matrix[x][y] = 0


    def getSurroundingTiles(self,posX,posY):
        tileCount = 0
        for neighbourY in range(posY - 1, posY + 2):
            for neighbourX in range(posX - 1, posX + 2):        
                if (neighbourX >= 0 and neighbourX < self.gridX) and (neighbourY >= 0 and neighbourY < self.gridY):
                    neighbourVal = self.matrix[neighbourX][neighbourY]
                    if (neighbourX != posX or neighbourY != posY):
                        tileCount += neighbourVal
                else:
                    tileCount += 1
        return tileCount

    def printMatrix(self,matrix):
        print(DataFrame(matrix).to_string(index=False,header=False))

    def returnPath(self,currentNode):
        path = []
        current = currentNode
        while current is not None:
            path.append(current.position)
            current = current.parent
        return path[::-1]   
             
class MazeSolver(AStar):

    """sample use of the astar algorithm. In this exemple we work on a maze made of ascii characters,
    and a 'node' is just a (x,y) tuple that represents a reachable position"""

    def __init__(self, maze):
        self.lines = []
        for line in maze:
            self.lines.append(''.join(map(str,line)))
        self.width = len(self.lines[0])
        self.height = len(self.lines)
        self.heuristic = 0.0

    def heuristic_cost_estimate(self, current, goal):
        dx1 = current[0] - goal[0]
        dy1 = current[1] - goal[1]
        dx2 = Origin[0] - goal[0]
        dy2 = Origin[1] - goal[1]
        cross = abs(dx1*dy2 - dx2*dy1)
        self.heuristic += cross*0.001
        return self.heuristic

    #def heuristic_cost_estimate(self, current, goal):
    #    dx = abs(current[0] - goal[0])
    #    dy = abs(current[1] - goal[1])        
    #    return max(dx, dy)

    #def heuristic_cost_estimate(self, current, goal):
    #    return np.linalg.norm(np.array(goal) - current)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        neighbourhood = [[-1, -1],[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]
        neighbours = [(node[0] + offset[0], node[1] + offset[1]) for offset in neighbourhood]
        validNeighbours = []
        for nx, ny in neighbours:
            if (0 <= nx < self.width) and (0 <= ny < self.width) and self.lines[nx][ny] == '0':
                validNeighbours.append((nx,ny))
        return validNeighbours


generator = MapGenerator()
terrainMap = generator.createMap()
tempMap = terrainMap
Origin = (15, 0)
Target = (15, 2)
#path = generator.aStarSearch(terrainMap,Origin,Target)
thing = MazeSolver(tempMap).astar(Origin, Target)
foundPath = list(MazeSolver(tempMap).astar(Origin, Target))
for path in foundPath:
    tempMap[path[0]][path[1]] = "P"
generator.printMatrix(tempMap)
pass