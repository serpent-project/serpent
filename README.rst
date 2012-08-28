SERPENT PROJECT
===============

The goal is to implement a python scriptset for editing isometric maps

Using the Ultima Online protocol to test against IRIS2, an open source
lugre scripted ogre client for Ultima Online.

The project consists of a lot of legacy code and the arkanlor test server
environment

This Project is in its alpha stages.

Main goals are:
    * Massive Multiplayer Online Map Editing in iso2.5
    
    * Procedural Map generation
    
    * eventually some server emulation

Project Code Description:
    * arkanlor - Server environment written in twisted
    
    * arkanlor.boulder - Gamestate management, designed as Django App
    
    * arkanlor.uos - Ultima Online Server Protocol for twisted
    
    * arkanlor.ced - CentrED Protocol (not started yet) 
    
    * concept - Playground for experimentation with OpenGL rendering
        
    * uolib1 - a library written mainly in python, which I used to manipulate UO data files for bugfixing, restructuring or cleaning up. Also I experimented with how to speed up python to nearly acceptable levels. My first UOLib was written in Pascal from scratch in 2000.  However, if you search a Pascal UO Engine, you might refer to the CentrED repository of Andreas Schneider, or to Alazanes InsideUO. For .net users there is one at RunUO.
    
    * uolib - if I have time to remodel uolib into a more organized format.
    
    * glue - the GL using editor.
