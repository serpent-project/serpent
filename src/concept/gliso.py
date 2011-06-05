# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    ISO Perspective rendering test taken from CEDClient.

@author: g4b (python version)
"""

import sys, os
from PySide import QtCore
from PySide import QtGui
from PySide import QtOpenGL
from OpenGL import GLU
from OpenGL.GL import *
from numpy import array
import math, random
import cedclasses
import Image
import logging
import buffers, numpy

def load_textures():
    def load_image(filename, mx, my, master_image):
        im = Image.open(filename)
        im = im.resize((64, 64))
        master_image = master_image.paste(im.copy(), (mx, my, mx + 64, my + 64))
        return master_image

    def get_image(filename):
        im = Image.open(filename)
        im = im.resize((64, 64))
        #master_image.paste(im.copy(), (mx, my, mx + 64, my + 64))
        #mx, my = shift_ms(mx, my)
        return im.size[0], im.size[1], im.tostring('raw', 'RGBA', 0, -1)

    def gen_megatexture(master_image):
        x = 64 * 10
        y = 64 * 10
        mega_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, mega_texture)
        glTexImage2D(
                GL_TEXTURE_2D, 0, 3,
                x, y, 0,
                GL_RGBA, GL_UNSIGNED_BYTE,
                master_image.tostring('raw', 'RGBA', 0, -1)
            )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        return mega_texture

    def gen_textures(imagelist):
        # request a texture id incorrectly
        # request a texture ID        
        textures = glGenTextures(len(imagelist))
        sys.stdout.write('loading textures.')
        for i in xrange(len(imagelist)):
            # make it the current texture ID
            glBindTexture(GL_TEXTURE_2D, textures[i])
            # set the storage format
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            # copy the texture into the current texture ID
            ix, iy, image = imagelist[i]
            glTexImage2D(
                GL_TEXTURE_2D, 0, 3,
                ix, iy, 0,
                GL_RGBA, GL_UNSIGNED_BYTE,
                image
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            sys.stdout.write('.')
        print "done."
        return textures

    def load_images(dirname):
        sys.stdout.write('loading images.')
        mx, my = 0, 0
        master_image = Image.new("RGBA", (640, 640))
        if os.path.exists(dirname):
            for root, dirs, files in os.walk(dirname):
                for file in files:
                    load_image(os.path.join(root, file), mx, my,
                                              master_image)
                    mx += 64
                    if mx > 640:
                        mx = 0
                        my += 64
                    sys.stdout.write('.')
        else:
            print "[directory not found]"
        print "done."
        return master_image
    texture = gen_megatexture(load_images('./tex/'))
    return texture

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.fx = 0 # fx and fy are important for drawing distance.
        self.fy = 0
        self.max_x, self.max_y = 40, 40
        self.landscape = cedclasses.Landscape(1, 1)
        self.landscape.random_cells(self.max_x + 2, self.max_y + 2)
        self.load_landscape()
        self.go_map_x = None
        self.go_map_y = None

        self.offset_x, self.offset_y = 0, 0


    def get_draw_distance(self):
        """ draw distance upon width and height of window """
        # @todo: find out how you get width and height
        width, height = 320, 200
        return math.trunc(
                    math.sqrt(
                        (width * width + height * height) / 44
                        # @research: why 44? 
                              )
                          )

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0, 0))
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.1)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DITHER)
        #glEnable(GL_BLEND) # Enable alpha blending of textures
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (-1, -1, 0.5, 0))
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
        #glEnable(GL_LIGHT1)
        #glLightfv(GL_LIGHT0, GL_POSITION, (-0.5, 1, 0.5, 0))
        self.textures = load_textures()
        self.prepare_buffers()

    def resizeGL(self, width, height):
        if height == 0: height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / float(height)
        GLU.gluOrtho2D(0, width, height, 0);
        #GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def load_landscape(self):
        self.scape = []
        for x in xrange(self.max_x):
            height_scape = []
            for y in xrange(self.max_y):
                normals = self.landscape.get_normals(x, y)
                quads = cedclasses.draw_quads_texture(x, y,
                        self.landscape.get_cell_nwse(x, y),
                        0, 0)
                # @todo: textures.
                data = []
                for j in xrange(4):
                    data.append([normals[j], quads[j]]
                                    )
                height_scape.append(data)
            self.scape.append(height_scape)

    def prepare_buffers(self):

        texcoords = []
        verts = []
        normals = []

        for x in xrange(self.max_x):
            for y in xrange(self.max_y):
                for s in [0, 3, 2, 1]: # vertexes are drawn in this order on the map.
                    verts.append(
                        [self.scape[x][y][s][1][0],
                         self.scape[x][y][s][1][1],
                         ])
                    normals.append(self.scape[x][y][s][0])
                # texture coordinates. all textures are on one big
                # texture and there are 10 of them in each row, 10 rows.
                # so this means 0.0-0.1,0.0-0.1 is the first texture.
                tx, ty = random.randint(0, 2), random.randint(0, 2)
                #tx, ty = 0, 0
                texcoords.append(
                        [[0.1 * tx, 0.1 * ty],
                         [0.1 * tx, 0.1 * (ty + 1)],
                         [0.1 * (tx + 1), 0.1 * (ty + 1)],
                         [0.1 * (tx + 1), 0.1 * ty]]
                                 )
        numpy_verts = numpy.array(verts, numpy.float32)
        self.vbuffer = buffers.VertexBuffer(numpy_verts, GL_DYNAMIC_DRAW)
        numpy_normals = numpy.array(normals, numpy.float32)
        self.nbuffer = buffers.VertexBuffer(numpy_normals, GL_STATIC_DRAW)
        numpy_texcoords = numpy.array(texcoords, numpy.float32)
        self.tbuffer = buffers.VertexBuffer(numpy_texcoords, GL_STATIC_DRAW)
        self.indexes = [ i for i in xrange(4 * self.max_x * self.max_y) ]

    def update_buffer(self):
        glLoadIdentity()
        glTranslate(self.offset_x,
                    self.offset_y,
                    0)
        ## this following would move the whole buffer by offsets.
        ## however, translate does the same job - better.
        #verts = []
        #for x in xrange(self.max_x):
        #    for y in xrange(self.max_y):
        #        for s in [0, 3, 2, 1]:
        #            verts.append([self.scape[x][y][s][1][0] +
        #                self.offset_x,
        #                self.scape[x][y][s][1][1] +
        #                self.offset_y, ])
        #numpy_verts = numpy.array(verts, numpy.float32)
        #self.vbuffer.update_data(numpy_verts, GL_DYNAMIC_DRAW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        self.tbuffer.bind_texcoords(2)

        glEnableClientState(GL_NORMAL_ARRAY)
        self.nbuffer.bind_normals()

        glEnableClientState(GL_VERTEX_ARRAY)
        self.vbuffer.bind_vertexes(2,)

        glDrawElementsui(GL_QUADS, self.indexes)

    def paintGL1(self):
        #
        # I leave this here for archivical purposes.
        # This Andreas Schneiders original code
        # translated from pascal.
        # A little bit played around with it.
        # I immediately started learn VertexArrays
        # researched OpenGL for how to do this FASTER.
        # Well, only option is to create bigger texture files
        # and try to work with models from then on.
        # I now can fully understand why isometric 2d games
        # are very hard to optimize.
        #
        # Plans from now on:
        # - Map objects have to be implemented so they can
        # stream themselves and even generate theyr landscape
        # dynamically.
        # - This would even allow to render in a very fast way,
        # so even a UO client written in python becomes possible.
        def flow_offset_by_draw_distance(draw_distance):
            low_offset_x = -self.fx if (self.fx - draw_distance < 0) \
                                    else - draw_distance
            low_offset_y = -self.fy if (self.fy - draw_distance < 0) \
                                    else - draw_distance
            if self.fy - draw_distance < 0:
                low_offset_y = -self.fy
            else:
                low_offset_y = -draw_distance
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for x in xrange(40):
            for y in xrange(40):
                #normals = self.landscape.get_normals(x, y)
                #quads = cedclasses.draw_quads_texture(x, y,
                #        self.landscape.get_cell_nwse(x, y),
                #        0, 0)
                glBindTexture(GL_TEXTURE_2D, self.textures[
                                                random.randint(0, len(self.textures) - 1)
                                                ])
                glBegin(GL_QUADS)
                glNormal3fv(self.scape[x][y][0][0])
                glTexCoord2i(0, 0)
                if self.offset_x or self.offset_y:
                    s = 0
                    glVertex2iv(
                        [self.scape[x][y][s][1][0] +
                        self.offset_x,
                        self.scape[x][y][s][1][1] +
                        self.offset_y, ]
                    )
                else:
                    glVertex2iv(self.scape[x][y][0][1])
                glNormal3fv(self.scape[x][y][3][0])
                glTexCoord2i(0, 1)
                if self.offset_x or self.offset_y:
                    s = 3
                    glVertex2iv(
                        [self.scape[x][y][s][1][0] +
                        self.offset_x,
                        self.scape[x][y][s][1][1] +
                        self.offset_y, ]
                    )
                else:
                    glVertex2iv(self.scape[x][y][3][1])
                glNormal3fv(self.scape[x][y][2][0])
                glTexCoord2i(1, 1)
                if self.offset_x or self.offset_y:
                    s = 2
                    glVertex2iv(
                        [self.scape[x][y][s][1][0] +
                        self.offset_x,
                        self.scape[x][y][s][1][1] +
                        self.offset_y, ]
                    )
                else:
                    glVertex2iv(self.scape[x][y][2][1])
                glNormal3fv(self.scape[x][y][1][0])
                glTexCoord2i(1, 0)
                if self.offset_x or self.offset_y:
                    s = 1
                    glVertex2iv(
                        [self.scape[x][y][s][1][0] +
                        self.offset_x,
                        self.scape[x][y][s][1][1] +
                        self.offset_y, ]
                    )
                else:
                    glVertex2iv(self.scape[x][y][1][1])
                glEnd()

    def spin(self):
        #self.yRotDeg = (self.yRotDeg + 1) % 360.0
        self.parent.statusBar().showMessage('my ass')
        #self.updateGL()



    def mouseReleaseEvent(self, event, *args, **kwargs):
        x, y, buttons = event.x(), event.y(), event.buttons()
        if buttons == 0:
            if self.go_map_x and self.go_map_y:
                self.offset_x = self.offset_x - (self.go_map_x - x)
                self.offset_y = self.offset_y - (self.go_map_y - y)
                self.go_map_x, self.go_map_y = None, None
                self.update_buffer()
                self.updateGL()
        return super(GLWidget, self).mouseReleaseEvent(event, *args, **kwargs)

    def mousePressEvent(self, event, *args, **kwargs):
        x, y, buttons = event.x(), event.y(), event.buttons()
        if buttons == 2:
            # we register a pressdown of a button
            self.go_map_x = x
            self.go_map_y = y
        return super(GLWidget, self).mousePressEvent(event, *args, **kwargs)


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(800, 600)
        self.setWindowTitle('GL OrthoIso Test')

        self.initActions()
        self.initMenus()

        glWidget = GLWidget(self)
        self.setCentralWidget(glWidget)

        #timer = QtCore.QTimer(self)
        #timer.setInterval(20)
        #QtCore.QObject.connect(timer, QtCore.SIGNAL('timeout()'), glWidget.spin)
        #timer.start()


    def initActions(self):
        self.exitAction = QtGui.QAction('Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), self.close)

    def initMenus(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.exitAction)

    def close(self):
        QtGui.qApp.quit()

app = QtGui.QApplication(sys.argv)

win = MainWindow()
win.show()

sys.exit(app.exec_())
