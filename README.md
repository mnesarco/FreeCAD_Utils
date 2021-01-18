# Mnesarco's Utils for **FreeCAD**

This project provides a pack of FreeCAD utilities:

* Camera POV Saver
* 8D+ FreeCAD HyperController
* Direct Scripting with exported bindable functions and variables
* Custom python paths configurator
* Bindable Timers

## Requirements

* Python 3.5+
* **FreeCAD 0.19_pre+**
* pyserial (if you will use HyperController)

## HyperController

HyperController is a hardware device for 3D space navigation and
manipulation inside FreeCAD. It features 8+ DOF capabilities.

https://github.com/mnesarco/HyperController.git


## Installation Method 1: zip

Download this repository as a zip file, and extract into your FreeCAD extensions dir (usually `$HOME/.FreeCAD/Mod`).

Then restart FreeCAD.


## Installation Method 2: git

Clone this repository inside your FreeCAD extensions dir (usually `$HOME/.FreeCAD/Mod`).

```bash
cd ~/.FreeCAD/Mod

git clone https://github.com/mnesarco/FreeCAD_Utils.git

``` 

Then restart FreeCAD.

## Note about pyserial

HyperController requires pyserial, if you are running an installed version of FreeCAD using system's python3, just install pyserial in your system using your prefered method. But if you are using an AppImage, it probably will not have pyserial installed and system libs will not be used. In that case, you can use the custom Python path configurator (included in this pack) to search for pyserial from an arbitrary directory, just download and extract pyserial into a directory and then add its path to the **additional python paths** and restart FreeCAD.

Official pyserial source: https://pypi.org/project/pyserial/#files

