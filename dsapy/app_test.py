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
from dsapy import dsapy_test

@app.onwrapmain
def a(**kwargs):
    print('a: {!r}'.format(dsapy_test.kw_as_str(kwargs)))
    return kwargs

@app.init
def b(**kwargs):
    print('b: {!r}'.format(dsapy_test.kw_as_str(kwargs)))

@app.onmain
def c(**kwargs):
    print('c: {!r}'.format(dsapy_test.kw_as_str(kwargs)))
    yield kwargs

@app.main(x=42, y=7)
def m(**kwargs):
    print('m: {!r}'.format(dsapy_test.kw_as_str(kwargs)))

app.start(x=43, z=100500)
''')
        out, err = self._run_module('main')
        self.assertEqual('', err)
        self.assertEqual('''a: "{'x': 42, 'y': 7, 'main_func': <function m at 0xADDRESS>, 'parser_kwargs': {}, 'subparser_kwargs': {}}"
b: "{'x': 43, 'z': 100500, 'parser_kwargs': {}, 'subparser_kwargs': {}, 'flags': Namespace(main_func=<function m at 0xADDRESS>), 'main_func': <function m at 0xADDRESS>}"
c: "{'x': 43, 'z': 100500, 'parser_kwargs': {}, 'subparser_kwargs': {}, 'flags': Namespace(main_func=<function m at 0xADDRESS>), 'main_func': <function m at 0xADDRESS>}"
m: "{'x': 43, 'z': 100500, 'parser_kwargs': {}, 'subparser_kwargs': {}, 'flags': Namespace(main_func=<function m at 0xADDRESS>)}"
''', out)

    def test_singlecommand_func_attrs(self):
        self._module('main', '''
from dsapy import app

def main(**kwargs):
    """Test short help.

    Test long description."""
    print('args: {!r}'.format(kwargs))

main.help = 'main.help'
main.description = 'main.description'

app.main(
    name='test',
    help='app.main.help',
    description='app.main.description',
)(main)

app.start(help='start.help', description='start.description')
''')
        out, err = self._run_module('main', '-h')
        self.assertEqual('', err)
        self.assertEqual('''usage: main.py [-h]

start.description

optional arguments:
  -h, --help  show this help message and exit
''', out)

    def test_multicommand_func(self):
        self._module('main', '''
from dsapy import app
import cmdone
import cmdtwo

app.start()
''')

        self._module('cmdone', '''
from dsapy import app

class CmdOne(app.Command):
    """Command one.

    This is full description from docstring."""

    help = 'First command.'  # Overrides default help extracted from docstring.

    def main(self):
        print('cmdone')
''')

        self._module('cmdtwo', '''
from dsapy import app

class CmdTwo(app.Command):
    """Second command.

    This description will be overridden.
    """

    name = 'cmdtwo'

    # Overrides description from docstring
    description = """Command two.

    This description overrides docstring."""

    def main(self):
        print('cmdtwo')
''')

        out, err = self._run_module('main', '-h')
        self.assertEqual('', err)
        self.assertEqual('''usage: main.py [-h] {CmdOne,cmdtwo} ...

optional arguments:
  -h, --help       show this help message and exit

subcommands:
  {CmdOne,cmdtwo}
    CmdOne         First command.
    cmdtwo         Command two.
''', out)

        out, err = self._run_module('main', 'CmdOne', '-h')
        self.assertEqual('', err)
        self.assertEqual('''usage: main.py CmdOne [-h]

Command one.

    This is full description from docstring.

optional arguments:
  -h, --help  show this help message and exit
''', out)

        out, err = self._run_module('main', 'cmdtwo', '-h')
        self.assertEqual('', err)
        self.assertEqual('''usage: main.py cmdtwo [-h]

Command two.

    This description overrides docstring.

optional arguments:
  -h, --help  show this help message and exit
''', out)

        out, err = self._run_module('main', 'CmdOne')
        self.assertEqual('', err)
        self.assertEqual('cmdone\n', out)

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
