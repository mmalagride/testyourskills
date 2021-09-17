from pandas import DataFrame
import sys
import random
random.seed(1)
class MapGenerator():
    def __init__(self):
        self.gridY = 25
        self.gridX  = 25
        self.smoothingIterations = 3
        self.mapDensity = [1,0,0]
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
        for x in range(self.gridY):
            for y in range(self.gridX):
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
