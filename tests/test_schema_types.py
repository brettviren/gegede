#!/usr/bin/env python
'''
Test gegede.schema.types
'''

import gegede.schema.types as gst

def test_named_typed_list():
    '''
        Volume = (("material", Named), ("shape", Named), 
                  ("placements", NameList(str,0)),
                  ("params", NamedTypedList(str, 0))),
    '''

    s0 = gst.NamedTypedList(str, 0)
    print s0
    print s0([])
