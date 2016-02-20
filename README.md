Scripts for dealing with torrent files and transfers. These should not depend on any external requirements, so that novices can run them with ease and without having to install och configure anything.

transmission_announce_edit.py
-----------------------------
Use this to replace a string in the announce field of all trackers in all active transfers in Transmission for Mac. Make sure you enable remote access in Transmission first, since the script talks through the RPC interface.

#### Instructions

1. Enable remote access in Transmission. It's in Preferences > Remote. Also check the "Only allow…" box and make sure `127.0.0.1` is in the list. 
2. Download the script `transmission_announce_edit.py` from [this link](https://raw.githubusercontent.com/alvaray/torrent/master/transmission_announce_edit.py).
3. Open a new Terminal window, type `python` in it and a space, then drag the downloaded script to the window to insert its path.
4. Press enter and follow the instructions:
    1. For the first and second choice, just press enter
    2. For the third choice, enter the string you want to replace, e.g. `theoldtracker.com`
    3. For the fourth choice, enter the string you want to replace it with, e.g. `thenewtracker.com`
5. Done!
6. Make sure you disable remote access in Transmission again, for your own security.
