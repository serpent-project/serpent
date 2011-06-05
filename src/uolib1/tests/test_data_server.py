# Client code

import xmlrpclib

server = xmlrpclib.Server('http://localhost:8000')
print server.version()
# server.log("hi wie gehts", "huhu", "hahahah")

server.add_object('gab')
server.objects['gab'].test()