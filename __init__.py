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
import itertools
import clicktime.selection as selection
import maya.cmds as cmds

def shift(iterable, size):
    """ iterate in groups ie [1,2,3] [2,3,4] """
    i = itertools.tee(iterable, size)
    for a, b in enumerate(i):
        for c in range(a):
            b.next()
    return itertools.izip(*i)

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
        s.move_slider = cmds.checkBox(h=20, l="Move Timeslider", v=True)

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
            coroutine = s.record_timing(cmds.checkBox(s.move_slider, q=True, v=True))
            next(coroutine)
            cmds.button(s.go_btn, e=True, c=lambda x: coroutine.send(time.time()))

    def record_timing(s, move_timeslider):
        """ Record our timing """
        poses = s.poses
        pose_times = []
        num_poses = len(poses)
        step = 100 / num_poses - 1
        message = "Timing in progress...\n[%s]"
        for i, curr in enumerate(poses):
            progress = (":"* int(i * step)).ljust(100, ".")
            cmds.text(s.message, e=True, l=message % progress)
            cmds.button(s.go_btn, e=True, l="%s poses left..." % (num_poses - i))
            if move_timeslider: cmds.currentTime(curr)
            t = (yield) # Time
            pose_times.append(t)
        if move_timeslider: cmds.currentTime(poses[0])

        cmds.button(s.go_btn, e=True, c=s.start_timing)
        s.reset_gui()

        # Now pose out our character!
        framerate = { 'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60, 'hour': 60, 'min': 60, 'sec': 60, 'millisec': 100 }
        rate = framerate.get(cmds.currentUnit(q=True, t=True))
        if rate:
            err = cmds.undoInfo(openChunk=True)
            try:
                start_time = pose_times[0] # Our start points
                start_frame = poses[0]
                offset = (int(((b - start_time) * rate) + a) for a, b in zip(poses, pose_times))
                new_frames = []
                for i, o in enumerate(offset): # Ensure we don't have doubleups if frames are too close together
                    if i:
                        i -= 1
                        if new_frames[i] == o: # If previous frame is the same, bump us forward a frame
                            o += 1
                        new_frames.append(o)
                    else:
                        new_frames.append(start_frame)

                curves = s.selection.keys()
                last_frame = cmds.findKeyframe(curves, which="last")

                for (f1, f2), (f3, f4) in itertools.izip(shift(poses, 2), shift(new_frames, 2)):
                    old_gap = f2 - f1 # Gap between frames
                    new_gap = f4 - f3
                    end_gap = last_frame - f3

                    scale = (1 / old_gap) if old_gap else 0 # Scale ammount
                    movement = new_gap * scale

                    cmds.scaleKey(curves, iub=True, t=(f3, last_frame), ts=movement, tp=f3)

                    new_end = end_gap * movement + f3 # Where has our end, ended up?
                    new_gap = new_end - f4
                    new_end_scale = (1 / new_gap) if new_gap else 0
                    last_frame = (f4 - (old_gap + f3)) + last_frame # Move last frame out a bit
                    return_move = (last_frame - f4) * new_end_scale

                    cmds.scaleKey(curves, iub=True, t=(f4, new_end), ts=return_move, tp=f4)

            except Exception as err:
                raise
            finally:
                cmds.undoInfo(closeChunk=True)
                if err: cmds.undo()
        else:
            cmds.confirmDialog(t="Oh no...", m="Frame rate could not be determined. :s")


m = Main()
