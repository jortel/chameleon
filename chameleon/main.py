# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from chameleon.parser import parse
from chameleon.model import Model
from chameleon.optimizer import *
from getopt import getopt, GetoptError
from datetime import datetime as dt
import traceback as tb
import sys
import os

sys.path.append('.')

options = {}

optimizers = {
    'none' : Optimizer(options),
    'basic' : Basic(options),
    'best' : BestPractices(options),
}

verbose = ( lambda : options.get('verbose', False) )
output = None


def main(argv):
    output = None
    style = 'oracle'
    optimizer = optimizers.get('none')              
    flags = 'vhfDSo:s:H:O:'
    keywords = [
        'help',
        'verbose',
        'output=',
        'style=',
        'header=',
        'optimizer=',
        'fast',
        'deferrable',
        'sort',
    ]
    try:                   
        opts, args = getopt(argv, flags, keywords)
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
                sys.exit(0)
            if opt in ('-v', '--verbose'):
                options['verbose'] = True
                continue
            if opt in ('-o', '--output'):
                output = arg
                continue
            if opt in ('-s', '--style'):
                if style in ('oracle', 'postgres'):
                    style = arg
                else:
                    raise GetoptError('style "%s, not-valid' % arg)
                continue
            if opt in ('-f', '--fast'):
                options['fast'] = 1
                continue
            if opt in ('-S', '--sort'):
                options['sort'] = True
                continue
            if opt in ('-O', '--optimizer'):
                optimizer = optimizers.get(arg)
                if optimizer is None:
                    raise GetoptError('optimizer "%s", not-valid' % arg)
                continue
            if opt in ('-H', '--header'):
                f = open(arg)
                options['header'] = f.read()
                f.close()
                continue
            if opt in ('-D', '--deferrable'):
                options['deferrable'] = True
                continue
        options['optimizer'] = optimizer
        processfiles(style, output, args)
    except GetoptError, e:
        print e
        usage()
        sys.exit(2)
        
def processfiles(style, output, files):
        plugin = getplugin(style)
        plugin.factory.options = options
        failed = []
        if output is None:
            data, fp = process(plugin, files)
            failed += fp
            print data
        else:
            if os.path.isdir(output):
                for fn in files:
                    data, fp = process(plugin, (fn,))
                    failed += fp
                    if len(fp):
                        continue
                    ofn = os.path.join(output, os.path.basename(fn))
                    if verbose():
                        print 'writing:\n\t%s\nto:\n\t%s' % (fn, ofn)
                    f = open(ofn, 'w')
                    f.write(data)
                    f.close()
            else:
                for fn in files:
                    data, fp = process(plugin, files)
                    failed += fp
                    if verbose():
                        print 'writing:\n\t%s\nto:\n\t%s' % (fn, output)
                    f = open(output, 'w')
                    f.write(data)
                    f.close()
        errno = len(failed)
        processed = len(files)
        optimizer = options.get('optimizer')
        s = []
        s.append('(succeeded: %d' % (processed-errno))
        s.append('failed: %d' % errno)
        s.append('warnings: %d)' % len(optimizer.warnings))
        print ', '.join(s)
        if verbose():
            print optimizer.report()
        if errno:
            for fd in failed:
                print '  %s\n    (%s)' % fd
        sys.exit(errno)    
       
def getplugin(style):
    if style == 'oracle':
        from chameleon.oracle import Model as Oracle
        return Oracle()
    if style == 'postgres':
        from chameleon.postgres import Model as Postgres
        return Postgres()
    raise GetoptError('output style "%s" not supported' % style)
        
def process(plugin, files):
    data = []
    failed = []
    header = options.get('header', '')
    fast = options.get('fast', 0)
    optimizer = options.get('optimizer')
    for fn in files:
        try:
            f = open(fn)
            script = parse(f.read(), fast)
            model = Model(script)
            model = optimizer.process(model)
            rendered = plugin.render(model)
            data.append(header)
            data.append('\n')
            data.append(rendered)
            data.append('\n')
        except Exception, e:
            tb.print_exc()
            failed.append((fn, e))
    data = '\n'.join(data)
    return (data, failed)

   
def usage():
    s = []
    s.append('Usage chameleon: [OPTION]... [INPUT]')
    s.append(' Options:')
    s.append('  -h, --help')
    s.append('      Show usage information.')
    s.append('  -v, --verbose')
    s.append('      Shows processing information, warnings and summary.')
    s.append('  -o, --output')
    s.append('      The output (file|directory).')
    s.append('  -s, --style')
    s.append('      The output style (oracle|postres ).')
    s.append('        Default: oracle.')
    s.append('  -f, --fast')
    s.append('      The (fast) flag')
    s.append('  -O, --optimizer')
    s.append('      The syntax optimizer to be used (none|basic|best).')
    s.append('  -H, --header')
    s.append('      The path to header file to prepend.')
    s.append('  Postgres Specific:')
    s.append('  -D, --deferrable')
    s.append('      Makes postgres FK constraints DEFERRABLE.')
    print('\n'.join(s))  

if __name__ == '__main__':
    main(sys.argv[1:])
