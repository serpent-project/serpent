Concept is the development framework, containing various scripts, stuff and
so on to be able to experiment with all I learned.

TODO
====

:) understand the drawing of the terrain
:) optimizing the model drawing (by using vertex arrays)
:) research how texturing can be done (texturemaps)
:( understand camera, find out how to create dynamic flow.
:( design a map system, which loads / renders data dynamically
:( make the map network transparent (possibly using ced protocol)
:( implement statics and sprites
:( implement a user interface
:( organize landtiles
:( implement a matrix system for edge detection like dragon, implement brushes
:( implement a good movement system with the mouse over the map


BRAINSTORM
==========

EDITOR
------

- User Interface allows direct control of view:
    * display or dont display terrain cells
    * display or dont display statics
    * display or dont display dynamic objects
    
    * edit or dont edit terrain cells
    * edit or dont edit static cells
    * edit or dont edit dynamic objects
    
    * terrain layer - with terrain changing only tools
    * static layer - with static only tools.
    * dynamic layer - with pluggable scripting support for placing mapitems.

- Artlibrary:
    * common abstract library, that loads textures.

- Objectlibrary:
    * common abstract library, that knows about objects
        MapTiles
        MapObjects
        general models.

- Map
    Map has layers of rendered data. 
    - UOMap: primary layer is a quad textureset.
    secondary layer is a statics set.
    additional layers can be defined.
    * can export or import data.
    * can modify cells.

    - network operations can hook updatelayer for global operations
    or write into a change queue.

    