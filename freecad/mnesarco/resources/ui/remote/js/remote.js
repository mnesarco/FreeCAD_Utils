// -*- coding: utf-8 -*-
// 
// Copyright (C) 2021 Frank David Martinez M. <https://github.com/mnesarco/>
// 
// This file is part of Mnesarco Utils.
// 
// Mnesarco Utils is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// Utils is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with Mnesarco Utils.  If not, see <http://www.gnu.org/licenses/>.
// 

var pageCacheCount = 0;
var pageCache = {}; // CachedPage { id, stylesheet }
var textLengthThreshold = 18;
var navHistory = [];


function fcInit() {
    setTimeout(loadAllWorkbenches, 50);
    initNoSleep();
    window.loadedWorkbenches = {};
    document.querySelector("#btn-all-workbenches").addEventListener("click", loadAllWorkbenches, false);
    document.querySelector("#btn-all-macros").addEventListener("click", loadAllMacros, false);
    document.querySelector("#btn-back").addEventListener("click", historyBack, false);
}


function loadAllWorkbenches() {
    getPage('/workbenches', onWorkbenchActivated);
}


function loadAllMacros() {
    getPage('/macros');
}


function onWorkbenchActivated(action, data) {
    getPage('/workbench-actions/' + data.workbench);
}


function onPageChanged() {
    document.querySelector("#btn-back").style.display = navHistory.length > 1 ? 'block' : 'none';
}


function historyAdd(url) {
    var tmp = [];
    for (var i=0; i<navHistory.length; i++) {
        if (navHistory[i] === url) {
            break;
        }
        tmp.push(navHistory[i]);
    }
    tmp.push(url);
    navHistory = tmp;
    onPageChanged();
}


function historyBack() {
    if (navHistory.length > 1) {
        navHistory.pop();
        setCachedPage(navHistory[navHistory.length - 1]);
    }
}


function Button(text, icon, action, onCompleted) {
    var group = document.createElement('div');
    group.classList.add(text.length > textLengthThreshold ? 'button-wide' : 'button')
    var img = document.createElement('img');
    img.src = icon;
    var label = document.createElement('span');
    label.innerHTML = text;
    group.title = text;
    group.appendChild(img);
    group.appendChild(label);
    var handler = function(a, d) {
        img.src = icon;
        if (onCompleted) {
            onCompleted(a, d);
        }
    };
    group.addEventListener('click', function() {
        img.src = "img/ajax-loader.gif";
        sendAction(action, handler);
    });
    return group;
}


function PageSection(section, withHeader, root, onActionCompleted) {
    if (withHeader) {
        var header = document.createElement('div');
        header.classList.add('section-header');
        header.title = section.title;
        root.appendChild(header);
    }
    for (var i=0; i<section.actions.length; i++) {
        var data = section.actions[i];
        root.appendChild(Button(data.title, data.icon, data.action, onActionCompleted));
    }
}


function setCachedPage(url) {
    var cache = pageCache[url];
    if (cache) {
        clearRoot();
        document.querySelector("#stylesheet").href = cache.stylesheet;
        document.querySelector("#" + cache.id).style.display = 'block';
        historyAdd(url);
        return true;
    }
    return false;
}


function getPage(url, onActionCompleted) {    
    if (!setCachedPage(url)) {
        fetch(url, {method: 'POST', mode: 'same-origin'})
            .then(function(r) { return r.json(); })
            .then(function(page) { 
                setPage(url, page, onActionCompleted); 
            })
    }
}


function setPage(url, page, onActionCompleted) {
    clearRoot();
    document.querySelector("#stylesheet").href = page.stylesheet;
    var pageId = 'cached-page-' + (pageCacheCount++);
    var el = document.createElement('div');
    el.classList.add('page');
    el.id = pageId;
    var singleSection = page.sections.length === 1;
    for (var s = 0; s < page.sections.length; s++) {
        PageSection(page.sections[s], !singleSection, el, onActionCompleted);
    }
    pageCache[url] = {
        id: pageId,
        stylesheet: page.stylesheet
    };
    var fcRoot = document.querySelector('#fc-root');
    fcRoot.appendChild(el);
    historyAdd(url);
}


function sendAction(action, onCompleted) {
    setTimeout(function() {
        fetch(action, {method: 'POST', mode: 'same-origin'})
            .then(function(r) { return r.json(); })
            .then(function(data) { 
                if (onCompleted) {
                    onCompleted(action, data);
                }    
            })
    }, 1);
}


function initNoSleep() {
    var noSleep = new NoSleep();        
    var wakeLockEnabled = false;
    var toggleEl = document.querySelector("#btn-wake-lock");
    toggleEl.addEventListener('click', function() {
        if (!wakeLockEnabled) {
            noSleep.enable();
            wakeLockEnabled = true;
            toggleEl.innerHTML = '<img src="img/pin_gray.svg" alt="Wake unlock" />';
            if (document.documentElement && document.documentElement.webkitRequestFullScreen) {
                document.documentElement.webkitRequestFullScreen();
            }        
        } 
        else {
            noSleep.disable();
            wakeLockEnabled = false;
            toggleEl.innerHTML = '<img src="img/pin.svg" alt="Wake lock" />';
        }
    }, false);
}


function clearRoot() {
    var nodes = document.querySelectorAll("#fc-root > div.page");
    for (var i = 0; i < nodes.length; i++) {
        nodes[i].style.display = 'none';
    }
}

