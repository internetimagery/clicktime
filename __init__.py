# Time out animation by clicking
# Created By Jason Dixon. http://internetimagery.com
#
# Wrap the outermost function calls in the Report class
# As a decorator or as a context manager on the outermost function calls
# For instance, decorate your Main() function,
# or any function that is called directly by a GUI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import clicktime.selection as selection
import maya.cmds as cmds

class Main(object):
    """ Time out animations by clicking your mouse """
    def __init__(s):
        name = "clicktime_gui"
        s.selection = {}

        # if cmds.window(name, q=True, ex=True):
        #     cmds.deleteUI(name)
        #
        # win = cmds.window(t="Click Timing", w=200, rtf=True)
        # cmds.columnLayout(adj=True)
        # cmds.button(h=20, l="Key Pose", c="")
        # cmds.button(h=20, l="Load Poses", c="")
        #
        # s.message = cmds.text(h=30, l="Hello!")
        #
        # s.go_btn = cmds.button(h=100, l="BIG ASS BUTTON", c="")
        # cmds.showWindow(win)

    def load_poses(s):
        """ Load up poses. ie: Moments in time with a key on each frame. """
        cmds.button(s.go_btn, e=True, l="Begin Timing...")
        # update selection


        # self.timestore = []
        # self.basetime = []
        # cmds.button( self.button, label = 'Begin Timing...' , edit = True )
        # self.updateSelection()
        # posenumber = len(self.basetime)
        # cmds.button( self.button, edit = True, enable = False )
        # cmds.text( self.message, label = 'Load in some poses...', edit = True )
        # if posenumber:
        #     cmds.text( self.message, label = 'Only 1 pose loaded...', edit = True )
        #     if posenumber > 1:
        #         cmds.button( self.button, edit = True, enable = True )
        #         cmds.text( self.message, label = (str(len(self.basetime)) + ' poses animated in selection.'), edit = True )
        #         if button and self.snapshot:
        #         	cmds.currentTime( self.basetime[0] )

    def update_selection(s):
        """ Snag current selection """
        sel = selection.get_selection()
        base_time = sorted(set(b for a in sel for b in cmds.keyframe(a, q=True, tc=True) or [])) # get all times regardless of framerange
        for curve, keys in sel.iteritems():
            breakdowns = set(cmds.keyframe(curve, q=True, tc=True, bd=True) or []) # Ignore breakdowns!
            print curve, breakdowns

    # def updateSelection(self):
    #     self.selection = sel.smartSelection().get()
    #     if self.selection:
    #         self.basetime = list(set(cmds.keyframe( query = True )))
    #         self.basetime.sort()
    #         for obj in self.selection:
    #             for attr in self.selection[obj]:
    #                 common = []
    #                 new = []
    #                 breakdown = cmds.keyframe(obj, at=attr, q=True, bd=True)
    #                 for i in range(len(self.selection[obj][attr])):
    #                     if breakdown and self.selection[obj][attr][i] in breakdown:
    #                         new.append(True)
    #                     else:
    #                         new.append(False)
    #                     if self.selection[obj][attr][i] in self.basetime and not new[i]:
    #                         common.append(self.selection[obj][attr][i])
    #                 self.selection[obj][attr] = [ self.selection[obj][attr] , new ]
    #                 self.basetime = common

m = Main()
m.update_selection()
