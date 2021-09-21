from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import Point3, CollisionNode, CollisionRay, CollisionTraverser, CollisionHandlerQueue, GeomNode
from pandas import DataFrame
import random
import time
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
        
        self.mouseOverTask = taskMgr.add(self.mouseOver, "mouseOver")
        self.playerNode = self.placeCharacter(self.terrain.getChild(1))
        self.targetNode = render.attachNewNode("target")
        self.mouseOverNode = render.attachNewNode("mouseOver")
        self.accept('mouse1',self.clickTile)
        self.accept('mouse1-up',self.clickTile)

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
        self.terrain = self.generateTerrain()
        self.mouseOverNode = render.attachNewNode("mouseOver")
        self.targetNode = render.attachNewNode("target")
        self.playerNode = self.placeCharacter(self.terrain.getChild(1))

    def clickTile(self):
        if base.mouseWatcherNode.hasMouse():
            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.x, mousePos.y)
            self.myTraverser.traverse(render)
        if self.myHandler.getNumEntries() > 0:
            self.myHandler.sortEntries()
            pickedObject = self.myHandler.getEntry(0).getIntoNodePath()
            pickedObjectTag = pickedObject.getNetTag('descriptor')
            if pickedObjectTag == 'mouseOver':              
                pickedObject.wrtReparentTo(self.targetNode)
                if self.targetNode.getChildren().getNumPaths() > 1: #Set Existing Target to Floor
                    self.targetNode.getChild(0).setColor(1.0, 1.0, 1.0, 1.0)
                    self.targetNode.getChild(0).setTag('descriptor', 'floor')
                    self.targetNode.getChild(0).reparentTo(self.terrain.getChild(1))
                pickedObject.setColor(1.0, 0.6, 0.0, 1.0)
                pickedObject.setTag('descriptor','target')  
                player = self.playerNode.getChild(0).getPos()
                print("Origin: (%s, %s)" % (int(player.x),int(player.y)))        
                print("Target: (%s, %s)" % (int(pickedObject.getPos().x),int(pickedObject.getPos().y)))
                #Start PathFinding Loop

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
                    pickedObject.wrtReparentTo(self.mouseOverNode)
                    if self.mouseOverNode.getChildren().getNumPaths() > 1: #Set Existing Target to Floor
                        self.mouseOverNode.getChild(0).setColor(1.0, 1.0, 1.0, 1.0)
                        self.mouseOverNode.getChild(0).setTag('descriptor', 'floor')
                        self.mouseOverNode.getChild(0).reparentTo(self.terrain.getChild(1)) 
                    pickedObject.setTag('descriptor','mouseOver')  
                    pickedObject.setColor(0.8, 0.8, 0.8, 1.0)    
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

app = MyGame()
app.run()
