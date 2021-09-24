from direct.showbase.ShowBase import ShowBase

from direct.actor.Actor import Actor
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionRay, CollisionHandlerQueue, CollisionNode, CollisionBox
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import Vec4, Vec3, Point3, GeomNode
from panda3d.core import WindowProperties, BitMask32
from direct.gui.DirectGui import DirectCheckButton, DirectButton
from random import Random
from pandas import DataFrame
from GameObject import *

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)
        render.setLight(self.mainLightNodePath)

        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(self.ambientLightNodePath)

        render.setShaderAuto()

        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False
        }

        self.accept("mouse1", self.mouseClick)

        self.pusher = CollisionHandlerPusher()
        self.cTrav = CollisionTraverser()
        self.pusher.setHorizontal(True)

        self.updateTask = taskMgr.add(self.update, "update")

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNodePath = camera.attachNewNode(self.pickerNode)
        self.pickerRay = CollisionRay()      
        self.pickerNode.addSolid(self.pickerRay)
        self.myTraverser = CollisionTraverser()
        self.myHandler = CollisionHandlerQueue()
        self.myTraverser.addCollider(self.pickerNodePath, self.myHandler)
        mask = BitMask32()
        mask.setBit(1)
        self.pickerNode.setIntoCollideMask(1)

        self.seed = 1
        self.myRandom = Random(self.seed)
        self.floorNodeList = []
        self.wallNodeList = []
        self.player = Player(Vec3(0,0,1))
        self.generateNewMap()
        
        self.camera.setPos(self.mapGenerator.gridX/2, self.mapGenerator.gridY/2, max(self.mapGenerator.gridX,self.mapGenerator.gridY)*2.5)
        self.camera.setP(-90)
        self.camera.setH(90)

        self.controlPlayer = DirectCheckButton(text="Move Character", scale=.05, command=self.beginPathFinding, pos=(-1, -1, 0))
        self.reloadButton = DirectButton(text=("New Map", "Loading!", "Load Map", "disabled"), scale=.05, command=self.generateNewMap, pos=(1, 1, 0))

    def beginPathFinding(self, status):
        if status:
            self.mouseOverTask = taskMgr.add(self.mouseOver, "mouseOver")
        else:
            taskMgr.remove('mouseOver')

    def generateNewMap(self):
        self.seed += 1
        self.mapGenerator = MapGenerator(self.seed)
        self.mapMatrix = self.mapGenerator.createMap()
        self.player.cleanup()
        for floor in self.floorNodeList:
            floor.cleanup()
        for wall in self.wallNodeList:
            wall.cleanup()
        self.floorNodeList = []
        self.wallNodeList = []
        self.terrain = self.generateTerrain()
        randomPosition = self.floorNodeList[self.myRandom.randint(0,len(self.floorNodeList)-1)].model.getPos()
        self.player = Player(Vec3(randomPosition.x,randomPosition.y,1))

    def generateTerrain(self):
        self.mapGenerator.printMatrix(self.mapMatrix)
        terrainNode = render.attachNewNode("terrain")
        wallNodeGroup = render.attachNewNode("wall")      
        floorNodeGroup = render.attachNewNode("floor")  
        for y in range(self.mapGenerator.gridY):
            for x in range(self.mapGenerator.gridX):                    
                if self.mapMatrix[y][x] == 0:
                    floorNode = StaticObject(Vec3(x,y,0),"cube","floor",(1,1,1,1))
                    self.floorNodeList.append(floorNode)
                    floorNodeGroup.attachNewNode(floorNode.model.node())              
                else:
                    wallNode = StaticObject(Vec3(x,y,1),"cube","wall",(0,0,0,0))
                    self.wallNodeList.append(wallNode)
                    wallNodeGroup.attachNewNode(wallNode.model.node())

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState

    def update(self, task):
        dt = globalClock.getDt()
        self.player.update(self.keyMap, dt)
        for floorNode in self.floorNodeList:            
            floorNode.update(dt)
        return task.cont

    def mouseOver(self, task):
        if base.mouseWatcherNode.hasMouse():
            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.x, mousePos.y)
            self.myTraverser.traverse(render)
            if self.myHandler.getNumEntries() > 0:
                self.myHandler.sortEntries()
                rayHit = self.myHandler.getEntry(0)
                rayHitPath = rayHit.getIntoNodePath()
                if rayHitPath.hasPythonTag("owner"):
                    hitObject = rayHitPath.getPythonTag("owner")
                    hitObject.mouseOver = True
                    if hitObject.collider.name == 'floor':
                        path = self.player.astarPathfinding(self.mapMatrix,self.floorNodeList,hitObject)
                        for step in path:
                            step.mouseOver = True
        return task.cont

    def mouseClick(self):
        if base.mouseWatcherNode.hasMouse() and self.controlPlayer["indicatorValue"]:
            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.x, mousePos.y)
            self.myTraverser.traverse(render)
            if self.myHandler.getNumEntries() > 0:
                self.myHandler.sortEntries()
                rayHit = self.myHandler.getEntry(0)
                rayHitPath = rayHit.getIntoNodePath()
                if rayHitPath.hasPythonTag("owner"):
                    hitObject = rayHitPath.getPythonTag("owner")                          
                    if hitObject.collider.name == 'floor':
                        path = self.player.astarPathfinding(self.mapMatrix,self.floorNodeList,hitObject)
                        for step in path:
                            step.isPath = True
                        pathTarget = hitObject.model.getPos()
                        hitObject.targetDestination = True
                        thing = path + [hitObject]
                        self.player.destination = path + [hitObject]
                        taskMgr.remove('mouseOver')
                        self.controlPlayer["indicatorValue"] = False
                        self.controlPlayer.setIndicatorValue()

class MapGenerator():
    def __init__(self,seed):
        self.myRandom = Random(seed)
        self.gridY = 25
        self.gridX  = self.gridY
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
                cell = self.myRandom.choice(self.mapDensity) #66% empty
                row.append(cell)
            self.matrix.append(row)


    def smoothGrid(self):
        for y in range(self.gridY):
            for x in range(self.gridX):
                neighbourTiles = self.getSurroundingTiles(x,y)
                if neighbourTiles > 4:
                    self.matrix[y][x] = 1
                elif neighbourTiles < 2:
                    self.matrix[y][x] = 0


    def getSurroundingTiles(self,posX,posY):
        tileCount = 0
        for neighbourY in range(posY - 1, posY + 2):
            for neighbourX in range(posX - 1, posX + 2):        
                if (neighbourX >= 0 and neighbourX < self.gridX) and (neighbourY >= 0 and neighbourY < self.gridY):
                    neighbourVal = self.matrix[neighbourY][neighbourX]
                    if (neighbourX != posX or neighbourY != posY):
                        tileCount += neighbourVal
                else:
                    tileCount += 1
        return tileCount

    def printMatrix(self,matrix):
        print(DataFrame(matrix).to_string(index=False,header=False))

game = Game()
game.run()