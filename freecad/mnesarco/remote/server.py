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


import json, os, re, socket
from pathlib import Path
from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
from freecad.mnesarco.resources import tr, resources_path
from freecad.mnesarco import App, Gui
from freecad.mnesarco.utils import preferences, qt
from freecad.mnesarco.remote import macros, workbenches
from freecad.mnesarco.utils.extension import log_err, log
from freecad.mnesarco.remote.exports import get_exported_file, get_exported_macro, get_exported_action
from freecad.mnesarco.utils.dialogs import message_dialog, error_dialog


DOCROOT = resources_path.joinpath('ui', 'remote')
GUI_TIMEOUT = 6000
GUI_POLL = 300

class HTTPHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        path = get_exported_file(path)
        if path and Path(path).exists() and not Path(path).is_dir():
            return path
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath


    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        ctrl = router.get(self.path)
        if ctrl:
            try:
                ctrl.run(self)
            except BaseException as ex:
                self.wfile.write(json.dumps({'status': 'error', 'message': str(ex)}).encode())    
        else:
            self.wfile.write(json.dumps({'status': 'error', 'message': 'Unknown action'}).encode())


class RemoteCtrlServer(BaseHTTPServer):

    def __init__(self, base_path, server_address, rhc=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, rhc)


class ServerThread(qt.QtCore.QThread):
    
    def run(self):
        self.httpd = RemoteCtrlServer(DOCROOT, ("", preferences.get_mnesarco_pref('Remote', 'Port', kind=int, default=8521)))
        self.httpd.serve_forever()
    
    def stop(self):
        self.httpd.shutdown()
        self.httpd.socket.close()
        self.wait()

class GetWorkbenches:

    cache = None

    def run(self, request):
        if not GetWorkbenches.cache:
            GetWorkbenches.cache = workbenches.AllWorkbenchesPage()
        request.wfile.write(json.dumps(GetWorkbenches.cache.data()).encode())


class GetMacros:

    cache = None

    def run(self, request):
        if not GetMacros.cache:
            GetMacros.cache = macros.AllMacrosPage()
        request.wfile.write(json.dumps(GetMacros.cache.data()).encode())


class GetWorkbenchActions:

    cache = {}

    def run(self, request):
        wb = re.match('/workbench-actions/(.*)', request.path).group(1)
        cache = GetWorkbenchActions.cache.get(wb, None) 
        if not cache:
            cache = workbenches.WorkbenchPage(wb)
            GetWorkbenchActions.cache[wb] = cache
        request.wfile.write(json.dumps(cache.data()).encode())


class ActionController:

    def __init__(self):
        self.signal = qt.SignalObject(Gui.getMainWindow())
        self.signal.forward(self.pre_run_gui)
        self.lock = False

    def send_to_gui(self, *args):
        """Forward code to Gui Thread and wait for completion"""
        self.lock = True
        self.signal.trigger(*args)
        wait = 0        
        while self.lock and wait < GUI_TIMEOUT:
            qt.QtCore.QThread.msleep(GUI_POLL)
            wait += GUI_POLL
        self.lock = False

    def pre_run_gui(self, args):
        try:
            self.run_gui(args)
        except:
            pass
        self.lock = False

    def run(self, request):
        """Code to be executed in Server Thread"""
        pass

    def run_gui(self, args):
        """Implemented in subclasses"""
        pass


class ActivateWorkbench(ActionController):

    def __init__(self):
        super(ActivateWorkbench, self).__init__()

    def run_gui(self, args):
        Gui.activateWorkbench(args[0])

    def run(self, request):
        match = re.match('/workbench/(.*)', request.path)
        workbench = match.group(1)
        self.send_to_gui(workbench)
        request.wfile.write(json.dumps({'status': 'ok', 'workbench': workbench}).encode())


class RunMacro(ActionController):

    def __init__(self):
        super(RunMacro, self).__init__()

    def run_gui(self, args):
        macro = get_exported_macro(args[0])
        if macro:
            macro = Path(macro)
            try:
                Gui.doCommandGui("exec(open(\"{0}\").read())".format(macro.as_posix()))
            except BaseException as ex:
                log_err(tr("Error in macro: "), macro)
                log_err(ex)            
        else:
            log_err(tr("Macro {} does not exists").format(macro))            

    def run(self, request):
        match = re.match('/macro/(.*)', request.path)
        macro = match.group(1)
        self.send_to_gui(macro)
        request.wfile.write(json.dumps({'status': 'ok'}).encode())



class RunCommand(ActionController):

    def __init__(self):
        super(RunCommand, self).__init__()

    def run_gui(self, args):
        qaction = get_exported_action(args[0])
        if qaction:
            qaction.trigger()

    def run(self, request):
        match = re.match('/action/(.*)', request.path)
        key = match.group(1)
        self.send_to_gui(key)
        request.wfile.write(json.dumps({'status': 'ok', 'key': key}).encode())


class Router:

    routes = {
        '/workbenches': GetWorkbenches(),
        '/workbench/(.*)': ActivateWorkbench(),
        '/workbench-actions/(.*)': GetWorkbenchActions(),
        '/macros': GetMacros(),
        '/macro/(.*)': RunMacro(),
        '/action/(.*)': RunCommand(),
    }

    def get(self, path):
        for key, inst in Router.routes.items():
            match = re.match(key, path)
            if match:
                return inst


def get_local_ip():
    try:
        host = socket.gethostbyname_ex(socket.gethostname())
        ips = [ip for ip in host[2] if not ip.startswith("127.")]
        dns = [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]
        return [l for l in (ips[:1], dns) if l][0][0]
    except BaseException:
        return None


router = Router()
main_thread = None


def start_remote_server():
    global main_thread
    if not main_thread:
        main_thread = ServerThread()
        main_thread.start()
    ip = get_local_ip()
    if ip:
        address = "http://{}:{}".format(ip, preferences.get_mnesarco_pref('Remote', 'Port', kind=int, default=8521))
        message_dialog(tr("You can connect your device to: {}").format(address))
        log("Remote address: {}".format(address))
    else:
        error_dialog(tr("Network address not detected"))
        log("Remote address: Not detected")
