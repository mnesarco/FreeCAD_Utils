# -*- coding: utf-8 -*-
# 
# Copyright (C) 2021 Frank David Martinez M. <https://github.com/mnesarco/>
# 
# This file is part of Mnesarco Utils.
# 
# Mnesarco Utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mnesarco Utils.  If not, see <http://www.gnu.org/licenses/>.
# 

from freecad.mnesarco.utils.toolbars import add_global_action
from freecad.mnesarco.resources import Icons, get_ui, tr
from freecad.mnesarco.utils.extension import DocumentObject, DocumentObjectGui, Property, log, show_task_panel, close_task_panel
from freecad.mnesarco import App
from freecad.mnesarco.gui import Gui
from freecad.mnesarco.utils.qt import QtCore, QtGui
from freecad.mnesarco.utils.math import sign

class TimerRegistry:

    def __init__(self) -> None:
        self.target_doc = None
        self.timers = []

    def slotDeletedDocument(self, doc):
        log("Removing active timers...")
        keep = []
        for timer_doc, timer in self.timers:
            if doc == timer_doc:
                timer.stop()
                timer.deleteLater()
            else:
                keep.append((timer_doc, timer))
        self.timers = keep

    def register(self, doc, timer):
        self.timers.append((doc, timer))

    def unregister(self, doc, timer):
        keep = []
        for timer_doc, old_timer in self.timers:
            if doc != timer_doc or timer != old_timer:
                keep.append((timer_doc, old_timer))
        self.timers = keep

TIMER_REGISTRY = TimerRegistry()
App.addDocumentObserver(TIMER_REGISTRY)

class TimerObject(DocumentObject):

    def __init__(self, obj):
        super(TimerObject, self).__init__(obj)
        obj.addProperty(Property.Integer, 'Time', 'Output', 'Current tick', Property.Flag_ReadOnly).Time = 0
        obj.addProperty(Property.Integer, 'Value', 'Output', 'Alias of Time', Property.Flag_ReadOnly).Value = 0
        obj.addProperty(Property.Integer, 'Start', 'Limits', 'Start time').Start = 0
        obj.addProperty(Property.Integer, 'End', 'Limits', 'End time').End = 10
        obj.addProperty(Property.Integer, 'Step', 'Control', 'Step').Step = 1
        obj.addProperty(Property.Bool, 'Enabled', 'Control', 'Enabled').Enabled = False
        obj.addProperty(Property.Bool, 'Pendulum', 'Control', 'Oscilate between Start and End').Pendulum = False
        obj.addProperty(Property.Float, 'TPS', 'Control', 'Ticks Per Second').TPS = 1.0
        obj.addProperty(Property.Bool, 'Loop', 'Control', 'Auto Repeat').Loop = False
        self.timer = None

    def execute(self, obj):
        """This DocumentObject does not need recompute"""
        pass

    def onDocumentRestored(self, fp):
        #obj = self.get_object()
        self.FCName = fp.Name
        obj = fp
        if obj:
            obj.Enabled = False

    def onChanged(self, feature, prop):
        obj = feature
        #obj = self.get_object()

        if prop == 'TPS':
            if obj.TPS > 30:
                obj.TPS = 30.0
            elif obj.TPS < 0:
                obj.TPS = 1.0
            if hasattr(obj, 'Enabled') and obj.Enabled and hasattr(obj, 'Time') and hasattr(obj, 'Start'):
                self.start(obj)

        if prop == 'Step':
            if obj.Step < 0:
                obj.Step = -obj.Step
            elif obj.Step == 0:
                obj.Step = 1
            if hasattr(obj, 'Time') and hasattr(obj, 'Start'):
                obj.Time = obj.Start

        if prop == 'Enabled':
            if getattr(obj, 'Enabled', False):
                self.start(obj)
            else:
                self.stop(obj)

        if prop == 'Time' and hasattr(obj, 'Value'):
            obj.Value = obj.Time    

        if prop == 'Start' and hasattr(obj, 'Time'):
            obj.Time = obj.Start

        if prop == 'End' and hasattr(obj, 'Time'):
            obj.Time = obj.Start


    def start(self, obj):
        self.stop(obj)
        log(tr("Starting timer {}").format(obj.Name))
        obj.Time = obj.Start
        self.timer = QtCore.QTimer()
        speed = int(1000 / obj.TPS)
        self.timer.setInterval(speed)
        self.timer.timeout.connect(self.timeout) 
        self.timer.start()
        TIMER_REGISTRY.register(obj.Document, self.timer)


    def stop(self, obj):
        timer = getattr(self, 'timer', None)
        if timer:
            try:
                if obj:
                    TIMER_REGISTRY.unregister(obj.Document, timer)
                timer.stop()
                timer.deleteLater()
                timer = None
            except RuntimeError:
                pass

    def timeout(self):
        if App.ActiveDocument is None:
            return
        obj = self.get_object()
        if obj is None:
            return
        time_dir = sign(obj.Start, obj.End)
        self.cur_dir = getattr(self, 'cur_dir', 1)
        step = obj.Step * time_dir * self.cur_dir
        time = obj.Time + step
        after = sign(time, obj.End) != time_dir and obj.End != time
        before = sign(obj.Start, time) != time_dir and obj.Start != time
        if after:
            time = obj.End
        elif before:
            time = obj.Start
        if after or before:
            if obj.Pendulum:
                self.cur_dir = -self.cur_dir
                time = obj.Time - step
            elif obj.Loop:
                time = obj.Start
            else:
                obj.Enabled = False
        if time != obj.Time:
            obj.Time = time
            # log(tr("Timer {} ({}) = {}").format(obj.Label, obj.Name, time))
        App.ActiveDocument.recompute()

    @staticmethod
    def create_object(name):
        if not App.ActiveDocument:
            App.newDocument()       
        obj = DocumentObject.create(name, TimerObject, TimerObjectGui)
        App.ActiveDocument.recompute()
        return obj

    @staticmethod
    def create():       
        from .dialogs import CreatePanel
        dialog = CreatePanel(TimerObject.create_object)
        show_task_panel(dialog)        


class TimerObjectGui(DocumentObjectGui):

    Icon = Icons.timer

    def __init__(self, vobj):
        super(TimerObjectGui, self).__init__(vobj)

    def setEdit(self, vobj, mode=0):
        self.Object.Proxy.stop()
        show_task_panel(ManualTimeSlider(self.Object))

    def unsetEdit(self, vobj, mode=0):
        close_task_panel()

    def doubleClicked(self, vobj):
        self.setEdit(vobj, 0)


class ManualTimeSlider:

    def __init__(self, obj):
        self.form = Gui.PySideUic.loadUi(get_ui('timers', 'TimerSliderPanel.ui'))
        self.object = obj
        minval = min(obj.Start, obj.End)
        maxval = max(obj.Start, obj.End)
        slider = self.form.timeSlider
        slider.setMinimum(minval)
        slider.setMaximum(maxval)
        slider.setSingleStep(obj.Step)
        slider.valueChanged.connect(self.value_changed)
        slider.setValue(obj.Time)
        self.form.setWindowTitle(tr("Manual control: {}").format(obj.Label))
        self.form.label.setText(tr("Time: {}").format(obj.Time))

    def value_changed(self, v):
        self.object.Enabled = False
        self.object.Time = v
        self.form.label.setText(tr("Time: {}").format(v))
        App.ActiveDocument.recompute()


class ManualTimeSliderItem(ManualTimeSlider):

    def __init__(self, obj):
        super().__init__(obj)
        self.form.label.setText("{}: {}".format(obj.Label, obj.Time))

    def value_changed(self, v):
        self.object.Enabled = False
        self.object.Time = v
        self.form.label.setText("{}: {}".format(self.object.Label, v))
        App.ActiveDocument.recompute()


class AllTimers:

    def __init__(self) -> None:
        timers = [obj.Proxy for obj in App.ActiveDocument.Objects if hasattr(obj, 'Proxy') and obj.Proxy.__class__ is TimerObject]
        panel = QtGui.QDialog()
        panel.setWindowTitle(tr("Timers"))
        layout = QtGui.QVBoxLayout(panel)
        panel.setLayout(layout)

        buttonsWidget = QtGui.QWidget(panel)
        buttons = QtGui.QHBoxLayout(buttonsWidget)
        buttonsWidget.setLayout(buttons)

        layout.addWidget(buttonsWidget)

        # btnPlay = QtGui.QPushButton("Play")
        # btnPlay.clicked.connect(self.play)
        # buttons.addWidget(btnPlay)
        
        # btnStop = QtGui.QPushButton("Stop")
        # btnStop.clicked.connect(self.stop)
        # buttons.addWidget(btnStop)
        
        btnReset = QtGui.QPushButton("Reset")
        btnReset.clicked.connect(self.reset)
        buttons.addWidget(btnReset)       

        self.sliders = []
        for timer in timers:
            obj = timer.get_object()
            obj.Enabled = False
            slider = ManualTimeSliderItem(obj)
            slider.form.label.setText(obj.Label)
            self.sliders.append(slider)
            layout.addWidget(slider.form)
        self.form = panel

    def play(self):
        pass

    def stop(self):
        pass

    def reset(self):
        for slider in self.sliders:
            slider.object.Enabled = False
            slider.form.timeSlider.setValue(slider.object.Start)

    @staticmethod
    def show():
        if App.ActiveDocument:
            show_task_panel(AllTimers())


def init_gui_timers():

    add_global_action(
        name="CreateTimer",
        icon=Icons.timer,
        action=TimerObject.create,
        menu=tr("Create Timer"),
        activation=lambda: True
    )

    add_global_action(
        name="ShowTimers",
        icon=Icons.timers,
        action=AllTimers.show,
        menu=tr("Show all timers"),
        activation=lambda: True
    )

