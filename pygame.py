from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from generateGrid import *
import time
class MyApp(ShowBase):
    def __init__(self):      
        ShowBase.__init__(self)
        base.disableMouse()

        self.map = MapGenerator()
        self.terrain = self.generateTerrain()
        self.matrix = self.map.createMap()

        self.camera.setPos(self.map.gridX/2, self.map.gridY/2, max(self.map.gridX,self.map.gridY)*3)
        self.camera.setP(-90)
        self.updateTask = taskMgr.add(self.update, "update")

        self.reloadButton = DirectButton(text=("OK", "click!", "rolling over", "disabled"), scale=.05, command=self.paintTerrain, pos=(1, 1, 0))

    def update(self, task):
        dt = globalClock.getDt()
        self.paintTerrain
        return task.cont

    def generateTerrain(self):
        terrainNode = render.attachNewNode("Terrain")
        for y in reversed(range(self.map.gridY)):
            for x in range(self.map.gridX):            
                self.cube = self.loader.loadModel("cube")
                self.cube.reparentTo(terrainNode)
                self.cube.setPos(x, y, 0)
        return terrainNode
    
    def paintTerrain(self):
        print("Loading Map...")        
        self.matrix = self.map.createMap()
        self.map.printMatrix(self.matrix)
        for child in self.terrain.getChildren():
            if self.matrix[int(child.getPos().x)][int(child.getPos().y)] != 0:
                child.setColorScale(0.0, 0.0, 0.0, 0.0)
            else:
                child.setColorScale(1.0, 1.0, 1.0, 1.0)
    
    def placePlayer(self):
        pass

app = MyApp()
app.run()
