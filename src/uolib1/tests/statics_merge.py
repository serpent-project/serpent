# -*- coding: utf-8 -*-

"""
    Statics Merge.
    (C) by Gabor Guzmics 2009
    
    Since you change the statics maybe in different applications, you might
    want to merge them together into one file.__class__
    
    What this tool does:
        * first off, it looks up, if statics, which are present in its actual
        copy, are still present in the other copies. if not, they are removed.
        
        * second, any new items are added. 
        
        * stadiffs not supported yet.
    
    Mergestrategies:
    Since you might want to define strategies of merging, the merge tool 
    tries to provide as much possible as you may want to have.
    
    BlockCompare: compare the statics in blocks to quickly find changes.
    sometimes blocks with same data are just rearranged. in this case, 
    it might be needed to ask, which version you take over.
    
    Wipe: wipe out a certain area in the original.
    
    Copy: copy over from one of the origins.
    
    
"""

class StaticsMergeTool( object ):
    
    def __init__(self):
        pass
    
    