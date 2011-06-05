MAIN CONCEPTS
=============

This document tries to describe all plans as far as I know how to implement
them.

MAP
---

The map currently is drawn by quads. optimizing speed is done by loading 64^2
mapcells into a vertex-buffer-object, adding their normals into a 
normals-buffer-object, and adding the textures into a texture-coord-object.

basicly this means, the map is divided into 64x64 blocks by design.

each map coordinate holds texture and height information.

MapBlock := [ 64*64* [height, texture] ]
MapBlock.vertexes = [ 64*64*4* (x,y) ]
MapBlock.normals = [ 64*64* (x,y,z) ]
MapBlock.textures = [ 64*64* [tx1,ty1,tx2,ty2] ]

However this means, one MapBlock has a certain texture set. if cells have
different textures than the current texture set, the mapblock divides itself
into multiple buffers, holding only the vertexes, normals and texture coords
of the textures not present in the main texture set.

Vertexarrays are drawn with the active texture loaded, which means,
all used textures in a mapblock have to be on as little many texturesets as
possible, so that the optimum is, that one mapblock only needs one vertex
array and one texturechange to occur.

Optimizing Textures
-------------------

It is important to optimize texture loading. If we assume a texture size of
44*44, 20x20 textures can be saved on one megatexture. That gives a 880x880
megatexture containing 400 maptiles.

On graphics cards with higher or lower texture sizes, this has to scale.
we assume, minimal texture size is 1024, however, if it is possible to do it
without big codechanges, scaling down to 256x256 or 512x512 or possibly
scaling up to 2048x2048 textures should be possible.

Additionally, the texture manager should scale itself upon the texture size,
making 64*64 textures possible.

Map Drawing
-----------

Movement can be done with glTranslate, which enables a whole scene to be 
"moved" by x,y,z.
Rotation is not really needed though, but could be done with glTranslate.
Dont forget to load glLoadIdentity - or your offsets will be added indefinitely.

This enables two things:
    1. the map blocks can be drawn next to each other by translating their
    position by 64*zoomsize*texturesize.
    2. the main block shown can be drawn directly continuously by only 
    translating the offset to the active camera position on the block.

Camera Movement
---------------

It would be very nice, if the whole drawing enables you to move the camera
over time (with a global redraw timer). 

Map Unpacking
-------------

The MapBlocks on a certain map are able to "prepare" their arrays to be shown.
ideally, mapblocks around your camera are unpacking themselves, and if prepared
can be rendered directly.

ITEMS
-----

Statics - or any kind of item - displayed at a static location on the map
should also be optimized accordingly.

One idea is to have "rucksack" algorithms in the megatexture-manager, to be
able to optimize maximum texture numbers on one megatexture.

Also, subtextures should be researched to enable animations, or even provide
with other solutions to the texturing problem.

Items should be allowed to be layered, so that statics are contained in one
layer, while dynamic items are in another.
However at drawtime, these layers overlap.

The main difference between an item and a mapcell is, that mapcells always
are drawn BEFORE the items.

LANDSCAPE
---------

Landscape is somewhat foggy for now. Ideally, a Landscape knows how to draw
itself all the time. landscape allows to alter information in its layers.

Landscape.maps = mapblock objects.
Landscape.items = item layers.



