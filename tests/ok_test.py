#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import os
import os.path
import subprocess
import sys
import tempfile
import unittest


class Ctx(object):
    def __init__(self):
        self.tempdir = 'tmp'
        self.root_path = os.path.abspath('../..')
        self.main_module = []
        self.modules = []
        self.current = self.main_module
        self.mod_names = []

    def file_prefix(self):
        return '''
#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import sys
sys.path.append({self.root_path!r})

from dsapy import app
from dsapy import logs
'''.format(self=self)

    def init_ok(self, name):
        self.current.append('''
@app.init
def init{0}(**kwargs):
    logs.info('init {0}')
'''.format(name))
        return self


    def fini_ok(self, name):
        self.current.append('''
@app.fini
def fini{0}(**kwargs):
    logs.info('fini {0}')
'''.format(name))
        return self


    def wrapper_ok(self, name):
        self.current.append('''
@app.onmain
def wrapper{0}(**kwargs):
    logs.info('wrapper {0} start')
    yield kwargs
    logs.info('wrapper {0} end')
'''.format(name))
        return self


    def wrapper_not_iterable(self, name):
        self.current.append('''
@app.onmain
def wrapper{0}(**kwargs):
    logs.info('wrapper {0} start')
    return kwargs
    logs.info('wrapper {0} end')
'''.format(name))
        return self


    def wrapper_no_yield(self, name):
        self.current.append('''
@app.onmain
def wrapper{0}(**kwargs):
    logs.info('wrapper {0} start')
    return kwargs
    yield kwargs
    logs.info('wrapper {0} end')
'''.format(name))
        return self


    def wrapper_many_yields(self, name):
        self.current.append('''
@app.onmain
def wrapper(**kwargs):
    logs.info('wrapper {0} start')
    yield kwargs
    logs.info('wrapper {0} middle')
    yield kwargs
    logs.info('wrapper {0} end')
'''.format(name))
        return self


    def main_func(self):
        return '''
def main(**kwargs):
    logs.info('main')

if __name__ == '__main__':
    app.start(main)
'''

    def module(self):
        self.current = []
        self.modules.append(self.current)
        return self

    def gen_main(self):
        filepath = os.path.join(self.tempdir, 'main.py')
        with open(filepath, 'w+t') as mod:
            print(self.file_prefix(), file=mod)
            for m in self.mod_names:
                print('import {}'.format(module_name(m)), file=mod)
            print(self.main_func(), file=mod)
        return filepath

    def gen_module(self, module):
        mod_file = tempfile.NamedTemporaryFile(prefix='mod', suffix='.py', mode='w+t', dir=self.tempdir, delete=False)
        with mod_file as mod:
            self.mod_names.append(mod_file.name)
            print(self.file_prefix(), file=mod)
            for section in module:
                print(section, file=mod)
        return mod_file.name

    def generate(self):
        mods = [
            self.gen_module(m)
            for m in self.modules
        ]
        return self.gen_main()

    def run(self):
        main_path = self.generate()
        p = subprocess.run(['python3', main_path, '--log-level=info'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return p.stdout, p.stderr


def strip_prefix(prefix, s):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def strip_suffix(suffix, s):
    if s.endswith(suffix):
        return s[:len(s)-len(suffix)]
    return s


def module_name(module_path):
    return strip_suffix('.py', os.path.basename(module_path))


class TestDsapyApp(unittest.TestCase):
    def test_simple_ok(self):
        out, err = (
            Ctx()
            .module()
            .init_ok('1')
            .module()
            .init_ok('2')
            .module()
            .fini_ok('1')
            .module()
            .fini_ok('2')
            .module()
            .wrapper_ok('1')
            .module()
            .wrapper_ok('2')
            .run()
        )
        self.assertEqual(out, '')
        self.assertEqual(err, 'wrapper 1 start\nwrapper 2 start\ninit 1\ninit 2\nmain\nfini 2\nfini 1\nwrapper 2 end\nwrapper 1 end\n')


if __name__ == '__main__':
    unittest.main()
