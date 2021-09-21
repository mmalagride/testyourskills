from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import Point3, CollisionNode, CollisionRay, CollisionTraverser, CollisionHandlerQueue, GeomNode
from pandas import DataFrame
import random
import time
from astar import AStar
class MyGame(ShowBase):
    def __init__(self):      
        ShowBase.__init__(self)
        base.disableMouse()

        self.map = MapGenerator()        
        self.matrix = []
        self.terrain = self.generateTerrain()        

        self.camera.setPos(self.map.gridX/2, self.map.gridY/2, max(self.map.gridX,self.map.gridY)*2.5)
        self.camera.setP(-90) #Rotate Camera To Align
        self.camera.setH(90)  #with Matrix Printed out

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNodePath = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.myTraverser = CollisionTraverser()
        self.myHandler = CollisionHandlerQueue()
        self.myTraverser.addCollider(self.pickerNodePath, self.myHandler)
        
        self.updateTask = taskMgr.add(self.update, "update")
        self.reloadButton = DirectButton(text=("New Map", "Loading!", "Load Map", "disabled"), scale=.05, command=self.refreshTerrain, pos=(1, 1, 0))
        
        self.controlPlayer = DirectCheckButton(text="Move Character", scale=.05, command=self.beginPathFinding, pos=(-1, -1, 0))

        self.playerTimer = 0.0        
        self.playerNode = self.placeCharacter(self.terrain.getChild(1))
        self.playerDirection = []
        self.playerDestination = ()
        self.targetNode = render.attachNewNode("target")
        self.mouseOverNode = render.attachNewNode("mouseOver")
        self.pathNode = render.attachNewNode("pathNode")
        self.accept('mouse1',self.clickTile)

    def update(self, task):
        dt = globalClock.getDt()
        return task.cont

    def generateTerrain(self):
        print("Loading Map...") 
        self.matrix = self.map.createMap()
        self.map.printMatrix(self.matrix)
        terrainNode = render.attachNewNode("terrain")
        wallNode = render.attachNewNode("Wall")
        wallNode.reparentTo(terrainNode)
        floorNode = render.attachNewNode("Floor")
        floorNode.reparentTo(terrainNode)
        for y in range(self.map.gridY):
            for x in range(self.map.gridX):            
                self.cube = self.loader.loadModel("cube")
                self.cube.setScale(0.5)
                if self.matrix[x][y] == 0:
                    self.cube.setColor(1.0, 1.0, 1.0, 1.0)
                    self.cube.setTag('descriptor', 'floor')
                    self.cube.reparentTo(floorNode)   
                else:
                    self.cube.setColor(0.0, 0.0, 0.0, 0.0)
                    self.cube.setTag('descriptor', 'wall')
                    self.cube.reparentTo(wallNode)             
                self.cube.setPos(x, y, 0)
        return terrainNode
    
    def placeCharacter(self,floor):
        player = floor.getChild(random.randint(0,floor.getNumChildren()))
        playerNode = render.attachNewNode("player")
        player.reparentTo(playerNode)
        player.setTag('descriptor', 'player')
        player.setColor(0.0, 0.8, 0.0, 1.0) 
        return playerNode
    
    def refreshTerrain(self):
        self.terrain.removeNode()
        self.playerNode.removeNode()
        self.targetNode.removeNode()
        self.mouseOverNode.removeNode()
        self.pathNode.removeNode()
        self.terrain = self.generateTerrain()
        self.mouseOverNode = render.attachNewNode("mouseOver")
        self.targetNode = render.attachNewNode("target")
        self.pathNode = render.attachNewNode("pathNode")
        self.playerNode = self.placeCharacter(self.terrain.getChild(1))

    def clickTile(self):
        if self.controlPlayer["indicatorValue"]:
            if self.clickedTerrain('target'):
                if len(self.playerDirection) == 1:
                    self.playerDestination = self.playerDirection[0]
                else:
                    self.playerDestination = self.playerDirection[-1]        
                taskMgr.remove('mouseOver') 
                self.controlPlayer["indicatorValue"] = False
                self.controlPlayer.setIndicatorValue()
                self.playerMoveTask = taskMgr.add(self.playerMove, "playerMove")
            else:
                print('Clicked Impassible Terrain')
        else:
            print('Mover Disabled')

    def playerMove(self,task):
        if not(self.controlPlayer["indicatorValue"]):
            dt = globalClock.getDt()
            self.playerTimer += dt
            if self.playerTimer > 0.01:
                self.playerTimer = 0.0
                print("Travelling from:    " + str((int(self.playerNode.getChild(0).getPos().x),int(self.playerNode.getChild(0).getPos().y))))
                print("Travelling through: " + ', '.join(str(e) for e in self.playerDirection[:-1]))
                print("Travelling to:      " + str((int(self.targetNode.getChild(0).getPos().x),int(self.targetNode.getChild(0).getPos().y))))
                if self.pathNode.getChildren().getNumPaths() > 0: 
                    self.playerNode.getChild(0).setColor(1.0, 1.0, 1.0, 1.0)                   
                    self.playerNode.getChild(0).setTag('descriptor', 'floor')
                    self.playerNode.getChild(0).reparentTo(self.terrain.getChild(1))
                    self.pathNode.getChild(0).setColor(0.0, 0.8, 0.0, 1.0)
                    self.pathNode.getChild(0).setTag('descriptor', 'player')
                    self.pathNode.getChild(0).reparentTo(self.playerNode)
                else:
                    self.playerNode.getChild(0).setColor(1.0, 1.0, 1.0, 1.0)
                    self.playerNode.getChild(0).setTag('descriptor', 'floor')
                    self.playerNode.getChild(0).reparentTo(self.terrain.getChild(1))
                    self.targetNode.getChild(0).setColor(0.0, 0.8, 0.0, 1.0)
                    self.targetNode.getChild(0).setTag('descriptor', 'player')
                    self.targetNode.getChild(0).reparentTo(self.playerNode)
                    return task.done
                print("")
            return task.cont
        else:
            return task.done

    def clickedTerrain(self, tag):
        if base.mouseWatcherNode.hasMouse():
            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.x, mousePos.y)
            self.myTraverser.traverse(render)
            if self.myHandler.getNumEntries() > 0:
                self.myHandler.sortEntries()
                pickedObject = self.myHandler.getEntry(0).getIntoNodePath()
                pickedObjectTag = pickedObject.getNetTag('descriptor')
                if pickedObjectTag == tag:
                    return True
        return False  

    def beginPathFinding(self, status):
        if status:
            self.mouseOverTask = taskMgr.add(self.mouseOver, "mouseOver")
        else:
            taskMgr.remove('mouseOver')

    def mouseOver(self, task):
        if base.mouseWatcherNode.hasMouse():
            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.x, mousePos.y)
            self.myTraverser.traverse(render)
            if self.myHandler.getNumEntries() > 0:
                self.myHandler.sortEntries()
                pickedObject = self.myHandler.getEntry(0).getIntoNodePath()
                pickedObjectTag = pickedObject.getNetTag('descriptor')
                if pickedObjectTag == 'floor':
                    player = self.playerNode.getChild(0).getPos()
                    Origin = (int(player.x),int(player.y)) 
                    mouseOver = pickedObject.getPos(render)
                    Target = (int(mouseOver.x),int(mouseOver.y))
                    foundPath = list(MapSolver(self.matrix).astar(Origin,Target))
                    self.playerDirection = foundPath[1:]
                    if self.targetNode.getChildren().getNumPaths() > 0: #Clear Existing Target
                        self.targetNode.getChild(0).setColor(1.0, 1.0, 1.0, 1.0)
                        self.targetNode.getChild(0).setTag('descriptor', 'floor')
                        self.targetNode.getChild(0).reparentTo(self.terrain.getChild(1))
                    pickedObject.wrtReparentTo(self.targetNode)
                    pickedObject.setTag('descriptor', 'target')
                    pickedObject.setColor(1.0, 0.6, 0.0, 1.0)
                    if self.pathNode.getChildren().getNumPaths() > 0: #Clear Existing Path
                        for previousPathNode in self.pathNode.getChildren():
                            previousPathNode.setColor(1.0, 1.0, 1.0, 1.0)
                            previousPathNode.reparentTo(self.terrain.getChild(1))
                        self.pathNode.removeNode()    
                        self.pathNode = render.attachNewNode("pathNode")
                    for pathTile in self.playerDirection[:-1]:
                        for anyTile in self.terrain.getChild(1).getChildren():
                            if ((anyTile.getPos().x,anyTile.getPos().y) == pathTile):
                                anyTile.wrtReparentTo(self.pathNode)
                                anyTile.setColor(0.8, 0.8, 0.8, 1.0)   
        return task.cont

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

class MapSolver(AStar):
    def __init__(self, maze):
        self.lines = []
        for line in maze:
            self.lines.append(''.join(map(str,line)))
        self.width = len(self.lines[0])
        self.height = len(self.lines)
        self.iteration = 0
        self.heuristic = 0.0
        self.Origin = (0,0)


    def heuristic_cost_estimate(self, current, goal):
        self.iteration += 1
        if self.iteration == 1:
            self.Origin = current
        dx1 = current[0] - goal[0]
        dy1 = current[1] - goal[1]
        dx2 = self.Origin[0] - goal[0]
        dy2 = self.Origin[1] - goal[1]
        cross = abs(dx1*dy2 - dx2*dy1)
        self.heuristic += cross*0.001
        return self.heuristic

    def distance_between(self, n1, n2):
        return 1

    def neighbors(self, node):
        neighbourhood = [[-1, 0], [0, -1], [1, 0], [0, 1], [-1, 1] ,[-1, -1], [1, -1], [1, 1]]
        neighbours = [(node[0] + offset[0], node[1] + offset[1]) for offset in neighbourhood]
        validNeighbours = []
        for nx, ny in neighbours:
            if (0 <= nx < self.width) and (0 <= ny < self.width) and self.lines[nx][ny] == '0':
                validNeighbours.append((nx,ny))
        return validNeighbours

app = MyGame()
app.run()
