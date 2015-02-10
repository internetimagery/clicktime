# Clicktime

A Maya tool that allows you to retime your animation in REALTIME using mouseclicks. Much like clicking a stopwatch.

# Installation:

Simply copy the folder into your scripts directory in Maya. The folder should be named "clicktime". If not, rename it that.

# Usage

Within Maya, create a shelf icon with the following PYTHON code:

	import clicktime
	clicktime.GUI()

Clicktime defines "Poses" as moments in time that have a keyframe on every animated channel, on every object you have selected. If you have missed out on a key by mistake and just can't seem to get it to register a pose. You can go to that frame and click the button "Key Pose" to key every channel at that time.

* Select the object(s) you wish to time out.

* Click "Load Poses" to load the poses up. A number will be displayed detailing the found poses. Double check this number is what you were expecting before moving on. You can select keyframes / Pick a different timeslider range / Highlight in the timeslider to limit the keys loaded.

* Click the "Begin timing" button once for every pose. FROM THE MOMENT YOU CLICK THE BUTTON YOU ARE ON THE CLOCK. Be sure you know and have rehersed your timing before you press the button. The first press corresponds to the first pose, which will stay at its current time.