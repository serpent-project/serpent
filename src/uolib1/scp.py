############################################################################
#    Copyright (C) 2007 by Gabor Guzmics   #
#    gab@g4b.org   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU Library General Public License as       #
#    published by the Free Software Foundation; either version 2 of the    #
#    License, or (at your option) any later version.                       #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU Library General Public     #
#    License along with this program; if not, write to the                 #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

from g4borg.base.containers import *
import sys
import re
import os

def log(*args):
    pass
    #print args

def error(*args):
    print args

def find(rx, where):
    if not isinstance(where, str):
        return None
    r = re.compile(rx)
    s = r.search(where)
    if s:
        return str(s.group())
    else:
        return None

def findm(rx, where):
    r = re.compile(rx)
    s = r.match(where)
    if s:
        return str(s.group())
    else:
        return None

class scpentry(ObjectContainer):
    __def = []
    __events = []
    __comments = []
    __dtype = ""
    __dname = ""
    def __init__(self, dtype = "Unknown", dname = "~ERROR~", lines = []):
        self.__dtype = dtype
        self.__dname = dname
        self.__events = []
        self.__def = []
        self.__comments = []
        self.__lines = lines
        self.SetExpanding()
        self.parseItem(lines)
    
    def GetLines(self):
        return self.__lines
    
    def GetDType(self):
        return self.__dtype
    
    def GetDName(self):
        return self.__dname
        
    def parseItem(self, itemContent):
        pass
    
    def xml(self):
        pass
        #return "<%s name=%s />\n" % (self.__dtype, self.__dname)

class scpdef(scpentry):
    """Defines a Definition which holds Values and/or Events"""
    def parseItem(self, itemContent):
        actualevent = None
        for i in itemContent:
            # remove comments:
            l = i.split("//")[0].lstrip().rstrip()
            if len(l) == 0:
                continue
            # 1st we take ASD=XY and ASD XY as variables
            # if we encounter an event we change to event mode
            # Events look like this: ON_(=|_)_@Event (_=spaces)
            e = findm("^(o|O)(n|N)[\s]*(=|\s)[\s]*@\w+.*", l)
            if e:
                # this is a new event.
                # create event
                actualevent = find("@\w+", e).lower()
                # start filling of eventlines
                self[actualevent] = []
                continue
            if actualevent:
                # eventmode saves everything in the latest event
                self[actualevent] += [ l ]
            else:
                s = findm("^[^=\s]+.+", l)
                # look if s is valid
                if s:
                    # this is a variable of some sort (we hope)
                    # TODO: find out if its a tag
                    var = findm("^[^=\s]+", s).lower()
                    value = s[len(var)+1:].lstrip()
                    if len(value) == 0:
                        error("WARNING! %s %s" % (l, actualevent))
                        value=""
                    if value.startswith("="):
                        value = value[1:].lstrip()
                    self[var] = value
                else:
                    error("Invalid? %s " % (l))
        # release lines now.
        self.__lines = []
    def xml(self):
        ret = "<%s name=\"%s\">\n" % (self.GetDType(), self.GetDName())
        for i in self.getKeys():
            ret += "<%s>%s</%s>\n" % (i, self[i], i)
        ret += "</%s>\n" % (self.GetDType())
        return ret
    
    def filterKeysStartWith(self, startwith):
        ret = []
        for i in self.getKeys():
            if str(i).startswith(startwith):
                ret += [ i ]
        return ret

def scpfactory(dtype = "Unknown", dname = "~ERROR~", lines = []):
    if dtype == "ITEMDEF":
        return scp_itemdef(dtype, dname, lines)
    elif dtype == "TYPEDEF":
        return scp_typedef(dtype, dname, lines)
    elif dtype == "WORLDITEM":
        return scp_worlditem(dtype, dname, lines)
    elif dtype == "EVENTS":
        return scp_events(dtype, dname, lines)
    elif dtype == "FUNCTION":
        return scp_function(dtype, dname, lines)
    elif dtype == "DEFNAME":
        return scp_defname(dtype, dname, lines)
    else:
        return scpentry(dtype, dname, lines)

########## CLASSES WHICH HAVE NO SCPDEFS ########

class scp_function(scpentry):
    def parseItem(self, itemContent):
        pass

########## CLASSES WHICH HAVE SCPDEFS ###########
class scp_typedef(scpdef):
    pass

class scp_itemdef(scpdef):
    def xml(self):
        def octag(t, s):
            return "\t<%s>%s</%s>\n" % (t, s, t)
        def ctag(t, s):
            return "\t<%s %s />\n" % (t, s)
        ret = "<item id=\"%s\">\n" % (self.GetDName())
        #for i in self.getKeys():
        #    ret += "<%s>%s</%s>\n" % (i, self[i], i)
        keys = self.getKeys()
        if "id" in keys:
            ret += "\t<inherit id=\"%s\">\n" % (self["id"])
        elif "defname" in keys:
            ret += octag("id", self["defname"])
        if "name" in keys:
            ret += octag("name", self["name"])
        if "weight" in keys:
            ret += octag("weight", self["weight"])
        if "value" in keys:
            ret += octag("sellprice", self["value"])
            #ret += octag("buyprice", str(int(self["value"]) / 100 * 140))
        if "armor" in keys:
            ret += octag("defense", self["armor"])
        if "dye" in keys:
            if int(self["dye"]) == 0:
                ret += ctag("nodye", "")
            else:
                ret += ctag("dye", "")
        if "twohands" in keys:
            if self["twohands"].upper() == "Y":
                ret += ctag("twohanded", "")
            else:
                ret += ctag("singlehanded", "")
        
        if ("category" in keys) & ("subsection" in keys) & ("description" in keys):
            ret += octag("category", "%s\\%s\\%s" % (self["category"], self["subsection"], self["description"]))
        if ("reqstr" in  keys):
            ret += "\t<requires type='str'>%s</requires>\n" % (self["reqstr"])
        ret += "</item>\n"
        return ret 

class scp_events(scpdef):
    pass

class scp_worlditem(scpdef):
    pass

class scp_defname(scpdef):
    pass

class scpcontainer(ObjectFileContainer):
    def __init__(self, ofc = None):
        self.SetExpanding()
        if isinstance(ofc, ObjectFileContainer):
            self.data = ofc.data
            self.parseItems(self.parseSCP(self.data))
        elif isinstance(ofc, str):
            self.parseFile(ofc)

    def parseSCP(self, scpContent):
        # loop through the content
        x = 0
        header = -1
        items = []
        lines = []
        type = "COMMENT"
        name = "CONTENT"
        for i in scpContent:
            x += 1
            l = i.split("//")[0].lstrip().rstrip()
            # skip comment junk or empty lines
            if len(l) == 0:
                continue
            # skip eofs
            if l.upper() == "[EOF]":
                continue
            # we search for [(spaces)word(spaces)((word)(spaces))] 
            s = findm("^\[\s*\w+.*\]", l.lstrip().rstrip())
            if s:
                # we extract anything to ]
                s = find("\w+\s+[^\]]+", s)
                if not s:
                    continue
                # extract the type (first word + spaces)
                ntype = find("\w+\s+", s).rstrip().upper()
                # extract the description (first space + words until ])
                nname = find("\s+[^\]]+", s).lstrip().lower()
                log("parsing %s / %s in %s:%s" % (ntype, nname, self.filename, x))
                if not name:
                    error("Not found %s" % (type))
                    name = ""
                #if header >= 0:
                items += [ scpfactory(type, name, lines) ]
                #else:
                #    items += [ scpentry(type, name, lines) ]
                header += 1
		name = nname
		type = ntype
                lines = []
                continue
            lines += [ l ]
        # Last Item:
        if len(lines) > 0:
            items += [ scpfactory(type, name, lines) ]
        log("parsing done.")
        return items
    
    def parseItems(self, items):
        for i in items:
            t = i.GetDType()
            if not self[t]:
                self.addKey(t)
                self.setItem(t, [])
            log("adding %s in %s" % (t, self.filename))
            self[t] += [ i ]
    
    def parseFile(self, fname):
        self.data = []
        self.readFrom(fname)
        self.filename = fname
        self.parseItems(self.parseSCP(self.data))
        # release filedata again
        self.data = []
    
    def parseDir(self, dir, subdirs = True):
        names = os.listdir(dir)
        for name in names:
            if not name.startswith("."):
                if name.endswith(".scp"):
                    self.parseFile(os.path.join(dir, name))
                elif os.path.isdir(os.path.join(dir, name)) & subdirs:
                    self.parseDir(os.path.join(dir, name), subdirs)
                    
    def listSCP(self):
        #t = self['ITEMDEF']
        self.data = []
        for k in self.getKeys():
            self.data += [ "<b>%s</b>\n" % (k) ]
            t = self[k]
            for i in t:
                self.data += ["%s" % (i.xml()) ]
                #print i.GetLines()
        self.saveTo('/home/g4b/ergebnis.txt')
        #print i.GetLines()

def main(sDir):
    a = scpcontainer()
    a.parseDir(sDir, True)
    #a.listSCP()
    items = a['ITEMDEF']
    for item in items:
        if item['tag.allow_class']:
            cl = int( "0x%s" % item['tag.allow_class'], 0 )
            if cl & 0x080000000:
                print item['name']
                
    

# main("/home/g4b/work/alathair/scripte")
