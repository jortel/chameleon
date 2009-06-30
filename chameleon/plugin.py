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

TAB = 4

def indent(n):
    if not n:
        return ''
    return '%*s' % (n, ' ')

class Plugin:
    
    def __init__(self, factory):
        self.factory = factory
        
    def plugin(self, m):
        return self.factory.get(m)
        
    def render(self, x, n=0):
        raise Exception()
    
    def option(self, name, default=None):
        return self.factory.options.get(name, default)
    
    def sorted(self, collection):
        return self.factory.sorted(collection)
    
    def xlated(self, s):
        return self.factory.xlated(s)
    
    def join(self, s):
        s = ''.join(s)
        return s.replace('\n\n', '\n')
                


class EmptyPlugin(Plugin):

    def render(self, x, n=0):
        return ''


class PluginFactory:
    
    def __init__(self):
        self.ordering = []
        self.plugins = {}
        self.options = {}

    def get(self, object):
        try:
            return self.plugins[object.__class__]
        except:
            msg = 'plugin for %s, not-found' % object.__class__
            raise Exception(msg)
        
    def sorted(self, collection):
        return sorted(collection, self.cmpfn)
    
    def xlated(self, s):
        return s
    
    def index(self, x):
        try:
            return self.ordering.index(x)
        except:
            msg = 'factory missing ordering for %s' % x.__name__
            raise Exception(msg)

    def cmpfn(self, a, b):
        myindex = self.index(a.__class__)
        otherindex = self.index(b.__class__)
        if myindex < otherindex:
            return -1
        else:
            return 1
        
        
class BaseModel(Plugin):

    def render(self, model, n=0):
        s = []
        if self.option('sort', False):
            content = self.factory.sorted(model.content)
        else:
            content = model.content
        for t in content:
            p = self.plugin(t)
            s.append(p.render(t))
        return '\n\n'.join(s)