from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.gui.DirectGui import *
from direct.showbase import BufferViewer
from direct.showbase.DirectObject import DirectObject
from direct.filter.CommonFilters import CommonFilters
from direct.interval.IntervalGlobal import Sequence
from direct.gui.DirectEntry import DirectEntry
from panda3d.core import *

# from panda3d.core import loadPrcFileData
# from panda3d.core import NodePath
# from panda3d.core import PandaNode
# from panda3d.core import LightRampAttrib
# from panda3d.core import Point3
# from panda3d.core import Vec4
# from panda3d.core import Vec3
# from direct.task.Task import Task
# from direct.actor.Actor import Actor
# from direct.gui.DirectGui import *
# from direct.showbase import BufferViewer
# from direct.showbase.DirectObject import DirectObject
# from direct.showbase.ShowBase import ShowBase
# from direct.filter.CommonFilters import CommonFilters
# from direct.interval.IntervalGlobal import Sequence
# from direct.directbase.DirectStart import *
# from direct.gui.DirectEntry import DirectEntry
from direct.interval.IntervalGlobal import *
# from pandac.PandaModules import *
# from math import pi, sin, cos
# from DirectPrompt import DirectPrompt
import sys
import random

class Audio(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.sound = {}
        self.sound['death'] = loader.loadSfx('arena/sound/invisibility.wav')
        self.music = {}
        self.music['complex'] = loader.loadMusic('arena/music/The Complex.mp3')
        self.currentMusic = None 
    def death(self):
        self.sound['death'].play()       
    def play(self,name):
        self.stop()
        self.music[name].play()
        self.currentMusic = name
    def stop(self):
        if(self.currentMusic):
            self.music[self.currentMusic].stop()
    def next(self):
        keys = self.music.keys()
        size = len(keys)
        index = (keys.index(self.currentMusic) + 1) % size
        self.play(keys[index])



class Arena(DirectObject):
    collshow = False
    def initShader(self):
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.9))
        tempnode.setShaderAuto()
        base.cam.node().setInitialState(tempnode.getState())
        self.separation = 1 # Pixels
        self.filters = CommonFilters(base.win, base.cam)
        filterok = self.filters.setBloom()
        if (filterok == False):
            addTitle("Toon Shader: Video card not powerful enough to do image postprocessing")
            sys.exit
   
    def initCollision(self):
        base.cTrav = CollisionTraverser()
        base.collisionHandlerEvent = CollisionHandlerEvent()
        base.collisionHandlerEvent.addInPattern('%fn-i-%in')
        base.collisionHandlerEvent.addOutPattern('%fn-o-%in')
        base.collisionHandlerEvent.addAgainPattern('%fn-a-%in')
        self.accept('mouseray-a-ground',self.collideGroundAgain)
        self.lastX = 0
        self.lastDirection = 0


    def collideGroundAgain(self,entry):
        np_into=entry.getIntoNodePath()
        pos = entry.getSurfacePoint(np_into)
        pos.setZ(1)
        x = pos.getX()
        if(x == self.lastX):
            return
        if(x < self.lastX):
            direction = -1
        else:
            direction = 1
        if(direction != self.lastDirection):
            if(direction == -1):
                self.sonic.left()
                self.tails.left()
            else:
                self.sonic.right()
                self.tails.right()
            self.lastDirection = direction
        self.lastX = x
        if (x < -7 ) : pos.setX(-7)
        if (x > 7 ) : pos.setX(7)
        pos.setY(-7)
        self.sonic.collisionNodePath.setPos(pos)
        pos.setY(-5)
        self.tails.collisionNodePath.setPos(pos)
        # self.pandaActor.setPos(pos)

    def updateMouseTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos=base.mouseWatcherNode.getMouse()
            self.mouse.collisionRay.setFromLens(base.camNode, mpos.getX(),mpos.getY())
        return task.cont

    def mouseClick(self):
        messenger.send("Spider") 
        print 'click'

    def toggle_collisions(self):
        self.collshow = not self.collshow
        if self.collshow:
            self.collisionTraverser.showCollisions(base.render)
            l=base.render.findAllMatches("**/+CollisionNode")
            for cn in l: cn.show()
        else:
            self.collisionTraverser.hideCollisions()
            l=base.render.findAllMatches("**/+CollisionNode")
            for cn in l: cn.hide()
    def toggle_wire(self):
        base.toggleWireframe()
        base.toggleTexture()

    def __init__(self):
        base.audio = Audio()
        base.audio.play('complex')
        self.initShader()
        self.initCollision()
        self.camera = Camera()
        self.mouse = Mouse()
        self.ground = Ground()
        self.smiley = Smiley()
        self.frowney = Frowney()
        self.gorrila = Gorrila()
        self.sonic = Sonic()
        self.tails = Tails()
        self.monster = Monster()
        base.arrow = Arrow()
        self.dragon = Dragon()
        self.panda = Panda()
        self.pandaren = Pandaren()
        self.tombstone = Tombstone()
        self.tombstone.spiders = []
        for i in range(50):
            self.tombstone.spiders.append(Spider(str(i)))
        self.tombstone.batch()
        taskMgr.add(self.updateMouseTask, "updatePicker")
        self.accept('escape',sys.exit)
        self.accept('mouse1',self.mouseClick)

class Camera(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        base.disableMouse()
        self.default()
        self.accept('1',self.front)
        self.accept('2',self.top)
        self.accept('0',self.default)
    def default(self):
        pos = Vec3(0,0,0)
        pos.addZ(20)
        pos.addY(-20)
        camera.setPos(pos)
        camera.setHpr(0, -45, 0)
    def front(self):
        pos = Vec3(0,0,0)
        pos.addY(-40)
        camera.setPos(pos)
        camera.setHpr(0, 0, 0)
    def top(self):
        pos = Vec3(0,0,0)
        pos.addZ(40)
        camera.setPos(pos)
        camera.setHpr(0, -90, 0)        


class Mouse(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionRay = CollisionRay()
        self.collisionNode = CollisionNode('mouseray')
        self.collisionNode.set_into_collide_mask(0)
        self.collisionNode.addSolid(self.collisionRay)
        self.collisionNodePath = base.camera.attachNewNode(self.collisionNode)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)    

class Ground(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionPlane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        self.collisionNode = CollisionNode('ground')
        self.collisionNode.addSolid(self.collisionPlane)
        self.collisionNode.setCollideMask(BitMask32.bit(2))
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.model = loader.loadModel("arena/environment/environment")
        self.model.setTwoSided(True)
        self.model.reparentTo(self.collisionNodePath)
        self.model.setScale(0.035, 0.035, 0.035)
        self.model.setPos(-0.7, 5.7, -0.1)
        self.model.showThrough()
        self.model.findAllMatches("**/TreeTrunk*").hide()
        self.model.findAllMatches("**/Cylinder*").hide()
        self.model.findAllMatches("**/Rock*").hide()
        self.model.findAllMatches("**/Bamboo*").hide()
        self.model.findAllMatches("**/Branch*").hide()
        self.model.findAllMatches("**/Plane*").hide()


class Smiley(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('smiley')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(-13,10,1)
        self.model = loader.loadModel('arena/balls/smiley')
        self.model.reparentTo(self.collisionNodePath)
        self.model.setScale(1,1,1)
        self.model.showThrough()

        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.accept('mouseray-i-smiley',self.collideIn)
        self.accept('mouseray-o-smiley',self.collideOut)
        self.interval = LerpHprInterval(self.collisionNodePath,1,Vec3(360,0,0))
        self.interval.loop()

    def collideIn(self,entry):
        self.interval.pause()
        base.audio.next()
    def collideOut(self,entry):
        self.interval.resume()

class Frowney(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('frowney')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(13,10,1)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.model = loader.loadModel('arena/balls/frowney')
        self.model.reparentTo(self.collisionNodePath)
        self.model.setScale(1,1,1)
        self.model.showThrough()

        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.accept('mouseray-i-frowney',self.collideIn)
        self.accept('mouseray-o-frowney',self.collideOut)
        self.interval = LerpHprInterval(self.collisionNodePath,1,Vec3(-360,0,0))
        self.interval.loop()

    def collideIn(self,entry):
        self.interval.pause()
        base.audio.stop()
    def collideOut(self,entry):
        self.interval.resume()



class Sonic(object):
    def __init__(self):
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('sonic')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(-10,10,0)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.actor = Actor("arena/sonic/sonic",{"run":"arena/sonic/sonic-run","board":"arena/sonic/sonic-board","win":"arena/sonic/sonic-win"})
        self.actor.setScale(0.07,0.07,0.07)
        self.actor.setPos(0,0,-1.2)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("board")
        self.actor.showThrough()
    def left(self):
        LerpHprInterval(self.collisionNodePath,0.1,Vec3(-90,0,0)).start()
    def right(self):
        LerpHprInterval(self.collisionNodePath,0.1,Vec3(90,0,0)).start()


class Tails(object):
    def __init__(self):
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('tails')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(-9,10,0)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.actor = Actor("arena/tails/tails",{"win":"arena/tails/tails-win","board":"arena/tails/tails-board"})
        self.actor.setScale(0.07,0.07,0.07)
        self.actor.setPos(0,0,-1.2)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("board")
        self.actor.showThrough()
    def left(self):
        LerpHprInterval(self.collisionNodePath,0.1,Vec3(270,0,0)).start()
    def right(self):
        LerpHprInterval(self.collisionNodePath,0.1,Vec3(90,0,0)).start()

class Dragon(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('dragon')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(9,9,1)
        self.actor = Actor("arena/dragon/nik-dragon",{"walk":"arena/dragon/nik-dragon"})
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.setScale(0.09,0.09,0.09)
        self.actor.setPos(0,-0.1,0)
        self.actor.loop("walk")
        self.actor.showThrough()
        LerpPosInterval(self.collisionNodePath,10,Point3(-9,9,1)).loop()
        LerpHprInterval(self.collisionNodePath,5,Vec3(360,0,0)).loop()
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.accept('mouseray-i-dragon',self.collideIn)
        self.accept('mouseray-o-dragon',self.collideOut)
    def collideIn(self,entry):
        base.arrow.highlight(self.collisionNodePath)
    def collideOut(self,entry):
        base.arrow.hide()

class Pandaren(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('pandaren')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(9,-5,1)        
        self.actor = Actor("arena/pandaren/panda",{"walk":"arena/pandaren/panda-walk"})
        self.actor.setScale(0.2,0.2,0.2)
        self.actor.setPos(0,0.3,-1)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("walk")
        self.actor.showThrough()
        LerpPosInterval(self.collisionNodePath,10,Point3(9,5,1)).loop()
        LerpHprInterval(self.collisionNodePath,5,Vec3(360,0,0)).loop()
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.accept('mouseray-i-pandaren',self.collideIn)
        self.accept('mouseray-o-pandaren',self.collideOut)
    def collideIn(self,entry):
        base.arrow.highlight(self.collisionNodePath)
    def collideOut(self,entry):
        base.arrow.hide()

class Gorrila(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('gorrila')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(-9,5,1)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.actor = Actor("arena/gorilla/gorillawalking",{"walk":"arena/gorilla/gorillawalking"})
        self.actor.setScale(0.2,0.2,0.2)
        self.actor.setPos(0,0.3,-1)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("walk")
        self.actor.showThrough()
        LerpPosInterval(self.collisionNodePath,10,Point3(-9,-5,1)).loop()
        LerpHprInterval(self.collisionNodePath,5,Vec3(360,0,0)).loop()
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.accept('mouseray-i-gorrila',self.collideIn)
        self.accept('mouseray-o-gorrila',self.collideOut)
    def collideIn(self,entry):
        base.arrow.highlight(self.collisionNodePath)
    def collideOut(self,entry):
        base.arrow.hide()

class Monster(object):
    def __init__(self):
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('monster')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(-7,10,0)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.actor = Actor("arena/monster/monster1",{"attack":"arena/monster/monster1-pincer-attack-both"})
        # self.actor = Actor("arena/monster/monster1-explode",{"explode":"arena/monster/monster1-explode"})
        self.actor.setScale(0.3,0.3,0.3)
        self.actor.setHpr(180,0,0)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("attack")
        self.actor.showThrough()

class Arrow(object):
    def __init__(self):
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('arrow')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(0,0,2)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.actor = Actor("arena/squarrow/squarrow-model",{"indicate":"arena/squarrow/squarrow-anim"})
        self.actor.setScale(0.2,0.2,0.2)
        self.actor.setPos(0,0,-0.5)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("indicate")
        LerpHprInterval(self.collisionNodePath,2,Vec3(360,0,0)).loop()
    def highlight(self,nodePath):
        self.collisionNodePath.reparentTo(nodePath)
        self.actor.showThrough()
    def hide(self):
        self.actor.hide()




class Panda(object):
    def __init__(self):
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('panda')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(-2,10,0)        
        self.actor = Actor("arena/panda/panda-model",{"walk":"arena/panda/panda-walk4"})
        self.actor.setScale(0.003,0.002,0.003)
        self.actor.setPos(0,0.1,-1)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("walk")
        self.actor.showThrough()




class Spider(DirectObject):
    def __init__(self,i):
        DirectObject.__init__(self)
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('spider'+i)
        self.collisionNode.setIntoCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(0,9,1)
        base.cTrav.addCollider(self.collisionNodePath, base.collisionHandlerEvent)
        self.actor = Actor("arena/spider/spider",{"walk":"arena/spider/spider-walk","run":"arena/spider/spider-run","death":"arena/spider/spider-death"})
        self.actor.setScale(0.4,0.4,0.9)
        self.actor.setPos(-0.3,-0.2,-1)
        self.actor.reparentTo(self.collisionNodePath)
        self.actor.loop("run")
        self.accept('sonic-i-spider'+i,self.die)
        self.accept('tails-i-spider'+i,self.die)
    def shot(self,x):
        self.actor.showThrough()
        self.collisionNodePath.setPos(x,8,1)
        LerpPosInterval(self.collisionNodePath,3,Point3(x,-8,1)).start()
    def die(self,entry):
        self.actor.loop('death')
        self.collisionNode.setIntoCollideMask(BitMask32.bit(0))
        self.actor.hide()
        base.audio.death()


class Elevator(Actor):
    def __init__(self):
        Actor.__init__(self,"arena/elevator/elevator",{"open":"arena/elevator/elevatordooropenanim"})
        self.setScale(1,1,1)
        self.setPos(50,-50,0)
        self.reparentTo(render)
        self.loop("open")

class Tombstone(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.collisionSphere = CollisionSphere(0,0,0,1)
        self.collisionNode = CollisionNode('tombstone')
        self.collisionNode.setCollideMask(BitMask32.bit(1))
        self.collisionNode.addSolid(self.collisionSphere)
        self.collisionNodePath = render.attachNewNode(self.collisionNode)
        self.collisionNodePath.setPos(0,8,1)
        base.cTrav.addCollider(self.collisionNodePath,base.collisionHandlerEvent)
        self.model = loader.loadModel("arena/tombstone/tombstone")
        self.model.setScale(1.5,1.5,1.5)
        self.model.setPos(0,0,-0.9)
        self.model.reparentTo(self.collisionNodePath)
        self.model.showThrough()
        self.accept('Spider',self.raiseSpider)
        self.i = 0;
    def raiseSpider(self):
        self.spiders[self.i].shot(self.collisionNodePath.getX())
        self.i = (self.i + 1) % 50        
    def batch(self):
        def move():
            pos = Point3(random.uniform(-8,8),7,1)
            self.raiseSpider()
            LerpPosInterval(self.collisionNodePath,0.3,pos).start()
        ivals=[]
        for i in range(50):
            ivals.append(Func(move))
            ivals.append(Wait(.5))
        Sequence(*ivals).start()






    # def initPanda(self):
    #     self.pandaActor = Actor("models/panda-model",{"walk":"models/panda-walk4"})
    #     self.pandaActor.setScale(0.02,0.02,0.02)
    #     self.pandaActor.reparentTo(render)
    #     self.pandaActor.loop("walk")
        # pandaPosInterval1 = self.pandaActor.posInterval(1.3, Point3(0,-10,0), startPos=Point3(0,10,0))
        # pandaPosInterval2 = self.pandaActor.posInterval(1.3, Point3(0,10,0), startPos=Point3(0,-10,0))
        # pandaHprInterval1 = self.pandaActor.hprInterval(.3, Point3(180,0,0), startHpr=Point3(0,0,0))
        # pandaHprInterval2 = self.pandaActor.hprInterval(.3, Point3(0,0,0), startHpr=Point3(180,0,0))
        # self.pandaPace = Sequence(pandaPosInterval1, pandaHprInterval1, pandaPosInterval2, pandaHprInterval2, name="pandaPace")
        # self.pandaPace.loop()
        # self.pandaCollisionSphere = CollisionSphere(0,0,0,1.5)
        # self.pandaCollisionNode = CollisionNode('pandacnode')
        # self.pandaCollisionNode.setCollideMask(BitMask32.bit(1))
        # self.pandaCollisionNode.addSolid(self.pandaCollisionSphere)
        # self.pandaCollisionNodePath = self.pandaActor.attachNewNode(self.pandaCollisionNode)
        # self.pandaCollisionNodePath.show()

        # base.cTrav.addCollider(self.pandaCollisionNodePath,base.collisionHandlerEvent)   




#add some text
# bk_text = "This is my Demo"
# textObject = OnscreenText(text = bk_text, pos = (0.95,-0.95), 
# scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)

# def setText(textEntered):
#     textObject.setText(textEntered)
 
# #clear the text
# def clearText():
#     b.enterText('')

# with open('infiniteloop/NewQuestion.txt','r') as myfile:
#     data=myfile.read()

# def itemSel(arg):
#     if(arg):
#         output = "Button Selected is: Yes"
#     else:
#         output = "Button Selected is: No"
#     textObject.setText(output)
 
#add button
# dialog = DirectPrompt(left='PREV',right='NEXT',dialogName="YesNoCancelDialog", text=data, command=itemSel)
# run()