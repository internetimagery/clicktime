import maya.cmds as cmds
import smartselection as sel
import time as t

# Created by Jason Dixon 14/03/14
# http://internetimagery.com

#REQUIRES SMART SELECTION SCRIPT

class clickTime(object):
    def __init__(self, snapshot = True):
        self.snapshot = snapshot
        self.pane = cmds.window( title = 'Click Timing', width = 200)
        cmds.columnLayout( adjustableColumn=True )
        cmds.button( label = 'Key Pose' , command = self.keypose , height= 20 )
        cmds.button( label = 'Load Poses' , command = self.loadposes , height= 20 )
        self.message = cmds.text( height = 30, label = 'Hello!')
        self.button = cmds.button( command = self.storeTime , height= 100, label = 'BIG ASS BUTTON!' )
        cmds.setParent('..')
        cmds.showWindow( self.pane )
        self.loadposes()
    def loadposes(self, *button):
        self.timestore = []
        self.basetime = []
        cmds.button( self.button, label = 'Begin Timing...' , edit = True )
        self.updateSelection()
        posenumber = len(self.basetime)
        cmds.button( self.button, edit = True, enable = False )
        cmds.text( self.message, label = 'Load in some poses...', edit = True )
        if posenumber:
            cmds.text( self.message, label = 'Only 1 pose loaded...', edit = True )
            if posenumber > 1:
                cmds.button( self.button, edit = True, enable = True )
                cmds.text( self.message, label = (str(len(self.basetime)) + ' poses animated in selection.'), edit = True )
                if button and self.snapshot:
                	cmds.currentTime( self.basetime[0] )
    def keypose(self, *args):
        selection = sel.smartSelection().get()
        if selection:
            for obj in selection:
            	cmds.setKeyframe( obj, at = ( selection[obj].keys() ) )
            self.loadposes()
    def updateSelection(self):
        self.selection = sel.smartSelection().get()
        if self.selection:
            self.basetime = list(set(cmds.keyframe( query = True )))
            self.basetime.sort()
            for obj in self.selection:
                for attr in self.selection[obj]:
                    common = []
                    new = []
                    breakdown = cmds.keyframe(obj, at=attr, q=True, bd=True)
                    for i in range(len(self.selection[obj][attr])):
                        if breakdown and self.selection[obj][attr][i] in breakdown:
                            new.append(True)
                        else:
                            new.append(False)
                        if self.selection[obj][attr][i] in self.basetime and not new[i]:
                            common.append(self.selection[obj][attr][i])
                    self.selection[obj][attr] = [ self.selection[obj][attr] , new ]
                    self.basetime = common
    def storeTime(self, *args):
        if self.selection:
            cmds.text( self.message, edit = True, label = 'Timing in Progress' )
            time = t.time()
            self.timestore.append( time )
            remain = len(self.basetime) - len(self.timestore)
            cmds.button( self.button, edit= True, label = (str(remain)+' poses left...') )
            if remain:
                if self.snapshot:
                    cmds.currentTime( self.basetime[(len(self.timestore))] )
            else: #last click
                cmds.text( self.message, edit = True, label = 'Timing out Poses.' )
                cmds.button( self.button, edit= True, label = 'Posing complete', enable = False)
                framerate = { 'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60, 'hour': 60, 'min': 60, 'sec': 60, 'millisec': 100 }
                rate = framerate[cmds.currentUnit( time = True, query = True )]
                start = self.timestore[0]
                self.newtime = []
                for i in range(len(self.timestore)):
                    self.timestore[i] = float( int( (self.timestore[i] - start) * rate ) )
                    if i:
                        if self.timestore[i] == self.timestore[(i-1)]: #fix duplicate frames
                            self.timestore[i] = self.timestore[i]+0.5
                        if self.timestore[i] < self.timestore[(i-1)]: #fix backward frames
                            self.timestore[i] = ((self.timestore[(i-1)] - self.timestore[i]) +0.5) + self.timestore[i]
                    self.newtime.append( self.timestore[i] + self.basetime[0] )
                if self.snapshot:
                    cmds.currentTime( self.basetime[0] )
                self.retime()
    def retime(self):
        if self.selection:
            for obj in self.selection:
                for attr in self.selection[obj]:
                    for i in range(len(self.newtime)-1):
                        l = i
                        r = i+1
                        basediff = self.basetime[r] - self.basetime[l]
                        newdiff = self.newtime[r] - self.newtime[l]
                        diff = newdiff - basediff
                        scale = ( 1 / basediff ) * newdiff
                        newbase = self.newtime[l] + basediff
                        self.breakdown( obj, attr, self.selection[obj][attr][1], False )
                        ott = cmds.keyTangent( obj, at=attr, time =(newbase,newbase), ott=True, query=True)[0]
                        oa = cmds.keyTangent( obj, at=attr, time = (newbase,newbase), oa= True, query = True)[0]
                        ow = cmds.keyTangent( obj, at=attr, time = (newbase,newbase), ow= True, query = True)[0]
                        cmds.keyTangent(  obj, at=attr, time = (newbase,newbase), lock = False, edit = True )
                        if diff > 0:
                            self.movekeys( obj, attr, diff, (newbase+0.01))
                            self.scalekeys( obj, attr, [self.newtime[l],newbase], scale, self.newtime[r] )
                        else:
                            self.scalekeys( obj, attr, [self.newtime[l],newbase], scale, self.newtime[r] )
                            self.movekeys( obj, attr, diff, (newbase+0.01))
                        cmds.keyTangent( obj, at=attr, e=True, time = (self.newtime[r],self.newtime[r]), oa= oa )
                        cmds.keyTangent( obj, at=attr, e=True, time = (self.newtime[r],self.newtime[r]), ow= ow )
                        cmds.keyTangent( obj, at=attr, e=True, time = (self.newtime[r],self.newtime[r]), ott= ott )
                        self.breakdown( obj, attr, self.selection[obj][attr][1], True )
    def breakdown(self, obj, attr, breaklist, state):
        if breaklist:
            for i in range(len(breaklist)):
                if breaklist[i]:
                    cmds.keyframe(obj, at=attr, index = (i,i), e = True, bd= state )
    def scalekeys(self, obj, attr, time, scale, newtime):
        cmds.scaleKey( obj, at=attr, time = (time[0],time[1]), tp =time[0], ts = scale )
    def movekeys(self, obj, attr, diff, time):
        cmds.keyframe( obj, at=attr, edit = True, time = (time,99999), tc = diff, r = True )

def GUI( snapshot = True):
	clickTime(snapshot)