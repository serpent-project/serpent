SERPENT PROJECT
===============

The goal is to implement a python scriptset for editing isometric maps

Using the Ultima Online protocol to test against free clients like iris2

The project consists of a lot of legacy code and the arkanlor test server
environment

This Project is in its alpha stages.

Arkanlor has an own information page on http://www.weltenfall.net/arkanlor/

Main goals are:
    * Massive Multiplayer Online Map Editing in iso2.5
    
    * Procedural Map generation
    
    * eventually some server emulation

Project Code Description (code located in src/):
    * arkanlor - Server environment written in twisted, later to be redesigned as library.
    
    * arkanlor.boulder - Gamestate management, designed as Django App (maybe alchemy later)
    
    * arkanlor.uos - Ultima Online Server Protocol for twisted
    
    * arkanlor.ced - CentrED Protocol
    
    * concept - Playground for experimentation with OpenGL rendering
        
    * uolib1 - a library written mainly in python, which I used to manipulate UO data files for bugfixing, restructuring or cleaning up. Also I experimented with how to speed up python to nearly acceptable levels. My first UOLib was written in Pascal from scratch in 2000.  However, if you search a Pascal UO Engine, you might refer to the CentrED repository of Andreas Schneider, or to Alazanes InsideUO. For .net users there is one at RunUO.
    
    * uolib - if I have time to remodel uolib into a more organized format.
    
    * glue - the GL using editor. not started yet. probably will fall out.

Other useful resources:
    * arkanlor.dagrm - abstract packet design mechanism.
    
    * arkanlor.dragons - "dragon" like tile interpolation techniques.
         -> dragon: reads dragon scripts
         -> quanum: reads custom quanum scripts
         -> caleb: transfers calebmap scripts to quanum scripts.
    
    * uolib1.scp - abstract parser vor sphere script files. (very old)
    
    * arkanlor.misc.geology - slightly modified geology class from mudpie

Links:
    See credits.txt
