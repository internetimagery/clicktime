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

from __future__ import division

import time
import clicktime.selection as selection
import maya.cmds as cmds

class Main(object):
    """ Time out animations by clicking your mouse """
    def __init__(s):
        name = "clicktime_gui"
        s.selection = {}
        s.times = []
        s.dry_run = False
        s._curve_monitor = []
        s._selection_monitor = cmds.ls(sl=True, type="transform")
        s.active = False

        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        s.win = win = cmds.window(name, t="Click Timing", w=200, rtf=True)
        cmds.columnLayout(adj=True)
        cmds.button(h=20, l="Key Pose", c=s.key_full_pose)
        cmds.button(h=20, l="Load Poses", c=s.load_poses)

        s.message = cmds.text(h=30, l="Hello!")

        s.go_btn = cmds.button(h=100, en=False, l="BIG ASS BUTTON", c=s.start_timing)
        cmds.showWindow(win)
        s.reset_gui()
        cmds.scriptJob(e=("SelectionChanged", s.monitor_selection_changes), p=win)

    def reset_gui(s):
        """ Reset GUI """
        cmds.button(s.go_btn, e=True, l="Begin Timing...", en=False)
        cmds.text(s.message, e=True, l="Load in some poses.")
        s.active = False

    def load_poses(s, *from_button):
        """ Load up poses. ie: Moments in time with a key on each frame. """
        s.update_selection()
        pose_number = len(s.poses)
        s.times = []

        if pose_number:
            cmds.text(s.message, e=True, l="Only one pose loaded. :(")
            if 1 < pose_number:
                s.active = True
                cmds.button(s.go_btn, e=True, en=True)
                cmds.text(s.message, e=True, l="%s poses found in selection." % pose_number)
                if from_button:
                    cmds.currentTime(s.poses[0])
        elif from_button:
            cmds.confirmDialog(t="Oh no!", m="No poses found!")

    def monitor_curve_changes(s):
        """ Monitor changes to animations """
        def cleanup():
            for job in s._curve_monitor:
                if cmds.scriptJob(ex=job):
                    cmds.scriptJob(kill=job)
            s._curve_monitor = []
        if s.active:
            s.reset_gui()
        cmds.scriptJob(ie=cleanup, ro=True)

    def monitor_selection_changes(s):
        """ Follow changes to selection """
        sel = cmds.ls(sl=True, type="transform")
        if s._selection_monitor != sel:
            s._selection_monitor = sel
            if s.active:
                s.reset_gui()

    def update_selection(s):
        """ Snag current selection """
        s.selection = sel = selection.get_selection()
        common = set(b for a in sel for b in cmds.keyframe(a, q=True, tc=True) or []) # get all times regardless of framerange
        for curve, keys in sel.iteritems(): # Find all frames that have a keyframe each channel
            new = set(a for a, b, c in keys if not c)
            common &= new
            cmds.scriptJob(ac=("%s.a" % curve, s.monitor_curve_changes), p=s.win, ro=True)
        s.poses = sorted(common)

    def key_full_pose(s, *_):
        """ Key a pose at the current time """
        sel = selection.get_selection()
        curves = sel.keys()
        if curves:
            cmds.setKeyframe(curves, i=True)
            s.reset_gui()

    def start_timing(s, *_):
        """ Begin timing """
        if s.poses:
            coroutine = s.record_timing(False)
            next(coroutine)
            cmds.button(s.go_btn, e=True, c=lambda x: coroutine.send(time.time()))

    def record_timing(s, move_timeslider):
        """ Record our timing """
        pose_times = []
        num_poses = len(s.poses)
        step = 100 / num_poses - 1
        message = "Timing in progress...\n[%s]"
        for i in range(1, num_poses):
            progress = (":"* int(i * step)).ljust(100, ".")
            cmds.text(s.message, e=True, l=message % progress)
            cmds.button(s.go_btn, e=True, l="%s poses left..." % (num_poses - i))
            t = (yield) # Time
            pose_times.append(t)

        cmds.button(s.go_btn, e=True, c=s.start_timing)
        s.reset_gui()

        # Now pose out our character!
        framerate = { 'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60, 'hour': 60, 'min': 60, 'sec': 60, 'millisec': 100 }
        rate = framerate.get(cmds.currentUnit(q=True, t=True))
        if rate:
            start = pose_times[0]


            pass
        else:
            cmds.confirmDialog(t="Oh no...", m="Frame rate could not be determined. :s")



    #             start = self.timestore[0]
    #             self.newtime = []
    #             for i in range(len(self.timestore)):
    #                 self.timestore[i] = float( int( (self.timestore[i] - start) * rate ) )
    #                 if i:
    #                     if self.timestore[i] == self.timestore[(i-1)]: #fix duplicate frames
    #                         self.timestore[i] = self.timestore[i]+0.5
    #                     if self.timestore[i] < self.timestore[(i-1)]: #fix backward frames
    #                         self.timestore[i] = ((self.timestore[(i-1)] - self.timestore[i]) +0.5) + self.timestore[i]
    #                 self.newtime.append( self.timestore[i] + self.basetime[0] )
    #             if self.snapshot:
    #                 cmds.currentTime( self.basetime[0] )
    #             self.retime()


m = Main()
