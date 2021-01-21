# -*- coding: utf-8 -*-
# 
# Copyright (C) 2021 Frank David Martinez M. <https://github.com/mnesarco/>
# 
# This file is part of Utils.
# 
# Utils is free software: you can redistribute it and/or modify
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
from freecad.mnesarco.utils.extension import DocumentObject, DocumentObjectGui, Property, log, show_task_panel
from freecad.mnesarco import App, Gui
from freecad.mnesarco.utils.qt import QtCore
from freecad.mnesarco.utils.math import sign


class TimerObject(DocumentObject):

    def __init__(self, obj):
        super(TimerObject, self).__init__(obj)
        obj.addProperty(Property.Integer, 'Time', 'Output', 'Current tick', Property.Flag_ReadOnly).Time = 0
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

    def onChanged(self, feature, prop):
        obj = self.get_object()

        if prop == 'TPS':
            if obj.TPS > 30:
                obj.TPS = 30.0
            elif obj.TPS < 0:
                obj.TPS = 1.0
            if hasattr(obj, 'Enabled') and obj.Enabled:
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
                self.stop()

    def start(self, obj):
        self.stop()
        log(tr("Starting timer {}").format(obj.Name))
        obj.Time = obj.Start
        self.timer = QtCore.QTimer()
        speed = int(1000 / obj.TPS)
        self.timer.setInterval(speed)
        self.timer.timeout.connect(self.timeout) 
        self.timer.start()

    def stop(self):
        timer = getattr(self, 'timer', None)
        if timer:
            try:
                timer.stop()
                timer.deleteLater()
                timer = None
            except RuntimeError:
                pass

    def timeout(self):
        obj = self.get_object()
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
            log(tr("Timer {} ({}) = {}").format(obj.Label, obj.Name, time))
        App.ActiveDocument.recompute()

    @staticmethod
    def create_object():
        if not App.ActiveDocument:
            App.newDocument()       
        obj = DocumentObject.create('Timer', TimerObject, TimerObjectGui)
        App.ActiveDocument.recompute()
        return obj


class TimerObjectGui(DocumentObjectGui):

    Icon = Icons.timer

    def __init__(self, vobj):
        super(TimerObjectGui, self).__init__(vobj)

    def doubleClicked(self, vobj):
        self.Object.Proxy.stop()
        form = ManualTimeSlider(self.Object)
        show_task_panel(form)


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
        slider.setValue(obj.Time)
        slider.valueChanged.connect(self.value_changed)
        self.form.setWindowTitle(tr("Manual control: {}").format(obj.Label))
        self.form.label.setText(tr("Time: {}").format(obj.Time))

    def value_changed(self, v):
        self.object.Time = v
        self.form.label.setText(tr("Time: {}").format(v))
        App.ActiveDocument.recompute()


def init_gui_timers():
    add_global_action(
        name="CreateTimer",
        icon=Icons.timer,
        action=TimerObject.create_object,
        menu=tr("Create Timer"),
        activation=lambda: True
    )


