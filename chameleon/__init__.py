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
# written by: Jeff Ortel ( jortel@redhat.com )

__version__ = 0.2


class PrettyPrinter:
    """ 
    Pretty printing of a Object object.
    """
    
    @classmethod
    def indent(cls, n):
        return '%*s'%(n*2,' ')

    def tostr(self, pyobj, indent=-2):
        """ get s string representation of pyobj """
        history = []
        return self.process(pyobj, history, indent)
    
    def process(self, pyobj, h, n=0, nl=False):
        """ print pyobj using the specified indent (n) and newline (nl). """
        if pyobj is None:
            return 'None'
        if isinstance(pyobj, dict):
            if pyobj:
                return self.printDict(pyobj, h, n+2, nl)
            else:
                return '<empty>'
        if isinstance(pyobj, (list,tuple)):
            if pyobj:
                return self.printList(pyobj, h, n+2)
            else:
                return '<empty>'
        if isinstance(pyobj, (basestring, bool, int)):
            return '"%s"' % str(pyobj)
        if isinstance(pyobj, object):
            if pyobj.__dict__:
                return self.printObject(pyobj, h, n+2, nl)
            else:
                return '<empty>'
        return '%s' % self.process(pyobj)
    
    def printObject(self, d, h, n, nl=False):
        """ print complex using the specified indent (n) and newline (nl). """
        s = []
        cls = d.__class__
        if d in h:
            s.append('(')
            s.append(cls.__name__)
            s.append(')')
            s.append('...')
            return ''.join(s)
        h.append(d)
        if nl:
            s.append('\n')
            s.append(self.indent(n))
        s.append('(')
        s.append(cls.__name__)
        s.append(')')
        s.append('\n')
        s.append(self.indent(n))
        s.append('{')
        for item in d.__dict__.items():
            if item[0].startswith('_'):
                continue
            s.append('\n')
            s.append(self.indent(n+1))
            if isinstance(item[1], (list,tuple)):            
                s.append(str(item[0]))
                s.append('[]')
            else:
                s.append(str(item[0]))
            s.append(' = ')
            s.append(self.process(item[1], h, n, True))
        s.append('\n')
        s.append(self.indent(n))
        s.append('}')
        h.pop()
        return ''.join(s)
    
    def printDict(self, d, h, n, nl=False):
        """ print complex using the specified indent (n) and newline (nl). """
        if d in h: return '{}...'
        h.append(d)
        s = []
        if nl:
            s.append('\n')
            s.append(self.indent(n))
        s.append('{')
        for item in d.items():
            s.append('\n')
            s.append(self.indent(n+1))
            if isinstance(item[1], (list,tuple)):            
                s.append(str(item[0]))
                s.append('[]')
            else:
                s.append(str(item[0]))
            s.append(' = ')
            s.append(self.process(item[1], h, n, True))
        s.append('\n')
        s.append(self.indent(n))
        s.append('}')
        h.pop()
        return ''.join(s)

    def printList(self, c, h, n):
        """ print collection using the specified indent (n) and newline (nl). """
        if c in h: return '[]...'
        h.append(c)
        s = []
        for item in c:
            s.append('\n')
            s.append(self.indent(n))
            s.append(self.process(item, h, n-2))
            s.append(',')
        h.pop()
        return ''.join(s)
