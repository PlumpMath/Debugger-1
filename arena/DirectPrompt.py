from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.gui.DirectFrame import *
from direct.gui.DirectButton import *
import types

class DirectPrompt(DirectDialog):
    def __init__(self,left='',right='', parent = None, **kw):
        # Inherits from DirectFrame
        optiondefs = (
            # Define type of DirectGuiWidget
            ('buttonTextList',  [left,right],       DGG.INITOPT),
            ('buttonValueList', [0,1],          DGG.INITOPT),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)
        DirectDialog.__init__(self, parent)
        self.inputEntry = self.createcomponent(
                'entry', (), "entry",
                DirectEntry, (self,),
                scale=.05,
                command=self.setPromptText,
                initialText="Type Something", 
                numLines = 2,
                focus=1,
                focusInCommand=self.clearPromptText,
                )
        self.inputEntry.reparentTo(self)
        self.initialiseoptions(DirectPrompt)
    def setPromptText(self,text):
    	print text
    def clearPromptText(self):
    	self.inputEntry.enterText('')
    def configureDialog(self):
    	DirectDialog.configureDialog(self)
    	self.inputEntry.setPos(-0.24,0,self.getChildren()[0].getPos()[2]+0.15)
    	for child in self.getChildren():
    		print child.getPos()
