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

# a hues mul entry consists of:
# HueEntry
# WORD ColorTable[32];
# WORD TableStart;
# WORD TableEnd;
# CHAR Name[20];
# HueGroup
# DWORD Header;
# HueEntry Entries[8]; 

import struct

class THue(object):
	colors = []
	start = 0
	end = 0
	name = ""
	def __init__(self, datapack = None):
		if datapack:
			self.applyData(datapack)
	def applyData(self, datapack):
		if isinstance(datapack, tuple):
			if len(datapack) >= 34:
				self.colors = []
				for x in range(0, 32):
					self.colors += [ int(datapack[x]) ]
				self.start = int(datapack[32])
				self.end = int(datapack[33])
				self.name = str(datapack[34])
		
	def toQtColor(self, brightness):
		if (len(self.colors) == 32) and (brightness in range(0,32)):
			color = self.colors[brightness]
			r = color >> 10
			g = (color-(r << 10)) >> 5
			b = color -(r << 10) -(g << 5)
			r = (r * 255) / 31
			g = (g * 255) / 31
			b = (b * 255) / 31
			try:
				from PyQt4.QtGui import QColor
				ret = QColor( r, g, b )
				return ret
			except:
				return None
		return None

class THuesMul(object):
	headerlist = []
	colorlist = []
	def __init__(self, fname = None):
		self.colorlist = []
		self.headerlist = []
		self.nameslist = []
		self.qtcolors = None
		if fname:
			self.loadFromFile(fname)
	def loadFromFile(self, fname):
		f = open(fname, 'rb')
		data = f.read()
		entry = "32hhh20s"
		entry_size = struct.calcsize(entry)
		group = "I" + str(entry_size*8) + "s"
		group_size = struct.calcsize(group)
		for x in range(0, len(data) / group_size):
			d_header, d_entry = struct.unpack_from(group, data, x * group_size)
			self.headerlist += [d_header]
			
			for i in range(0, 8):
				a_color=struct.unpack_from(entry, d_entry, i * entry_size)
				hue = THue(a_color)
				self.colorlist += [ hue ]
				self.nameslist += [ hue.name ]
	
	def countColorGroups(self):
		return len(self.headerlist)
	
	def countColors(self):
		return self.countColorGroups()*8
	
	def Color(self, num):
		if num < len(self.colorlist):
			return self.colorlist[num]
	
	def Name(self, num):
		if num < len(self.nameslist):
			return self.nameslist[num]
	
	def QtColors(self, num):
		if self.qtcolors:
			if num < len(self.qtcolors):
				return self.qtcolors[num]
			else:
				return None
	def QtColor(self, num, brightness):
		if self.qtcolors:
			if num < len(self.colorlist):
				return self.qtcolors[num][brightness]
			else:
				return None
		else:
			self.qtcolors = []
			for i in range(0, self.countColors()):
				c = []
				for z in range(0, 32):
					c += [ self.Color(i).toQtColor(z) ]
				self.qtcolors += [ c ]
			return self.QtColor(num, brightness)
