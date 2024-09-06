# Mnesarco's Utils for **FreeCAD**

This project provides a pack of FreeCAD utilities:

* Camera POV Saver
* 8D+ FreeCAD HyperController
* Direct Scripting with exported bindable functions and variables
* Custom python paths configurator
* Bindable Timers
* Physical external KeyPad (Macro keyboard)


## Requirements

* Python 3.8+
* **FreeCAD 0.21+**
* pyserial (if you will use HyperController)

## Installation Method 1: zip

Download this repository as a zip file, and extract into your FreeCAD extensions dir:

* Old FreeCAD versions: `$HOME/.FreeCAD/Mod`
* New FreeCAD versions: `$HOME/.local/share/FreeCAD/Mod`

Then restart FreeCAD.


## Installation Method 2: git

Clone this repository inside your FreeCAD extensions dir:

* Old FreeCAD versions: `$HOME/.FreeCAD/Mod`
* New FreeCAD versions: `$HOME/.local/share/FreeCAD/Mod`

```bash
cd ~/.local/share/FreeCAD/Mod

git clone https://github.com/mnesarco/FreeCAD_Utils.git

``` 

Then restart FreeCAD.

## Installation Method 3: Addon manager (Preferred)

Use the Addon Manager, search for Utils, Install.

## HyperController

HyperController is a hardware device for 3D space navigation and
manipulation inside FreeCAD. It features 8+ DOF capabilities.

https://github.com/mnesarco/HyperController.git


## Note about pyserial

HyperController requires pyserial, if you are running an installed version of FreeCAD using system's python3, just install pyserial in your system using your prefered method. But if you are using an AppImage, it probably will not have pyserial installed and system libs will not be used. In that case, you can use the custom Python path configurator (included in this pack) to search for pyserial from an arbitrary directory, just download and extract pyserial into a directory and then add its path to the **additional python paths** and restart FreeCAD.

* Official pyserial source: https://pypi.org/project/pyserial/#files
* How to install it in FreeCAD (the easy way): https://www.youtube.com/watch?v=GkiOFCtvPws

## Forum threads

* Main Thread: https://forum.freecadweb.org/viewtopic.php?f=9&t=55511
* Keypad: https://forum.freecadweb.org/viewtopic.php?f=24&t=55374
* 8D Space Controller: https://forum.freecadweb.org/viewtopic.php?f=24&t=54367
* Scripting utilities: https://forum.freecadweb.org/viewtopic.php?f=22&t=54026

## Videos

* Scripting: https://www.youtube.com/watch?v=WnlR2qCRbKI
* Python Path config: https://www.youtube.com/watch?v=GkiOFCtvPws
* Camera (POV) saver: https://www.youtube.com/watch?v=iGuCerRy0vE
* HyperController: https://www.youtube.com/watch?v=o9VPcpPox0Q
* Remote Control: https://www.youtube.com/watch?v=Yc3DguSp8wA

