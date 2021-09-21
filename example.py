from pandas import DataFrame
from astar import AStar
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

    def heuristic_cost_estimate(self, n1, n2):
        (x1, y1) = n1 #start
        (x2, y2) = n2 #end
        dx = abs(x2 - x1) * 10
        dy = abs(y2 - y1) * 10
        hx = dx + dy  

        dx1 = x1 - x2
        dy1 = y1 - y2
        dx2 = Origin[0] - x2
        dy2 = Origin[1] - y2
        cross = abs(dx1*dy2 - dx2*dy1)
        self.heuristic += cross*0.001
        #distances1 = ((dx + dy) + (math.sqrt(2) - 2) *  min(dx,dy)) #octile distance
        #distances2 = (dx + dy) - min(dx,dy)                         #Chebyshev distance
        #distances3 = dx + dy                                        #Manhatten distance                  
        #return ((dx + dy) + (math.sqrt(2) - 2) *  min(dx,dy))
        return self.heuristic
 
        #return abs(x2 - x1), abs(y2 - y1)
        #return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        x, y = node
        return[(nx, ny) for nx, ny in[(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y), (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1)]if 0 <= nx < self.width and 0 <= ny < self.height and self.lines[ny][nx] == '0']


generator = MapGenerator()
terrainMap = generator.createMap()
tempMap = terrainMap
Origin = (20, 0)
Target = (7, 18)
#path = generator.aStarSearch(terrainMap,Origin,Target)
thing = MazeSolver(tempMap).astar(Origin, Target)
foundPath = list(MazeSolver(tempMap).astar(Origin, Target))
for path in foundPath:
    tempMap[path[0]][path[1]] = "P"
tempMap[0][20] = 'S'
tempMap[6][17] = 'E'
generator.printMatrix(tempMap)
pass