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

import re
from struct import unpack, pack, calcsize

# Converts 2-byte string to little-endian short value.
# unpack returns a tuple, so we grab the first (and only) element.
def short(x):
	return unpack("<H", x)[0]

def dword(x):
	return unpack("L", x)[0]

def word(x):
	return unpack("I", x)[0]

class binaryReader():
	def __init__(self, format = ""):
		self.__format = ""
	def parse(buf):
		# Compile a regex that can parse a buffer with an arbitrary number of
		# records, each consisting of dataformat
		# Incomplete records at the end of the file 
		# will be ignored.  re.DOTALL ensures we treat newlines as data.
		# example: r = re.compile("(..)(.*?)\0(..)(..)", re.DOTALL)
		r = re.compile(self.__regex , re.DOTALL)
		# packed will be a list of tuples
		# You can use finditer instead to save memory on a large file, but
		# it will return MatchObjects rather than tuples.
		packed = r.findall(buf)
		# Create an unpacked list of tuples, mirroring the packed list.
		# Perl equivalent: @objlist = unpack("(S Z* S S)*", $buf);
		# Note that we do not need to unpack the string, because its 
		# packed and unpacked representations are identical.
		objlist = map(lambda x: (short(x[0]), x[1], short(x[2]), short(x[3])), packed)
		# Alternatively, unpack using a list comprehension:
		# objlist = [ ( short(x[0]), x[1], short(x[2]), short(x[3]) ) for x in packed ]
		
		# Create a dictionary from the packed list.  The records hold object id,
		# description, and x and y coordinates, and we want to index by id.
		# We could also create it from the unpacked list, of course.
		objdict = {}
		for x in packed:
			id = short(x[0])
			objdict[id] = {}
			objdict[id]["desc"] = x[1]
			objdict[id]["x"] = short(x[2])
			objdict[id]["y"] = short(x[3])
		
		return objlist, objdict

# STAIDX:
## 768 * 512 * 12 bytes in total, 3 Longs each entry
class TStaidx():
	indexes = None
	def __init__(self, filename = None, mapx = 768, mapy = 512):
		self.mapx = mapx
		self.mapy = mapy
		if filename != None:
			self.indexes = self.read(filename)
		
	def read(self, filename):
		f = open(filename, 'r')
		filecontent = f.read()
		f.close()
		r = re.compile("(....)(....)(....)" , re.DOTALL)
		packed = r.findall(filecontent)
		ret = map(lambda x: (dword(x[0]), dword(x[1]), dword(x[2])), packed)
		return ret
	
	def write(self, filename):
		if self.indexes != None:
			f = open(filename, 'w')
			for i in self.indexes:
				s = pack("LLL", i[0], i[1], i[2])
				f.write(s)
			f.close()
	
	def getStaIdx(self, x, y):
		if self.indexes != None:
			if (x < self.mapx) and (y < self.mapy):
				lookup = x * self.mapx + y
				return self.indexes[lookup]
	
	def getStaIdxStart(self, x, y):
		idx = self.getStaIdx(x,y)
		if idx != None:
			return idx[0]
	
	def getStaIdxLength(self, x, y):
		idx = self.getStaIdx(x,y)
		if idx != None:
			return idx[1]

class TStatics():
	statics = None
	def __init__(self, staidx, stamul, mapx = 768, mapy = 512):
		self.mapx = mapx
		self.mapy = mapy
		if staidx != None:
			self.staidx = TStaidx(staidx, mapx, mapy)
		
	def read(self, filename, realx = None, realy = None):
		if realx == None:
			realx = self.mapx * 8
		if realy == None:
			realy = self.mapy * 8
		f = open(filename, 'r')
		
		f.close()
		
	def readXY(self, filehandler, x, y):
		xblock = int(x / 8)
		yblock = int(y / 8)
		f.seek(xblock * self.mapx + yblock)
		

sta = TStaidx('/home/g4b/Spiele/Alathair/staidx0.mul')
sta.write('/home/g4b/Spiele/Alathair/staidx0.valor')
