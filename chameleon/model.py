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

class Model(object):
    
    def __init__(self, content):
        self.content = content
        self.tables = {}
        self.indexes = {}
        self.sequences = {}
        self.synonyms = []
        self.extra = []
        for c in content:
            if isinstance(c, Table):
                self.tables[c.name] = c
                continue
            if isinstance(c, Index):
                self.indexes[c.name] = c
                continue
            if isinstance(c, Sequence):
                self.sequences[c.name] = c
                continue
            if isinstance(c, Synonym):
                self.synonyms.append(c)
                continue
            self.extra.append(c)


class Object(object):

    def __init__(self, name=None):
        self.name = name
        
    def anonymous(self):
        return self.name is None
        
    def named(self):
        return ( not self.anonymous() )


class Table(Object):

    def __init__(self, name):
        Object.__init__(self, name)
        self._global = False
        self._temporary = False
        self.columns = []
        self.constraints = []
        self.modifiers = []

     
class Column(Object):

    def __init__(self, name):
        Object.__init__(self, name)
        self.table = None
        self.modifiers = []
        
    def references(self):
        for m in self.modifiers:
            if isinstance(m, FkMod):
                yield m

class Default(Object):
    
    def __init__(self, value):
        Object.__init__(self)
        self.value = value


class NotNull(Object):
    
    def __init__(self, name=None):
        Object.__init__(self, name)  

        
class Constraint(Object):

    def __init__(self, name):
        Object.__init__(self, name)


class PK(Constraint):
    def __init__(self, name, columns):
        Constraint.__init__(self, name)
        self.columns = columns
        self.modifiers = []


class PkMod(PK):
    def __init__(self, name=None):
        PK.__init__(self, name, None)

        
class FK(Constraint):
    
    class Cascade: pass
    class Setnull: pass

    class Reference:
        def __init__(self, table, columns):
            self.table = table
            self.columns = columns

    def __init__(self, name):
        Constraint.__init__(self, name)
        self.refA = None
        self.refB = None
        self.ondelete = None


class FkMod(FK):

    def __init__(self, name=None):
        FK.__init__(self, name)
            
        
class CkMod(Constraint):

    def __init__(self, name, expression):
        Constraint.__init__(self, name)
        self.expression = expression
        

class Unique(Constraint):

    def __init__(self, name, columns):
        Constraint.__init__(self, name)
        self.columns = columns
        self.modifiers = []


class UniqueMod(Unique):

    def __init__(self, name=None):
        Unique.__init__(self, name, None)


class Type(Object):

    def __init__(self, name, precision=None):
        Object.__init__(self, name)
        self.precision = precision
        
        
class Index(Object):

    def __init__(self, name, table, columns):
        Object.__init__(self, name)
        self.table = table
        self.columns = columns
        self.unique = False
        self.modifiers = []
        
        
class Tablespace(Object):

    def __init__(self, name):
        Object.__init__(self, name)
        

class TsMod(Tablespace):
    pass


class Logging(Object):
    
    def __init__(self, enabled):
        Object.__init__(self)
        self.enabled = enabled


class Parallel(Object):

    def __init__(self, enabled, n=None):
        Object.__init__(self)
        self.enabled = enabled
        self.n = n
        

class RowMovement(Object):

    def __init__(self, enabled=True):
        Object.__init__(self)
        self.enabled = enabled
        

class OnCommit(Object):

    def __init__(self, preserve=True):
        Object.__init__(self)
        self.preserve = preserve


class Sequence(Object):
    
    class StartWith:
        def __init__(self, n):
            self.start = n
            
    class Order:
        pass
    
    def __init__(self, name):
        Object.__init__(self, name)
        self.modifiers = []


class TableComment(Object):

    def __init__(self, table, text):
        Object.__init__(self)
        self.table = table
        self.text = text[1:-1]


class ColumnComment(TableComment):

    def __init__(self, table, column, text):
        TableComment.__init__(self, table, text)
        self.column = column


class Synonym(Object):

    def __init__(self, synonym, referenced=None):
        Object.__init__(self)
        self.synonym = synonym
        self.referenced = referenced


class Drop(Object):
    
    def __init__(self, t, n):
        Object.__init__(self)
        self.object = self.get(t, n)
    
    class Table(Object):
        pass
    
    class Index(Object):
        pass
   
    class Column(Object):
        pass

    class Constraint(Object):
        pass
    
    class Sequence(Object):
        pass
    
    class Synonym(Object):
        pass
    
    @classmethod
    def get(cls, t, n):
        clsmap = {
            'table' : cls.Table,
            'index' : cls.Index,
            'column' : cls.Column,
            'constraint' : cls.Constraint,
            'sequence' : cls.Sequence,
            'synonym' : cls.Synonym,
        }
        t = t.lower()
        return clsmap.get(t)(n)


class Rename:
    
    def __init__(self, object):
        self.object = object
    
    class Table(Object):
        def __init__(self, name, newname):
            Object.__init__(self, name)
            self.newname = newname
    
    class Column(Object):
        def __init__(self, name, newname):
            Object.__init__(self, name)
            self.newname = newname
            
            
class Modify:
    def __init__(self, columns=()):
        self.columns = columns


class Alter:

    class Table(Object):
        
        def __init__(self, table, adds=(), mods=(), drops=()):
            Object.__init__(self)
            self.table = table
            self.adds = adds
            self.mods = mods
            self.drops = drops
            
        def __len__(self):
            return ( len(self.adds) + len(self.mods) + len(self.drops) )

    class Index(Object):
        
        def __init__(self, index, mods):
            Object.__init__(self)
            self.index = index
            self.mods = mods
        

class Insert(Object):
    
    def __init__(self, table, columns, values):
        Object.__init__(self)
        self.table = table
        self.columns = columns
        self.values = values
        

class Commit(Object):
    pass
        
        
class Function(Object):

    def __init__(self, name, args):
        Object.__init__(self, name)
        self.args = args


class Expression(Object):
    
    def __init__(self, terms):
        Object.__init__(self)
        self.terms = terms

class Include(Object):
    pass