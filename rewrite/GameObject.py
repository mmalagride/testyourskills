from panda3d.core import Vec3, Vec2
from direct.actor.Actor import Actor
from panda3d.core import CollisionBox, CollisionNode
from direct.interval.LerpInterval import LerpPosInterval
from astar import AStar
import math

class GameObject():
    def __init__(self, pos, modelName, maxSpeed, colliderName):
        self.actor = Actor(modelName)
        self.actor.reparentTo(render)
        self.actor.setPos(pos)
        self.actor.setScale(0.5)
        self.walking = False
        self.maxSpeed = maxSpeed
        self.mouseOver = False
        self.targetDestination = False
        self.destination = []
        self.lerpDuration = 0

        colliderNode = CollisionNode(colliderName)
        colliderNode.addSolid(CollisionBox(Vec3(0,0,0),1,1,1))
        self.collider = self.actor.attachNewNode(colliderNode)
        self.collider.setPythonTag("owner", self)
        self.collider.show()

    def update(self, dt):
        if self.mouseOver:
            self.mouseOver = False
            
    def cleanup(self):
        if self.collider is not None and not self.collider.isEmpty():
            self.collider.clearPythonTag("owner")
            base.cTrav.removeCollider(self.collider)
            base.pusher.removeCollider(self.collider)
        
        if self.actor is not None:
            self.actor.cleanup()
            self.actor.removeNode()
            self.actor = None
        
        self.collider = None

    def astarPathfinding(self, matrix, floorList, target):  
        Origin = (int(self.actor.getPos().x),int(self.actor.getPos().y))  
        Target = (int(target.model.getPos().x),int(target.model.getPos().y))
        pathNodes = []
        try:
            Path = list(MapSolver(map(list, zip(*matrix))).astar(Origin,Target))
            pathNodes = []
            for step in Path:
                lister = [[floorNode,(int(floorNode.model.getPos().x),int(floorNode.model.getPos().y))] for floorNode in floorList]        
                for floorDict in lister:
                    if step == floorDict[1]:
                        pathNodes.append(floorDict[0])
        except:
            pass        
        return pathNodes

class Player(GameObject):
    def __init__(self, pos):
        GameObject.__init__(self, pos, "cube", 0.1, "player")
        self.actor.getChild(0).setH(180)
        self.actor.setColor(0.0, 1.0, 0.0, 1.0) 
        self.actor.setSx(0.25)
        self.actor.setSy(0.25)
        self.yVector = Vec2(0,1)
        #base.pusher.addCollider(self.collider, self.actor)
        #base.cTrav.addCollider(self.collider, base.pusher)

    def update(self, keys, dt):
        GameObject.update(self, dt)

        self.walking = False

        if len(self.destination) > 1:
            if self.lerpDuration > self.maxSpeed:
                self.destination[0].isPath = False
                self.destination.pop(0)
                self.lerpDuration = 0
                self.walking = True                
                nextTile = self.destination[0].model.getPos()
                direction = Vec3(self.destination[0].model.getPos().xy - self.actor.getPos().xy,0)
                lerp = LerpPosInterval(self.actor, self.maxSpeed, self.actor.getPos() + direction, self.actor.getPos(),blendType='noBlend')
                heading = self.yVector.signedAngleDeg((direction).xy)
                self.actor.setH(heading)
                lerp.start()
            self.lerpDuration += dt

class StaticObject(GameObject):
    def __init__(self, pos, modelName, colliderName, colour):
        self.model = loader.loadModel(modelName) 
        self.model.setColor(colour)
        self.model.setPos(pos)
        self.model.setScale(0.5)
        self.mouseOver = False
        self.isPath = False
        self.isTarget = False

        colliderNode = CollisionNode(colliderName)
        colliderNode.addSolid(CollisionBox(Vec3(0,0,0),1,1,1))
        
        self.collider = self.model.attachNewNode(colliderNode)
        self.collider.setPythonTag("owner", self)
        self.collider.show()

    def cleanup(self):
        if self.collider is not None and not self.collider.isEmpty():
            self.collider.clearPythonTag("owner")
            base.cTrav.removeCollider(self.collider)
            base.pusher.removeCollider(self.collider)
        
        if self.model is not None:
            self.model.removeNode()
            #self.model.destroy()
            self.model = None
        
        self.collider = None

    def update(self, dt):
        if self.mouseOver:
            self.model.setColor(0.0,0.9,0.9,1)
            self.mouseOver = False
        elif self.isPath:
            self.model.setColor(0.8,1.0,0.0,1)
        else:
            self.model.setColor(1.0,1.0,1.0,1)

class MapSolver(AStar):
    def __init__(self, maze):
        self.lines = []
        for line in maze:
            self.lines.append(''.join(map(str,line)))
        self.width = len(self.lines)
        self.height = len(self.lines[0])
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
