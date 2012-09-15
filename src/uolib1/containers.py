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

class AbstractObject:
	"Abstract to all Objects"
	def __init__(self):
		return None
	def toString(self):
		return "This class is  " + self.__doc__

class ObjectContainer(AbstractObject):
	"An Object Container contains Objects"
	def __init__(self):
		self.data = []
		return None
	def addObject(self, obj):
		"Adds an Object to the Container"
		self.data.append(obj)
	def toString(self):
		ret = ""
		for i in range(len(self.data)):
			ret = ret + str(self.data[i])
		return ret

class ObjectFileContainer(ObjectContainer):
	"An Object Container for parsing Textfiles"
	_isopen = False
	_filename = None
	data = []
	def readFrom(self, fname):
		"reads data into a file"
		# TODO catch expression
		f = open(fname, 'r')
		self._filename = fname
		self.data = f.readlines()
		self._isopen = True
		f.close()
	def saveTo(self, fname):
		"saves data into a file"
		if self.data != None:
			f = open(fname, 'w')
			f.writelines(self.data)
			f.close()
			return True
		return False
	def save(self):
		if _isopen:
			saveTo(self._filename)
	def isOpen(self):
		return self._isopen == True
	def close(self):
		self.data = None
		self._isopen = False

"""
class DBObject(ObjectContainer):
	"A Database Object"
	_keys = []
	_values = []
	_primary = None
	_db = None
	_has_db = False
	def __init__(self):
		return None
	def setDB(self, db):
		if db == DBConnection:
			self._db = db
			self._has_db = True
	def load(self):
		return None
	def save(self):
		return None
	def toString(self):
		return ""

class DBConnection (AbstractObject):
	_db = None
	_un = None
	_pw = None
	_host = "localhost"
	_isconn = False
	_iscursor = False
	_conn = None
	def connect (self):
		pass
	def connected (self):
		return self._isconn == True
	def setDB(self, host = "localhost", db = None, un = None, pw = None):
		self._db = db
		self._un = un
		self._pw = pw
		self._host = host
	def execute(self, what):
		pass
	def getCursor(self):
		pass
	def close(self):
		pass

# TODO export this in own file
import MySQLdb
class MySQLConnection (DBConnection):
	def connect (self):
		self._isconn = MySQLdb.connect (host = self._host, user = self._un, passwd = self._pw, db = self._db)
		return self._isconn
	def execute(self, what):
		if self._isconn:
			cursor = self.getCursor()
			cursor.execute(what)
	def getrow(self):
		if self._iscursor:
			cursor = self._cursor
			return cursor.fetchone()
	def getrows(self):
		if self._iscursor:
			cursor = self._cursor
			return cursor.fetchall()
	def getCursor(self):
		if self._isconn:
			self._iscursor = True
			return self._conn.cursor()
	def close(self):
		if self._iscursor:
			self._cursor.close()
			self._iscursor = False
		if self._isconn:
			self._conn.close()
			self._isconn = False
"""
