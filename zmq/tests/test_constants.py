#-----------------------------------------------------------------------------
#  Copyright (c) 2013 Brian Granger, Min Ragan-Kelley
#
#  This file is part of pyzmq
#
#  Distributed under the terms of the New BSD License.  The full license is in
#  the file COPYING.BSD, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import json
from unittest import TestCase

import zmq

from zmq.utils import constant_names
from zmq.sugar import constants as sugar_constants
from zmq.backend import constants as backend_constants

all_set = set(constant_names.all_names)
#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------

class TestConstants(TestCase):
    
    def _duplicate_test(self, namelist, listname):
        """test that a given list has no duplicates"""
        dupes = {}
        for name in set(namelist):
            cnt = namelist.count(name)
            if cnt > 1:
                dupes[name] = cnt
        if dupes:
            self.fail("The following names occur more than once in %s: %s" % (listname, json.dumps(dupes, indent=2)))
    
    def test_duplicate_all(self):
        return self._duplicate_test(constant_names.all_names, "all_names")
    
    def _change_key(self, change, version):
        """return changed-in key"""
        return "%s-in %d.%d.%d" % tuple([change] + list(version))

    def test_duplicate_changed(self):
        all_changed = []
        for change in ("new", "removed"):
            d = getattr(constant_names, change + "_in")
            for version, namelist in d.items():
                all_changed.extend(namelist)
                self._duplicate_test(namelist, self._change_key(change, version))
        
        self._duplicate_test(all_changed, "all-changed")
    
    def test_changed_in_all(self):
        missing = {}
        for change in ("new", "removed"):
            d = getattr(constant_names, change + "_in")
            for version, namelist in d.items():
                key = self._change_key(change, version)
                for name in namelist:
                    if name not in all_set:
                        if key not in missing:
                            missing[key] = []
                        missing[key].append(name)
        
        if missing:
            self.fail(
                "The following names are missing in `all_names`: %s" % json.dumps(missing, indent=2)
            )
    
    def test_no_negative_constants(self):
        for name in sugar_constants.__all__:
            self.assertNotEqual(getattr(zmq, name), -1)
    
    def test_undefined_constants(self):
        for name in all_set:
            raw = getattr(backend_constants, name)
            if raw == -1:
                self.assertRaises(AttributeError, getattr, zmq, name)
            else:
                self.assertEqual(getattr(zmq, name), raw)
