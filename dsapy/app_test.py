#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import contextlib
import os
import os.path
import shutil
import subprocess
import sys
import tempfile
import unittest


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.tempdir = tempfile.mkdtemp()
        os.symlink(os.path.abspath('.'), os.path.join(self.tempdir, 'dsapy'))

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_simple_main(self):
        self._module('main', '''
from dsapy import app
@app.main()
def testmain(**kwargs):
    print('Ok')
app.start()
''')
        out, err = self._run_module('main')
        self.assertEqual('', err)
        self.assertEqual('Ok\n', out)

    def test_wrappers_order(self):
        self._module('main', '''
from dsapy import app

@app.onmain
def a(**kwargs):
    print('a begin')
    yield kwargs
    print('a end')

@app.init
def c(**kwargs):
    print('c')

@app.onmain
def b(**kwargs):
    print('b begin')
    yield kwargs
    print('b end')

@app.init
def d(**kwargs):
    print('d')

@app.onwrapmain
def e(**kwargs):
    print('e')
    return kwargs

@app.main()
def m(**kwargs):
    print('m')

app.start()
''')
        out, err = self._run_module('main')
        self.assertEqual('', err)
        self.assertEqual('''e
c
d
a begin
b begin
m
b end
a end
''', out)

    def test_wrappers_args(self):
        self._module('main', '''
from dsapy import app

def kwstr(kwargs):
    kw = kwargs.copy()
    if 'main_func' in kw:
        kw['main_func'] = kw['main_func'].__name__
    if 'flags' in kw:
        f = kw['flags']
        if hasattr(f, 'main_func') and hasattr(f.main_func, '__name__'):
            f.main_func = f.main_func.__name__
    return kw

@app.onwrapmain
def a(**kwargs):
    print('a: {!r}'.format(kwstr(kwargs)))
    return kwargs

@app.init
def b(**kwargs):
    print('b: {!r}'.format(kwstr(kwargs)))

@app.onmain
def c(**kwargs):
    print('c: {!r}'.format(kwstr(kwargs)))
    yield kwargs

@app.main(x=42, y=7)
def m(**kwargs):
    print('m: {!r}'.format(kwstr(kwargs)))

app.start(x=43, z=100500)
''')
        out, err = self._run_module('main')
        self.assertEqual('', err)
        self.assertEqual('''a: {'x': 42, 'y': 7, 'main_func': 'm'}
b: {'x': 43, 'z': 100500, 'flags': Namespace(main_func='m'), 'main_func': 'm'}
c: {'x': 43, 'z': 100500, 'flags': Namespace(main_func='m'), 'main_func': 'm'}
m: {'x': 43, 'z': 100500, 'flags': Namespace(main_func='m')}
''', out)

    def _mpath(self, name):
        return os.path.join(self.tempdir, name + '.py')

    def _module(self, name, content):
        with open(self._mpath(name), 'w+') as m:
            m.write(content)

    def _run_module(self, name, *args):
        env = os.environ.copy()
        env['PYTHONPATH'] = self.tempdir
        p = subprocess.run(
            ['python3', self._mpath(name)] + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
        )
        return p.stdout, p.stderr


if __name__ == '__main__':
    unittest.main()
