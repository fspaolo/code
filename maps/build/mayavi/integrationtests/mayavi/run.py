#!/usr/bin/env python
"""Script to run all the tests.
"""
# Author: Prabhu Ramachandran <prabhu [at] aero . iitb . ac . in>
# Copyright (c) 2008,  Prabhu Ramachandran
# License: BSD Style.

import sys
import os
from os.path import splitext
import glob
from common import test, TestCase

def get_tests():
    """Get all the tests to run.
    """
    files = glob.glob('test_*.py')
    return files

def run_all(tests):
    """Run the given tests.
    """
    args = ' '.join(sys.argv[1:])
    for test in tests:
        cmd = 'python %s %s'%(test, args)
        print cmd
        os.system(cmd)


class RunAllTests(TestCase):
    """Runs all the tests in one go, instead of running each test
    separately.  This speeds up the testing.
    """
    def get_tests(self):
        tests = get_tests()
        tests = [splitext(t)[0] for t in tests]
        klasses = []
        for test in tests:
            # Find test.
            m = __import__(test)
            m.mayavi = self.script
            m.application = self.application
            for name in dir(m):
                klass = getattr(m, name)
                try:
                    if issubclass(klass, TestCase) and klass is not TestCase:
                        mod_name = '%s.%s'%(test, name)
                        klasses.append((mod_name, klass))
                        break
                except TypeError:
                    continue
        return klasses

    def do(self):
        klasses = self.get_tests()
        for name, klass in klasses:
            # Close existing scenes. 
            e = self.script.engine
            for scene in e.scenes:
                e.close_scene(scene)
            print '*'*80
            print name 
            obj = klass()
            obj.set(script=self.script)
            obj.test()


def main():
    argv = ' '.join(sys.argv)

    if '--one-shot' in argv:
        argv = argv.replace('--one-shot', '')
        sys.argv = argv.split()
        t = RunAllTests()
        t.main()
    else:
        tests = get_tests()
        run_all(tests)

if __name__ == "__main__":
    main()

