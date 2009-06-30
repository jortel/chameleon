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


class Tablespace(Plugin):

    def render(self, t, n=0):
        s = []
        s.append('\n')
        s.append(indent(n))
        s.append('TABLESPACE ')
        s.append(t.name)
        return self.join(s)

    
class TsMod(Plugin):

    def render(self, t, n=0):
        s = []
        s.append('\n')
        s.append(indent(n))
        s.append('USING INDEX TABLESPACE ')
        s.append(t.name)
        return self.join(s)


class Logging(Plugin):

    def render(self, lg, n=0):
        s = []
        s.append('\n')
        s.append(indent(n))
        if lg.enabled:
            s.append('LOGGING')
        else:
            s.append('NOLOGGING')
        return self.join(s)


class Parallel(Plugin):

    def render(self, p, n=0):
        s = []
        s.append('\n')
        s.append(indent(n))
        if p.enabled:
            s.append('PARALLEL')
            if p.n is not None:
                s.append(' ')
                s.append(p.n)
        else:
            s.append('NOPARALLEL')
        return self.join(s)
    
    
class RowMovement(Plugin):
    
    def render(self, r, n=0):
        s = []
        s.append('\n')
        s.append(indent(n))
        s.append('ENABLE ROW MOVEMENT')
        return self.join(s)


class Type(Plugin):
    
    tab = {
        'NUMERIC' : lambda t : model.Type('NUMBER', t.precision),
        'SMALLINT': lambda t : model.Type('NUMBER', 5),
        'INTEGER' : lambda t : model.Type('NUMBER', 10),
        'BIGINT'  : lambda t : model.Type('NUMBER', 19),
        'VARCHAR' : lambda t : model.Type('VARCHAR2', t.precision),
        'BYTEA'   : lambda t : model.Type('BLOB'),
    }
    
    def xlated(self, t):
        fn = self.tab.get(t.name.upper())
        if fn is None:
            return t
        else:
            return fn(t)

    def render(self, type, n=0):
        t = self.xlated(type)
        s = []
        s.append(t.name.upper())
        if t.precision is not None:
            s.append('(')
            s.append(str(t.precision))
            s.append(')')
        return self.join(s)


class Synonym(Plugin):
        
    def render(self, syn, n=0):
        s = []
        s.append('CREATE SYNONYM ')
        s.append(syn.synonym)
        if syn.referenced is not None:
            s.append(' FOR ')
            s.append(syn.referenced)
        s.append(';')
        return self.join(s)


class _Function(Function):
        
    def render(self, f, n=0):
        if f.name.upper() == 'NEXTVAL' and len(f.args):
            return '%s.%s' % (f.args[0], f.name)
        return Function.render(self, f, n)
    
    
class Include(Plugin):
        
    def render(self, x, n=0):
        return '@%s' % x.name


class Factory(OraPgFactory):
    
    def __init__(self):  
        OraPgFactory.__init__(self)
        plugins = {
            model.Function : _Function(self),
            model.Synonym : Synonym(self),
            model.Type : Type(self),
            model.TsMod : TsMod(self),
            model.Tablespace : Tablespace(self),
            model.Logging : Logging(self),
            model.Parallel : Parallel(self),
            model.RowMovement : RowMovement(self),
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
        'CURRENT_TIMESTAMP' : 'SYSDATE',
        'CURRENT_DATE' : 'SYSDATE',
    }

    def xlated(self, s):
        if self.squoted(s):
            return s
        if self.dquoted(s):
            content = s[1:-1]
            return "'%s'" % content
        return self.xtab.get(s.upper(), s)
    
    def dquoted(self, s):
        return ( s[0] == '"' and s[-1] == '"' )
    
    def squoted(self, s):
        return ( s[0] == "'" and s[-1] == "'" )
