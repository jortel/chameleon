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

from chameleon.model import *


class Optimizer:
    
    def __init__(self, options):
        self.options = options
        self.warningtypes = []
        self.warnings = []
        
    def process(self, model):
        return model
    
    def verbose(self):
        return self.options.get('verbose', False)
        
    def findwarning(self, id):
        for w in self.warningtypes:
            if id == w[0]:
                return w
        return None
        
    def warning(self, wid, *args):
        w = self.findwarning(wid)
        self.warnings.append((wid, args))
        if self.verbose():
            print w[2] % args

    def report(self, short=True):     
        d = {}
        for w in self.warnings:
            wlist = d.get(w[0])
            if wlist is None:
                wlist = []
                d[w[0]] = wlist
            wlist.append(w)
        s = []
        for k,v in d.items():
            w = self.findwarning(k)
            summary = w[1]
            count = len(v)
            s.append('%*s: %s' % (4, count, summary))
        return '\n'.join(s)
        

class Basic(Optimizer):
    
    BasicWarnings = [
    (1, 'Alter Table (promoted)',
    """
    Warning: ALTER TABLE "%s" has been optimized into the
             "CREATE TABLE" declaration.
    """),
    (2, 'Alter Index (promoted)',
    """
    Warning: ALTER INDEX "%s" has been optimized into the
             "CREATE INDEX" declaration.
    """),
    ]
        
    def __init__(self, options):
        Optimizer.__init__(self, options)
        self.warningtypes += self.BasicWarnings

    def process(self, model):
        for ex in model.extra:
            if isinstance(ex, Alter.Table):
                table = model.tables.get(ex.table)
                if table is None: 
                    continue
                self.warning(1, table.name)
                unused = []
                for a in ex.adds:
                    table.constraints.append(a)
                    unused.append(a)
                ex.adds = list(ex.adds)
                for a in unused:
                    ex.adds.remove(a)
                unused = []
                for m in ex.mods:
                    if isinstance(m, (Rename, Modify)):
                        continue
                    table.modifiers.append(m)
                    unused.append(m)
                ex.mods = list(ex.mods)
                for m in unused:
                    ex.mods.remove(m)
                if not len(ex):
                    model.content.remove(ex)
            if isinstance(ex, Alter.Index):
                index = model.indexes.get(ex.index)
                if index is None: 
                    continue
                self.warning(2, index.name)
                for m in ex.mods:
                    index.modifiers.append(m)
                model.content.remove(ex)               
        return model
                
                
class BestPractices(Basic):
    
    BestWarnings = [
    (10, 'Anonymous constraint (name needed)',
    """
    Warning: Anonymous (%s) constraint on "%s.%s" has been named.
    """),
    (20, 'Named (not null) constraint (should be anonymous)',
    """
    Warning: The named (not null) constraint "%s" on "%s.%s" has been made anonymous.
    """),
    (30, 'Redundant (not null) w/ (primary key)',
    """
    Warning: The (not null) constraint on "%s.%s" has been removed 
             because it redundant with the (primary key).
    """),
    (31, 'Redundant (unique) w/ (primary key)',
    """
    Warning: The (unique) constraint "%s" on "%s.%s" has been removed 
             because it redundant with the (primary key).
    """),
    (40, 'Table constraint (promoted)',
    """
    Warning: The (%s) table constraint "%s" on "%s" has 
    been promoted to the "%s" column.
    """),
    (50, 'Index reduntant w/ (pk,unique) constraint, removed',
    """
    Warning: Index (%s) is reduntant with constraint "%s" on "%s", removed.
    """),
    ]
    
    def __init__(self, options):
        Basic.__init__(self, options)
        self.warningtypes += self.BestWarnings

    def process(self, model):
        model = Basic.process(self, model)
        self.fixtables(model)
        self.fixindexes(model)
        return model
    
    def fixcolumn(self, c):
        self.redundant(c)
        self.anonymous(c)
        self.named(c)
    
    def anonymous(self, c):
        for m in c.modifiers:
            if isinstance(m, FkMod):
                if m.anonymous():
                    self.warning(10, 'fk', c.table.name, c.name)
                    m.name = '%s_fk' % c.name
                continue
            if isinstance(m, CkMod):
                if m.anonymous():
                    self.warning(10, 'check', c.table.name, c.name)
                    m.name = '%s_ck' % c.name
                continue
            if isinstance(m, UniqueMod):
                if m.anonymous():
                    self.warning(10, 'unique', c.table.name, c.name)
                    m.name = '%s_uq' % c.name
                continue
            
    def named(self, c):
        for m in c.modifiers:
            if isinstance(m, NotNull):
                if m.named():
                    self.warning(20, m.name, c.table.name, c.name)
                    m.name = None
                continue
    
    def redundant(self, c):
        pk = []
        for m in c.modifiers:
            if isinstance(m, PkMod):
                pk.append(c)
        unused = []
        for m in c.modifiers:
            if isinstance(m, NotNull):
                if len(pk):
                    self.warning(30, c.table.name, c.name)
                    unused.append(m)
                continue
            if isinstance(m, UniqueMod):
                if len(pk):
                    self.warning(31, m.name, c.table.name, c.name)
                    unused.append(m)
                continue
        for m in unused:
            c.modifiers.remove(m)
        return pk
    
    def fixtables(self, model):
        for t in model.tables.values():
            self.fixtable(t)
                    
    def fixtable(self, t):
        self.promote(t)
        for c in t.columns:
            self.fixcolumn(c)
        
    def promote(self, t):
        unused = []
        for m in t.constraints:
            if isinstance(m, PK):
                if len(m.columns) > 1:
                    continue
                name = m.columns[0]
                column = self.findcolumn(t, name)
                if column is None:
                    continue
                self.warning(40, 'pk', m.name, t.name, name)
                mod = PkMod()
                mod.name = m.name
                mod.modifiers = m.modifiers
                column.modifiers.append(mod)
                unused.append(m)
                continue
            if isinstance(m, FK):
                if len(m.refA.columns) > 1:
                    continue
                name = m.refA.columns[0]
                column = self.findcolumn(t, name)
                if column is None:
                    continue
                self.warning(40, 'fk', m.name, t.name, name)
                mod = FkMod()
                mod.name = m.name
                mod.refA = m.refA
                mod.refB = m.refB
                mod.ondelete = m.ondelete
                column.modifiers.append(mod)
                unused.append(m)
                continue
            if isinstance(m, Unique):
                if len(m.columns) > 1:
                    continue
                name = m.columns[0]
                column = self.findcolumn(t, name)
                if column is None:
                    continue
                self.warning(40, 'unique', m.name, t.name, name)
                mod = UniqueMod()
                mod.name = m.name
                mod.modifiers = m.modifiers
                column.modifiers.append(mod)
                unused.append(m)
                continue
            if isinstance(m, NotNull):
                name = m.columns[0]
                column = self.findcolumn(t, name)
                if column is None:
                    continue
                self.warning(40, 'not null', m.name, t.name, name)
                column.modifiers.append(mod)
                unused.append(m)
                continue
        for m in unused:
            t.constraints.remove(m)
            
    def fixindexes(self, model):
        unused = []
        for t in model.tables.values():
            t.indexed = {}
            for c in t.constraints:
                if isinstance(c, (PK, Unique)):
                    t.indexed[tuple(c.columns)] = c
            for c in t.columns:
                for m in c.modifiers:
                    if isinstance(m, (PkMod, UniqueMod)):
                        t.indexed[(c.name,)] = m
        for i in model.indexes.values():
            t = model.tables.get(i.table)
            if t is None:
                return
            indexed = tuple(i.columns)
            c = t.indexed.get(indexed)
            if c is None:
                continue
            self.warning(50, i.name, c.name, t.name)
            for m in i.modifiers:
                if isinstance(m, Tablespace):
                    c.modifiers.append(TsMod(m.name))
                    continue
                c.modifiers.append(m)
            unused.append(i)
        for i in unused:
            model.content.remove(i)
            del model.indexes[i.name]
            
    def findcolumn(self, t, name):
        for c in t.columns:
            if c.name == name:
                return c
        return None