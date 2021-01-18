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

import re
from freecad.mnesarco.utils.qt import QtCore, QtGui
from freecad.mnesarco import App, Gui
from freecad.mnesarco.resources.style.py_editor import stylesheet
from freecad.mnesarco.resources import tr


class SyntaxRule:

    def __init__(self, pattern, color, bold=False, background=None):
        self.format = QtGui.QTextCharFormat()
        self.format.setForeground(self.hex2color(color))
        if bold:
            self.format.setFontWeight(QtGui.QFont.Bold)
        if background:
            self.format.setBackground(self.hex2color(background))
            self.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

        self.pattern = pattern

    def hex2color(self, h):
        h = h.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return QtGui.QColor.fromRgb(*rgb)

    @staticmethod
    def keyword(kw, color):
        return SyntaxRule(re.compile(r'\b' + kw + r'\b'), color)


class PythonSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, doc):
        super(PythonSyntaxHighlighter, self).__init__(doc)
        # Keywords
        self.rules = [
            SyntaxRule.keyword(k, '#333333')
            for k in (
                'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
                'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
                'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'none',
                'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try',
                'while', 'with', 'yield'
            )
        ]
        self.rules += [
            # Comments
            SyntaxRule(re.compile(r'#[^\n]*'), "#315739"),
            # Tabs
            SyntaxRule(re.compile(r'\t+'), "#315739", background="#ff0000"),
        ]
        
    def highlightBlock(self, text):

        # Simple rules
        for rule in self.rules:
            for m in rule.pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), rule.format)
        self.setCurrentBlockState(0)

        # Functions
        rule = SyntaxRule(re.compile(r'def\s+(\w+)\s*\('), "#000099", True)
        for m in rule.pattern.finditer(text):
            self.setFormat(m.start(1), m.end(1) - m.start(1), rule.format)
        self.setCurrentBlockState(0)

        # Vars
        rule = SyntaxRule(re.compile(r'^(\w+)\s*=\s*([^\n]+)'), "#000099", bold=True)
        rule2 = SyntaxRule(None, "#990000", bold=True)
        for m in rule.pattern.finditer(text):
            self.setFormat(m.start(1), m.end(1) - m.start(1), rule.format)
            self.setFormat(m.start(2), m.end(2) - m.start(2), rule2.format)
        self.setCurrentBlockState(0)

        # Sections
        rule = SyntaxRule(re.compile(r'^SECTION\s*=\s*[^\n]+'), "#000000", background="#aaaaaa")
        for m in rule.pattern.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), rule.format)
        self.setCurrentBlockState(0)

        # return
        rule = SyntaxRule(re.compile(r'return\s*([^\n]+)'), "#990000", bold=True)
        for m in rule.pattern.finditer(text):
            self.setFormat(m.start(1), m.end(1) - m.start(1), rule.format)
        self.setCurrentBlockState(0)


class LineNumberArea(QtGui.QWidget):

    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QtGui.QSize(self.editor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QtGui.QPlainTextEdit):

    def __init__(self, *args):
        super(CodeEditor, self).__init__(*args)
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()     
        self.setTabStopWidth(16)
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.setStyleSheet(stylesheet)

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtGui.Qt.lightGray)

        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_num + 1)
                painter.setPen(QtGui.Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                    QtGui.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_num += 1
        

    def lineNumberAreaWidth(self):
        digits = 1
        max_ = max(1, self.blockCount())
        while max_ >= 10:
            max_ /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def resizeEvent(self, event):
        super(CodeEditor, self).resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def updateLineNumberAreaWidth(self, new_block_count):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def highlightCurrentLine(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QtGui.QTextEdit.ExtraSelection()
            line_color = QtGui.QColor(QtCore.Qt.yellow).lighter(200)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def sizeHint(self):
        return QtCore.QSize(600, 800)


class CodeEditorPanel:

    def __init__(self, name, file_name, highlighter=PythonSyntaxHighlighter, tab_size=4):

        self.form = QtGui.QDialog()
        self.form.setWindowTitle(tr("Edit: {}").format(str(file_name.name)))
        self.editor = CodeEditor()
        self.editor.appendPlainText(file_name.read_text())
        self.highlighter = highlighter(self.editor.document())
        self.error_message = QtGui.QLabel()
        self.file_name = file_name
        self.name = name
        self.tab_size = tab_size

        layout = QtGui.QVBoxLayout(self.form)       
        layout.addWidget(self.editor)
        layout.addWidget(self.error_message)
    

    def get_source(self):
        return self.editor.toPlainText().replace("\t", " " * self.tab_size)

    def get_object(self):
        return App.ActiveDocument.getObject(self.name)

    def compile(self):

        self.error_message.setText("")
        editor = self.editor
        source = self.get_source()
        try:
            compile(source, self.file_name, "exec")
            return True
        except SyntaxError as e:
            block = editor.document().findBlockByLineNumber(e.lineno-1)
            editor.moveCursor(QtGui.QTextCursor.End)
            editor.setTextCursor(QtGui.QTextCursor(block))
            self.error_message.setText("Line {0}: {1}".format(e.lineno, e.msg))
            return False


    def accept(self):

        if self.compile():
            self.file_name.write_text(self.get_source())
            obj = self.get_object()
            obj.enforceRecompute()
            App.ActiveDocument.recompute([obj])
            Gui.Control.closeDialog()


