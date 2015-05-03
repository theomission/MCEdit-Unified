# -*- coding: utf_8 -*-
#
# mclangres.py
#
# Collect the Minecraft internal translations.
#
'''
Use `.minecraft/assets/indexes/[version].json`. The version is the highest
found by default.
Find the file name containing the en_GB translation (en_US seem to not be
present).
Load the en_GB file and build a dictionnary: {'string': 'element name'}.
Find the file name corresponding to the current MCEdit language, and build
a dictionnary: {'element name': 'string'}.
Retrieve the current MCEdit language translation with getting the 'element
name' in the English dictionnary and getting the 'string' in the current
language dictionnary using this 'element name'.
'''

import re
import os
import codecs
from directories import getMinecraftLauncherDirectory, getDataDir
import logging
log = logging.getLogger(__name__)

indexesDirectory = os.path.join(getMinecraftLauncherDirectory(), 'assets', 'indexes')
objectsDirectory = os.path.join(getMinecraftLauncherDirectory(), 'assets', 'objects')

enRes = {}
serNe = {}
langRes = {}
serGnal = {}
enMisc = {}
csimNe = {}
langMisc = {}
csimGnal = {}

# Shall this be maintained in an external resource?
excludedEntries = ['tile.flower1.name',]

def getResourceName(name, data):
    match = re.findall('"minecraft/lang/%s.lang":[ ]\{\b*.*?"hash":[ ]"(.*?)",'%name, data, re.DOTALL)
    if match:
        return match[0]
    else:
        print 'Could not find %s resource name.'%name

def findResourceFile(name, basedir):
    for root, dirs, files in os.walk(basedir):
        if name in files:
            return os.path.join(basedir, root, name)

def buildResources(version=None, lang=None):
    log.debug('Building Minecraft language resources...')
    global enRes
    global serNe
    global langRes
    global serGnal
    global enMisc
    global csimEn
    global langMisc
    global csimGnal
    enRes = {}
    serNe = {}
    langRes = {}
    serGnal = {}
    enMisc = {}
    csimEn = {}
    langMisc = {}
    csimGnal = {}
    versions = os.listdir(indexesDirectory)
    if 'legacy.json' in versions:
        versions.remove('legacy.json')
    versions.sort()
    version = "%s.json"%version
    if version in versions:
        fName = os.path.join(indexesDirectory, version)
    else:
        fName = os.path.join(indexesDirectory, versions[-1])
    log.debug('Using %s'%fName)
    data = open(fName).read()
    name = getResourceName('en_GB', data)
    if name:
        fName = os.path.join(objectsDirectory, name[:2], name)
        if not os.path.exists(fName):
            fName = findResourceFile(name, objectsDirectory)
        if not fName:
            log.debug('Can\'t get the resource %s.'%name)
            log.debug('Nothing built. Aborted')
            return
        log.debug('Found %s'%name)
        lines = codecs.open(fName).readlines()
        for line in lines:
            if line.split('.')[0] in ['book', 'enchantment', 'entity', 'gameMode', 'generator', 'item', 'tile'] and line.split('=')[0].strip() not in excludedEntries:
                enRes[line.split('=', 1)[-1].strip()] = line.split('=', 1)[0].strip()
                serNe[line.split('=', 1)[0].strip()] = line.split('=', 1)[-1].strip()
        lines = codecs.open(os.path.join(getDataDir(), 'Items', 'en_GB'))
        for line in lines:
            enMisc[line.split('=', 1)[-1].strip()] = line.split('=', 1)[0].strip()
            csimNe[line.split('=', 1)[0].strip()] = line.split('=', 1)[-1].strip()
        log.debug('... Loaded!')
    else:
        return
    if not lang:
        lang = 'en_GB'
    log.debug('Looking for %s resources.'%lang)
    name = getResourceName(lang, data)
    if name:
        fName = os.path.join(objectsDirectory, name[:2], name)
        if not os.path.exists(fName):
            fName = findResourceFile(name, objectsDirectory)
        if not fName:
            log.debug('Can\'t get the resource %s.'%name)
            return
        log.debug('Found %s...'%name)
        lines = codecs.open(fName, encoding='utf_8').readlines()
        for line in lines:
            if line.split('.')[0] in ['book', 'enchantment', 'entity', 'gameMode', 'generator', 'item', 'tile'] and line.split('=')[0].strip() not in excludedEntries:
                langRes[line.split('=', 1)[0].strip()] = line.split('=', 1)[-1].strip()
                serGnal[line.split('=', 1)[-1].strip()] = line.split('=', 1)[0].strip()
        if os.path.exists(os.path.join(getDataDir(), 'Items', lang)):
            lines = codecs.open(os.path.join(getDataDir(), 'Items', lang))
            for line in lines:
                langMisc[line.split('=', 1)[0].strip()] = line.split('=', 1)[-1].strip()
                csimGnal[line.split('=', 1)[-1].strip()] = line.split('=', 1)[0].strip()
        log.debug('... Loaded!')
    else:
        return

def compound(char, string, pair=None):
    if pair is None:
        if char in '{[(':
            pair = '}])'['{[('.index(char)]
        else:
            pair = char
    name, misc = string.split(char, 1)
    name = name.strip()
    misc = [a.strip() for a in misc.strip()[:-1].split(',')]
    head = langRes.get(enRes.get(name, name), name)
    for i in range(len(misc)):
        if ' ' in misc[i]:
            if langMisc.get(enMisc.get(misc[i], False), False):
                misc[i] = langMisc.get(enMisc.get(misc[i], misc[i]), misc[i])
            elif langRes.get(enRes.get(misc[i], False), False):
                misc[i] = langRes.get(enRes.get(misc[i], misc[i]), misc[i])
            else:
                stop = [False, False]
                for j in range(1, misc[i].count(' ') + 1):
                    elems = misc[i].rsplit(' ', j)
                    if not stop[0]:
                        h = elems[0]
                        if langMisc.get(enMisc.get(h, False), False):
                            h = langMisc.get(enMisc.get(h, h), h)
                            stop[0] = True
                        elif langRes.get(enRes.get(h, False), False):
                            h = langRes.get(enRes.get(h, h), h)
                            stop[0] = True
                    if not stop[1]:
                        t = ' '.join(elems[1:])
                        if langMisc.get(enMisc.get(t, False), False):
                            t = langMisc.get(enMisc.get(t, t), t)
                            stop[1] = True
                        elif langRes.get(enRes.get(t, False), False):
                            t = langRes.get(enRes.get(t, t), t)
                            stop[1] = True
                        if stop[0]:
                            stop[1] = True
                misc[i] = ' '.join((h, t))
        elif '/' in misc[i]:
            misc[i] = '/'.join([langMisc.get(enMisc.get(a, a), translate(a)) for a in misc[i].split('/')])
        elif '-' in misc[i]:
            misc[i] = '-'.join([langMisc.get(enMisc.get(a, a), translate(a)) for a in misc[i].split('-')])
        elif '_' in misc[i]:
            misc[i] = '_'.join([langMisc.get(enMisc.get(a, a), translate(a)) for a in misc[i].split('_')])
        else:
            misc[i] = langRes.get(enRes.get(misc[i], misc[i]), misc[i])
    tail = '%s%s%s'%(char, ', '.join([langMisc.get(enMisc.get(a, a), a) for a in misc]), pair)
    return ' '.join((head, tail))

def translate(name):
    for c in '{[(':
        if c in name:
            return compound(c, name)
    return langRes.get(enRes.get(name, name), name)

def untranslate(name, case_sensitive=True):
    key = serGnal.get(name, None)
    value = serNe.get(key, None)
    return value or name

def search(text, untranslate=True): # Useless?
    text = text.lower()
    results = []
    for k, v in serGnal.items():
        if text in k.lower():
            if untranslate:
                results.append(serNe[v].lower())
            else:
                results.append(k.lower())
    return results
