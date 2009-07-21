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

from chameleon import model
from chameleon.plugin import *
from chameleon.orapg import *


class Model(BaseModel):
    
    def __init__(self):
        Plugin.__init__(self, Factory())


class _FK(FK):

    def render(self, fk, n=0):
        s = []
        s.append(FK.render(self, fk, n))
        if self.option('deferrable', False):
            s.append(' DEFERRABLE')
        return self.join(s)

        
class _FkMod(FkMod):

    def render(self, fk, n=0):
        s = []
        s.append(FkMod.render(self, fk, n))
        if self.option('deferrable', False):
            s.append(' DEFERRABLE')
        return self.join(s)


class Type(Plugin):
    
    def xlated(self, t):
        tn = t.name.upper()
        if tn == 'VARCHAR2':
            if t.precision is None:
                return model.Type('TEXT')
            else:
                return model.Type('VARCHAR', t.precision)
        if tn == 'DATE':
            return model.Type('TIMESTAMPTZ')
        if tn == 'BLOB':
            return model.Type('BYTEA')
        if tn == 'NUMBER':
            t = self.pgint(t)
        return t
    
    def pgint(self, t):
        if t.precision is None:
            return model.Type('NUMERIC')
        if t.precision.isdigit():
            if t.precision > 10 and t.precision < 20:
                return model.Type('BIGINT')
            if t.precision > 5 and t.precision < 10:
                return model.Type('INTEGER')
            return model.Type('SMALLINT')
        else:
            f = model.Type('FLOAT')
            f.precision = t.precision.split(',')[1].strip()
            return f

    def render(self, type, n=0):
        t = self.xlated(type)
        s = []
        s.append(t.name.upper())
        if t.precision is not None:
            s.append('(')
            s.append(str(t.precision))
            s.append(')')
        return self.join(s)
    

class Include(Plugin):
        
    def render(self, x, n=0):
        return '\i %s' % x.name


class Factory(OraPgFactory):

    def __init__(self):
        OraPgFactory.__init__(self)
        plugins = {
            model.Type : Type(self),
            model.FkMod : _FkMod(self),
            model.TsMod : EmptyPlugin(self),
            model.FK : _FK(self),
            model.Tablespace : EmptyPlugin(self),
            model.Logging : EmptyPlugin(self),
            model.Parallel : EmptyPlugin(self),
            model.RowMovement : EmptyPlugin(self),
            model.Synonym : EmptyPlugin(self),
            model.Sequence.Order : EmptyPlugin(self),
            model.Include : Include(self),
        }
        self.plugins.update(plugins)
        self.translator = Translator()

    def xlated(self, s):
        if isinstance(s, str):
            s = self.translator.xlated(s)
        return s


class Translator:

    xtab = {
        'SYSDATE' : 'CURRENT_TIMESTAMP',
    }

    def xlated(self, s):
        if self.squoted(s):
            return s
        if self.dquoted(s):
            content = s[1:-1]
            return "'%s'" % content
        if s.endswith('.nextval'):
            return "nextval('%s')" % s[0:s.index('.')]
        return self.xtab.get(s.upper(), s)
    
    def dquoted(self, s):
        return ( s[0] == '"' and s[-1] == '"' )
    
    def squoted(self, s):
        return ( s[0] == "'" and s[-1] == "'" )