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


class Table(Plugin):
    
    def margin(self, table, n):
        m = 0
        for c in table.columns:
            w = len(c.name)
            if m < w: m = w
        m += n
        return ( m + 2 )

    def render(self, table, n=0):
        s = []
        m = self.margin(table, n)
        s.append('CREATE ')
        if table._global:
            s.append('GLOBAL ')
        if table._temporary:
            s.append('TEMPORARY ')
        s.append('TABLE ')
        s.append(table.name)
        s.append('\n(')
        for c in table.columns:
            p = self.plugin(c)
            s.append('\n')
            s.append(p.render(c, n+TAB, m))
            s.append(',')
        s.pop()
        for m in table.constraints:
            p = self.plugin(m)
            s.append(',')
            s.append('\n')
            s.append(p.render(m, n+TAB))
        s.append('\n)')
        for m in table.modifiers:
            p = self.plugin(m)
            s.append(p.render(m))
        s.append('\n;')
        return self.join(s)

     
class Column(Plugin):

    def render(self, column, n=0, n2=0):
        s = []
        s.append(indent(n))
        s.append(column.name)
        L = len(column.name)
        N = n2-L
        s.append(indent(N))
        for m in self.factory.sorted(column.modifiers):
            p = self.plugin(m)
            s.append(p.render(m, n))
            s.append(' ')
            if n2:
                n += n2
                n2 = 0
        s.pop()
        return self.join(s)


class Index(Plugin):
        
    def render(self, index, n=0):
        s = []
        s.append('CREATE ')
        if index.unique:
            s.append('UNIQUE ')
        s.append('INDEX ')
        s.append(index.name)
        s.append('\n')
        s.append(indent(n+TAB))
        s.append('ON ')
        s.append(index.table)
        s.append(' (')
        for c in index.columns:
            s.append(c)
            s.append(', ')
        s.pop()
        s.append(')')
        for m in index.modifiers:
            p = self.plugin(m)
            s.append(p.render(m, n+TAB))
        s.append(';')
        return self.join(s)
    
class PK(Plugin):

    def render(self, pk, n=0):
        s = []
        s.append(indent(n))
        s.append('CONSTRAINT ')
        s.append(pk.name)
        s.append(' PRIMARY KEY')
        s.append(' (')
        for c in pk.columns:
            s.append(c)
            s.append(', ')
        s.pop()
        s.append(')')
        for m in pk.modifiers:
            s.append(' ')
            p = self.plugin(m)
            s.append(p.render(m, n+TAB))
        return self.join(s)
    

class PkMod(PK):
    
    def render(self, pk, n=0):
        s = []
        if pk.named():
            s.append('\n')
            s.append(indent(n+TAB))
            s.append('CONSTRAINT ')
            s.append(pk.name)
            s.append(' ')
        s.append('PRIMARY KEY')
        for m in pk.modifiers:
            p = self.plugin(m)
            s.append(p.render(m, n+TAB))
        return self.join(s)
    
    
class Unique(Plugin):

    def render(self, u, n=0):
        s = []
        s.append(indent(n))
        s.append('CONSTRAINT ')
        s.append(u.name)
        s.append(' UNIQUE')
        s.append(' (')
        for c in u.columns:
            s.append(c)
            s.append(', ')
        s.pop()
        s.append(')')
        for m in u.modifiers:
            s.append(' ')
            p = self.plugin(m)
            s.append(p.render(m, n+TAB))
        return self.join(s)

    
class UniqueMod(Plugin):
    
    def render(self, u, n=0):
        s = []
        if u.named():
            s.append('\n')
            s.append(indent(n+TAB))
            s.append('CONSTRAINT ')
            s.append(u.name)
            s.append(' ')
        s.append('UNIQUE')
        for m in u.modifiers:
            p = self.plugin(m)
            s.append(p.render(m, n+TAB))
        return self.join(s)


class FK(Plugin):
    
    class Cascade(Plugin):
        def render(self, d, n=0):
            s = []
            s.append('\n')
            s.append(indent(n+TAB))
            s.append('ON DELETE CASCADE')
            return self.join(s)
    class Setnull(Plugin):
        def render(self, d, n=0):
            s = []
            s.append('\n')
            s.append(indent(n+TAB))
            s.append('ON DELETE SET NULL')
            return self.join(s)

    def render(self, fk, n=0):
        s = []
        s.append(indent(n))
        s.append('CONSTRAINT ')
        s.append(fk.name)
        s.append(' FOREIGN KEY')
        s.append(' (')
        for c in fk.refA.columns:
            s.append(c)
            s.append(', ')
        s.pop()
        s.append(')\n')
        s.append(indent(n+TAB))
        s.append('REFERENCES ')
        s.append(fk.refB.table)
        s.append(' (')
        for c in fk.refB.columns:
            s.append(c)
            s.append(', ')
        s.pop()
        s.append(')')
        if fk.ondelete is not None:
            p = self.plugin(fk.ondelete)
            s.append(' ')
            s.append(p.render(fk.ondelete, n+TAB))
        return self.join(s)

        
class FkMod(FK):

    def render(self, fk, n=0):
        s = []
        s.append('\n')
        s.append(indent(n+TAB))
        if fk.named():
            s.append('CONSTRAINT ')
            s.append(fk.name)
            s.append('\n')
            s.append(indent(n+TAB+TAB))
        s.append('REFERENCES ')
        s.append(fk.refB.table)
        s.append(' (')
        for c in fk.refB.columns:
            s.append(c)
            s.append(', ')
        s.pop()
        s.append(')')
        if fk.ondelete is not None:
            p = self.plugin(fk.ondelete)
            s.append(' ')
            s.append(p.render(fk.ondelete, n+TAB))
        return self.join(s)


class CkMod(Plugin):
    
    def render(self, ck, n=0):
        s = []
        s.append('\n')
        s.append(indent(n+TAB))
        if ck.named():
            s.append('CONSTRAINT ')
            s.append(ck.name)
            s.append('\n')
            s.append(indent(n+(TAB*2)))
        s.append('CHECK (')
        ex = ck.expression
        p = self.plugin(ex)
        s.append(p.render(ex, n))
        s.append(')')
        return self.join(s)


class Default(Plugin):

    def render(self, d, n=0):
        s = []
        v = self.xlated(d.value)
        s.append('\n')
        s.append(indent(n+TAB))
        s.append('DEFAULT (')
        if isinstance(v, str):
            s.append(self.xlated(v))
        else:
            p = self.plugin(v)
            s.append(p.render(v, n))
        s.append(')')
        return self.join(s)
    
class NotNull(Plugin):

    def render(self, x, n=0):
        return 'NOT NULL'
    
class OnCommit(Plugin):
    
    def render(self, c, n=0):
        s = []
        s.append('\n')
        s.append(indent(n))
        s.append('ON COMMIT ')
        if c.preserve:
            s.append('PRESERVE ')
        else:
            s.append('DELETE ')
        s.append('ROWS')
        return self.join(s)
    
class Sequence(Plugin):
    
    class StartWith(Plugin):      
        def render(self, m, n=0):
            return ' START WITH %s' % m.start
        
    class Order(Plugin):      
        def render(self, m, n=0):
            return ' ORDER'
        
        
    def render(self, seq, n=0):
        s = []
        s.append('CREATE SEQUENCE ')
        s.append(seq.name)
        for m in seq.modifiers:
            p = self.plugin(m)
            s.append('%s' % p.render(m, n))
        s.append(';')
        return self.join(s)
    
    
class TableComment(Plugin):
        
    def render(self, tc, n=0):
        s = []
        s.append('COMMENT ON TABLE ')
        s.append(tc.table)
        s.append(' IS ')
        s.append("'%s'" % tc.text)
        s.append(';')
        return self.join(s)


class ColumnComment(Plugin):
        
    def render(self, tc, n=0):
        s = []
        s.append('COMMENT ON COLUMN ')
        s.append('%s.%s' % (tc.table, tc.column))
        s.append(' IS ')
        s.append("'%s'" % tc.text)
        s.append(';')
        return self.join(s)

   
class Drop(Plugin):
    
    def render(self, d):
        s = []
        s.append('DROP ')
        p = self.plugin(d.object)
        s.append(p.render(d.object))
        return self.join(s)
    
    class Table(Plugin):
        def render(self, d):
            return 'TABLE %s;' % d.name

    class Index(Plugin):
        def render(self, d):
            return 'INDEX %s;' % d.name
        
    class Column(Plugin):
        def render(self, d):
            return 'COLUMN %s' % d.name
        
    class Constraint(Plugin):
        def render(self, d):
            return 'CONSTRAINT %s' % d.name
        
    class Sequence(Plugin):
        def render(self, d):
            return 'SEQUENCE %s;' % d.name
        
    class Synonym(Plugin):
        def render(self, d):
            return 'SYNONYM %s;' % d.name
        
        
class Rename(Plugin):
    
    class Table(Plugin):
        def render(self, t, n=0):
            return 'TO %s' % t.newname
    
    class Column(Plugin):
        def render(self, c, n=0):
            return 'COLUMN %s TO %s' % (c.name, c.newname)
    
    def render(self, r, n=0):
        s = []
        s.append(' RENAME ')
        p = self.plugin(r.object)
        s.append(p.render(r.object))
        return self.join(s)


class Modify(Plugin):
    
    def margin(self, t, n):
        m = 0
        for c in t.columns:
            w = len(c.name)
            if m < w: m = w
        m += n
        return ( m + 2 )

    def render(self, mod, n=0):
        s = []
        m = self.margin(mod, n)
        s.append('\nMODIFY\n')
        s.append('(')
        for c in mod.columns:
            s.append('\n')
            p = self.plugin(c)
            s.append(p.render(c, n, m))
            s.append(',')
        s.pop()
        s.append('\n)')
        return self.join(s)


class Alter:

    class Table(Plugin):
            
        def render(self, alter, n=0):
            s = []
            s.append('ALTER TABLE ')
            s.append(alter.table)
            for a in alter.adds:
                s.append('\n')
                s.append(indent(n+TAB))
                s.append('ADD ')
                p = self.plugin(a)
                s.append(p.render(a))
                s.append(',')
            if len(alter.adds):
                s.pop()
            for m in alter.mods:
                p = self.plugin(m)
                s.append(p.render(m, n+TAB))
            for d in alter.drops:
                s.append('\n')
                s.append(indent(n+TAB))
                p = self.plugin(d)
                s.append(p.render(d))
            s.append(';')
            return self.join(s)

    class Index(Plugin):
            
        def render(self, alt, n=0):
            s = []
            s.append('ALTER INDEX ')
            s.append(alt.index)
            for m in alt.mods:
                p = self.plugin(m)
                s.append(p.render(m, n+TAB))
            s.append(';')
            return self.join(s)
    
    
class Insert(Plugin):
        
    def render(self, i, n=0):
        s = []
        s.append('INSERT INTO ')
        s.append(i.table)
        if len(i.columns):
            s.append('\n')
            s.append(indent(n+TAB))
            s.append('(')
            for c in i.columns:
                s.append(c)
                s.append(', ')
            s.pop()
            s.append(')')
        s.append('\nVALUES')
        s.append('\n')
        s.append(indent(n+TAB))
        s.append('(')
        for v in i.values:
            if isinstance(v, str):
                s.append(self.xlated(v))
            else:
                p = self.plugin(v)
                s.append(p.render(v, n))
            s.append(', ')
        s.pop()
        s.append(')')
        s.append(';')
        return self.join(s)
    

class Commit(Plugin):
        
    def render(self, c, n=0):
        return 'COMMIT;'
    

class Function(Plugin):
        
    def render(self, f, n=0):
        s = []
        s.append(f.name)
        s.append('(')
        for a in f.args:
            v = self.xlated(a)
            s.append(v)
            s.append(', ')
        if len(f.args):
            s.pop()
        s.append(')')
        return self.join(s)
    
    
class Expression(Plugin):
        
    def render(self, x, n=0):
        s = []
        for t in x.terms:
            if isinstance(t, str):
                s.append(self.xlated(t))
            else:
                p = self.plugin(t)
                s.append(p.render(t, n))
        return ' '.join(s)


class OraPgFactory(PluginFactory):

    order = [
        model.Drop,
        model.Table,
        model.Column,
        model.Type,
        model.Default,
        model.NotNull,
        model.PkMod,
        model.TsMod,
        model.UniqueMod,
        model.FkMod,
        model.CkMod,
        model.PK,
        model.FK,
        model.Unique,
        model.TableComment,
        model.ColumnComment,
        model.Synonym,
        model.Index,
        model.Sequence,
        model.Alter.Table,
        model.Alter.Index,
        model.Insert,
        model.Commit,
        model.Rename,
        model.Include,
    ]

    
    def __init__(self):  
        PluginFactory.__init__(self)
        self.ordering = self.order
        self.plugins = {
            model.Expression : Expression(self),
            model.Table : Table(self),
            model.TableComment : TableComment(self),
            model.ColumnComment : ColumnComment(self),
            model.Column : Column(self),
            model.Index : Index(self),
            model.Sequence : Sequence(self),
            model.Sequence.StartWith : Sequence.StartWith(self),
            model.Sequence.Order : Sequence.Order(self),
            model.NotNull : NotNull(self),
            model.Default : Default(self),
            model.PK : PK(self),
            model.PkMod : PkMod(self),
            model.FkMod : FkMod(self),
            model.FkMod.Cascade : FkMod.Cascade(self),
            model.FkMod.Setnull : FkMod.Setnull(self),
            model.FK : FK(self),
            model.FK.Cascade : FK.Cascade(self),
            model.FK.Setnull : FK.Setnull(self),
            model.CkMod : CkMod(self),
            model.Unique : Unique(self),
            model.UniqueMod : UniqueMod(self),
            model.OnCommit : OnCommit(self),
            model.Alter.Table : Alter.Table(self),
            model.Drop : Drop(self),
            model.Drop.Table : Drop.Table(self),
            model.Drop.Index : Drop.Index(self),
            model.Drop.Column : Drop.Column(self),
            model.Drop.Constraint : Drop.Constraint(self),
            model.Drop.Sequence : Drop.Sequence(self),
            model.Drop.Synonym : Drop.Synonym(self),
            model.Alter.Index : Alter.Index(self),
            model.Rename : Rename(self),
            model.Rename.Table : Rename.Table(self),
            model.Rename.Column : Rename.Column(self),
            model.Modify : Modify(self),
            model.Insert : Insert(self),
            model.Commit : Commit(self),
            model.Function : Function(self),
        }