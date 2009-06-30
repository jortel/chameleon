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

from ply import *
from chameleon.model import *
import sys


#######################################################
# LEXER
#######################################################

states = [
    ('COMMENT', 'exclusive')
]

keywords = [
    'CREATE',
    'REPLACE',
    'INSERT',
    'TO',
    'INTO',
    'VALUES',
    'ALTER',
    'TABLE',
    'COLUMN',
    'INDEX',
    'UNIQUE',
    'CONSTRAINT',
    'REFERENCES',
    'BYTEA',
    'BLOB',
    'CHAR',
    'VARCHAR',
    'VARCHAR2',
    'NUMBER',
    'NUMERIC',
    'SMALLINT',
    'INTEGER',
    'BIGINT',
    'DATE',
    'TIMESTAMP',
    'EVR_T',
    'NOT',
    'NULL',
    'ON',
    'DEFAULT',
    'SEQUENCE',
    'SYNONYM',
    'START',
    'WITH',
    'PRIMARY',
    'FOREIGN',
    'CHECK',
    'KEY',
    'DELETE',
    'CASCADE',
    'SET',
    'CURRENT_TIMESTAMP',
    'CURRENT_DATE',
    'SYSDATE',
    'AND',
    'OR',
    'BETWEEN',
    'IN',
    'IS',
    'ENABLE',
    'ROW',
    'MOVEMENT',
    'TABLESPACE',
    'LOGGING',
    'NOLOGGING',
    'PARALLEL',
    'NOPARALLEL',
    'USING',
    'COMMENT',
    'ADD',
    'DROP',
    'FOR',
    'GLOBAL',
    'TEMPORARY',
    'COMMIT',
    'PRESERVE',
    'ROWS',
    'ORDER',
    'RENAME',
    'MODIFY',
]

symbols = [
    'LPAREN',
    'RPAREN',
    'SEMICOLON',
    'COMMA',
]

tokens = [
    'SQUOTED',
    'DQUOTED',
    'SQLCOMMENT',
    'STARTCOMMENT',
    'ENDCOMMENT',
    'INCLUDE',
    'MACRO',
    'WHITESPACE',
    'IDENTIFIER',
    'DIGITS',
    'EQ',
    'NEQ',
    'GT',
    'GTEQ',
    'LT',
    'LTEQ',
    'PLUS',
    'MINUS',
] + keywords + symbols

def t_SQUOTED(t):
    r"'([^']|'')*'"
    return t

def t_DQUOTED(t):
    r'"[^"]*"'
    return t

def t_WHITESPACE(t):
    r'[ \t]+'
    pass

def t_SQLCOMMENT(t):
    r'(--|\#)[^\n]*'
    pass

def t_STARTCOMMENT(t):
    r'\/\*'
    t.lexer.push_state('COMMENT')
    
def t_COMMENT_ENDCOMMENT(t):
    r'\*\/'
    t.lexer.pop_state()
    
def t_MACRO(t):
    r'\[\[.+\]\]'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z][\.a-zA-Z_0-9]*'
    v = t.value.upper()
    for k in keywords:
        if k == v:
            t.type = k
            break
    return t

def t_INCLUDE(t):
    r'(@|\\i[\s]+)[^\n]+'
    v = t.value
    if v[0] == '@':
        t.value = v[1:]
    else:
        t.value = v.split(' ',1)[1]
    return t

t_DIGITS = r'(-)?[0-9]+'
t_LPAREN = '\('
t_RPAREN = '\)'
t_SEMICOLON = ';'
t_COMMA = ','
t_NEQ = '!='
t_GTEQ = '>='
t_LTEQ = '<='
t_EQ = '='
t_GT = '>'
t_LT = '<'
t_PLUS = '\+'
t_MINUS = '\-'

def t_ANY_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    s = []
    pos, snip = column(t.lexer)
    s.append('(')
    s.append(t.value[0])
    s.append(') unexpected at: ')
    s.append('%d:%d' % (t.lineno, pos))
    s.append(' snip: "%s", skipped' % snip)
    print ''.join(s)
    t.lexer.skip(1)
    
def t_COMMENT_error(t):
    t.lexer.skip(1)

#######################################################
# PARSER
#######################################################

precedence = (\
    ('left', 'LPAREN', 'RPAREN'),
    ('left', 'EQ', 'NEQ','GT', 'GTEQ', 'LT', 'LTEQ', 'PLUS', 'MINUS'),
    ('left', 'NOT', 'AND', 'OR'),
    ('left', 'IS', 'IN'),
)

def p_string(p):
    """
    string : SQUOTED
        | DQUOTED
    """
    p[0] = p[1]

def p_operator(p):
    """
    operator : EQ
        | NEQ
        | GT
        | GTEQ
        | LT
        | LTEQ
        | PLUS
        | MINUS
    """
    p[0] = p[1]
    
def p_term(p):
    """
    term : IDENTIFIER
        | DIGITS
        | string
        | SYSDATE
        | CURRENT_TIMESTAMP
        | CURRENT_DATE
    """
    p[0] = p[1]
    
def p_terms(p):
    """
    terms : term
        | terms COMMA term
    """
    if len(p) == 4:
        p[1].append(',')
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

    
def p_expression(p):
    """
    expression : term operator term
        | term DIGITS
        | term operator LPAREN expression RPAREN
        | term BETWEEN term AND term
        | term IN LPAREN terms RPAREN
        | term IS NULL
        | expression AND expression
        | expression OR expression
        | LPAREN expression RPAREN
        | LPAREN expression RPAREN operator term
    """
    if len(p) == 3:
        ex = Expression([p[1]])
        digits = p[2]
        if digits[0] == '-':
            ex.terms.append('-')
            ex.terms.append(digits[1:])
        else:
            ex.terms.append('+')
            ex.terms.append(digits)
        p[0] = ex
        return
    if isinstance(p[1], Expression):
        ex = p[1]
        ex.terms.append(p[2])
        ex.terms += p[3].terms
        p[0] = ex
        return
    if p[1] == '(':
        ex = p[2]
        ex.terms.insert(0, p[1])
        ex.terms.append(p[3])
        if len(p) > 4:
            ex.terms += p[4:6]
        p[0] = ex
        return
    if p[3] == '(': 
        ex = Expression(p[1:4])
        if isinstance(p[4], Expression):
            ex.terms += p[4].terms
        else:
            ex.terms += p[4]
        ex.terms.append(p[5])
        p[0] = ex
        return
    ex = Expression(p[1:])
    p[0] = ex

def p_identifier(p):
    """ identifier : IDENTIFIER
            | CREATE
            | TABLE
            | COLUMN
            | INDEX
            | UNIQUE
            | REFERENCES
            | DATE
            | NOT
            | NULL
            | ON
            | DEFAULT
            | SEQUENCE
            | START
            | WITH
            | PRIMARY
            | FOREIGN
            | KEY
            | DELETE
            | CASCADE
            | SET
            | ENABLE
            | ROW
            | MOVEMENT
            | TIMESTAMP
            | PARALLEL
            | NOPARALLEL
            | GLOBAL
            | TEMPORARY
            | PRESERVE
            | VALUES
            | ORDER
            | RENAME
            | DROP
            | TO
            | MODIFY
    """
    p[0] = p[1]
    
def p_tdef(p):
    """
    tdef : column
        | pk
        | fk
        | unique
        | ckmod
    """
    p[0] = p[1]
    
def p_tdefs(p):
    """
    tdefs : tdef
        | tdefs COMMA tdef
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[1].append(p[3])
        
def p_tmod(p):
    """
    tmod : tablespace
        | rowMovement
        | logging
        | parallel
        | oncommit
    """
    p[0] = p[1]
    
def p_tmods(p):
    """
    tmods : tmod
        | tmods tmod
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[1].append(p[2])
        
def p_tempTable(p):
    """
    tempTable : GLOBAL TEMPORARY table
    """
    p[3]._global = True
    p[3]._temporary = True
    p[0] = p[3]

def p_table(p):
    """
    table : TABLE identifier LPAREN tdefs RPAREN SEMICOLON
        | TABLE identifier LPAREN tdefs RPAREN tmods SEMICOLON
    """
    table = Table(p[2])
    for m in p[4]:
        if isinstance(m, Column):
            m.table = table
            table.columns.append(m)
            continue
        if isinstance(m, Constraint):
            table.constraints.append(m)
            continue
    if len(p) == 8:
        for m in p[6]:
            table.modifiers.append(m)
    p[0] = table
        
def p_cmod(p):
    """
    cmod : type
        | pkmod
        | notnull
        | default
        | fkmod
        | ckmod
        | uniquemod
    """
    p[0] = p[1]
    
def p_cmods(p):
    """
    cmods : cmod
        | cmods cmod
    """
    n = len(p)
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]
        
def p_column(p):
    """ 
    column : identifier cmods
    """
    column = Column(p[1])
    for m in p[2]:
        column.modifiers.append(m)
    p[0] = column
    
def p_precision(p):
    """
    precision : DIGITS
        | DIGITS COMMA DIGITS
    """
        
def p_type(p):
    """
    type : CHAR
        | BYTEA
        | BLOB
        | CHAR LPAREN DIGITS RPAREN
        | VARCHAR LPAREN DIGITS RPAREN
        | VARCHAR2 LPAREN DIGITS RPAREN
        | NUMBER
        | NUMBER LPAREN precision RPAREN
        | NUMERIC
        | NUMERIC LPAREN precision RPAREN
        | SMALLINT
        | INTEGER
        | BIGINT
        | DATE
        | TIMESTAMP
        | EVR_T
    """
    dt = Type(p[1])
    if len(p) == 5:
        dt.precision = p[3]
    p[0] = dt
        
def p_notnull(p):
    """
    notnull : NOT NULL
        | CONSTRAINT identifier NOT NULL
    """
    if len(p) == 3:
        p[0] = NotNull()
    else:
        p[0] = NotNull(p[2])
        
def p_ckmod(p):
    """
    ckmod : CHECK LPAREN expression RPAREN
        | CONSTRAINT identifier CHECK LPAREN expression RPAREN
    """
    if len(p) == 5:
        p[0] = CkMod(None, p[3])
    else:
        p[0] = CkMod(p[2], p[5])
    
def p_pkmod(p):
    """
    pkmod : PRIMARY KEY
        | PRIMARY KEY tsmod
        | CONSTRAINT identifier PRIMARY KEY
        | CONSTRAINT identifier PRIMARY KEY tsmod
    """
    if len(p) == 3:
        p[0] = PkMod()
        return
    if len(p) == 4:
        p[0] = PkMod()
        p[0].modifiers.append(p[3])
        return
    if len(p) == 5:
        p[0] = PkMod(p[2])
        return
    if len(p) == 6:
        p[0] = PkMod(p[2])
        p[0].modifiers.append(p[5])
        return
        
def p_uniquemod(p):
    """
    uniquemod : UNIQUE
        | UNIQUE tsmod
        | CONSTRAINT identifier UNIQUE
        | CONSTRAINT identifier UNIQUE tsmod
    """
    if len(p) == 2:
        p[0] = UniqueMod()
        return
    if len(p) == 3:
        p[0] = UniqueMod()
        p[0].modifiers.append(p[2])
        return
    if len(p) == 4:
        p[0] = UniqueMod(p[2])
        return
    if len(p) == 5:
        p[0] = UniqueMod(p[2])
        p[0].modifiers.append(p[4])
        return
    
def p_params(p):
    """
    params : value
        | params COMMA value
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]
    
def p_function(p):
    """
    function : identifier LPAREN params RPAREN
    """
    p[0] = Function(p[1], p[3])
    
def p_value(p):
    """
    value : string
        | DIGITS
        | SYSDATE
        | CURRENT_TIMESTAMP
        | CURRENT_DATE
        | NULL
        | function
        | IDENTIFIER
        | expression
    """
    p[0] = p[1]
    
def p_default(p):
    """
    default : DEFAULT value
        | DEFAULT LPAREN value RPAREN
    """
    if len(p) == 3:
        p[0] = Default(p[2])
    else:
        p[0] = Default(p[3])

def p_reflist(p):
    """
    reflist : identifier
        | reflist COMMA identifier
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]
        
def p_ondelete(p):
    """
    ondelete : ON DELETE CASCADE
        | ON DELETE SET NULL
    """
    if p[3].upper() == 'CASCADE':
        p[0] = FK.Cascade()
    else:
        p[0] = FK.Setnull()
        
def p_fkbasemod(p):
    """
    fkbasemod : REFERENCES identifier LPAREN reflist RPAREN
        | CONSTRAINT identifier REFERENCES identifier LPAREN reflist RPAREN
    """
    if len(p) == 6:
        fk = FkMod()
        fk.refB = FK.Reference(p[2], p[4])
    else:
        fk = FkMod(p[2])
        fk.refB = FK.Reference(p[4], p[6])
    p[0] = fk

def p_fkmod(p):
    """
    fkmod : fkbasemod 
        | fkbasemod ondelete
    """
    fk = p[1]
    if len(p) == 3:
        fk.ondelete = p[2]
    p[0] = fk
    
def p_fkbase(p):
    """
    fkbase : CONSTRAINT identifier FOREIGN KEY LPAREN reflist RPAREN REFERENCES identifier LPAREN reflist RPAREN
    """
    fk = FK(p[2])
    fk.refA = FK.Reference(None, p[6])
    fk.refB = FK.Reference(p[9], p[11])
    p[0] = fk
    
def p_fk(p):
    """
    fk : fkbase
        | fkbase ondelete
    """
    fk = p[1]
    if len(p) == 3:
        fk.ondelete = p[2]
    p[0] = fk
    
def p_pk(p):
    """
    pk : CONSTRAINT identifier PRIMARY KEY LPAREN reflist RPAREN
        | CONSTRAINT identifier PRIMARY KEY LPAREN reflist RPAREN tsmod
    """
    pk = PK(p[2], p[6])
    if len(p) == 9:
        pk.modifiers.append(p[8])
    p[0] = pk
    
def p_unique(p):
    """
    unique : CONSTRAINT identifier UNIQUE LPAREN reflist RPAREN
        | CONSTRAINT identifier UNIQUE LPAREN reflist RPAREN tsmod
    """
    u = Unique(p[2], p[5])
    if len(p) == 8:
        u.modifiers.append(p[7])
    p[0] = u
    
def p_tablespace(p):
    """
    tablespace : TABLESPACE identifier
        | TABLESPACE MACRO
    """
    p[0] = Tablespace(p[2])
    
def p_tsmod(p):
    """
    tsmod : USING INDEX TABLESPACE identifier
        | USING INDEX TABLESPACE MACRO
    """
    p[0] = TsMod(p[4])
    
def p_logging(p):
    """
    logging : LOGGING
        | NOLOGGING
    """
    flag = ( p[1].upper() == 'LOGGING' )
    p[0] = Logging(flag)
    
def p_parallel(p):
    """
    parallel : PARALLEL
        | PARALLEL DIGITS
        | NOPARALLEL
    """
    flag = ( p[1].upper() == 'PARALLEL' )
    if len(p) > 2:
        p[0] = Parallel(flag, p[2])
    else:
        p[0] = Parallel(flag)
    
def p_rowMovement(p):
    """
    rowMovement : ENABLE ROW MOVEMENT
    """
    flag = ( p[1].upper() == 'ENABLE' )
    p[0] = RowMovement(flag)
    
def p_oncommit(p):
    """
    oncommit : ON COMMIT DELETE ROWS
        | ON COMMIT PRESERVE ROWS
    """
    flag = ( p[2].upper() == 'PRESERVE' )
    p[0] = OnCommit(flag)
    
def p_imod(p):
    """
    imod : tablespace
        | logging
        | parallel
    """
    p[0] = p[1]
    
def p_imods(p):
    """
    imods : imod
        | imods imod
    """
    if isinstance(p[1], list):
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [p[1]]
        
def p_baseidx(p):
    """
    baseidx : INDEX identifier ON identifier LPAREN reflist RPAREN
    """
    index = Index(p[2], p[4], p[6])
    p[0] = index
    
def p_index(p):
    """
    index : baseidx SEMICOLON
        | baseidx imods SEMICOLON
    """
    index = p[1] 
    if len(p) > 3:
        mods = p[2]
        index.modifiers = p[2]
    p[0] = index
    
def p_uniqueIndex(p):
    """
    uniqueIndex : UNIQUE index
    """
    index = p[2]
    index.unique = True
    p[0] = index
    
def p_seqmod(p):
    """
    seqmod : START WITH DIGITS
        | ORDER
    """
    if p[1].upper() == 'START':
        p[0] = Sequence.StartWith(p[3])
        return
    if p[1].upper() == 'ORDER':
        p[0] = Sequence.Order()
        return
    
def p_seqmods(p):
    """
    seqmods : seqmod
        | seqmods seqmod
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]
    
def p_sequence(p):
    """
    sequence : SEQUENCE identifier SEMICOLON
        | SEQUENCE identifier seqmods SEMICOLON
    """
    sequence = Sequence(p[2])
    if len(p) > 4:
        sequence.modifiers = p[3]
    p[0] = sequence
    
def p_comment(p):
    """
    comment : COMMENT ON TABLE identifier IS string SEMICOLON
        | COMMENT ON COLUMN identifier IS string SEMICOLON
    """
    if '.' in p[4]:
        cn = p[4].split('.')
        p[0] = ColumnComment(cn[0], cn[1], p[6])
    else:
        p[0] = TableComment(p[4], p[6])
        
def p_synonym(p):
    """
    synonym : SYNONYM identifier SEMICOLON
        | SYNONYM identifier FOR identifier SEMICOLON
    """
    if len(p) < 6:
        p[0] = Synonym(p[2])
    else:
        p[0] = Synonym(p[2], p[4])
    
def p_clutter(p):
    """
    clutter : WHITESPACE
        | SQLCOMMENT
        | STARTCOMMENT
        | ENDCOMMENT
    """
    pass

def p_created(p):
    """
    created : table
        | tempTable
        | index
        | uniqueIndex
        | sequence
        | synonym
    """
    p[0] = p[1]

def p_create(p):
    """
    create : CREATE created
        | CREATE OR REPLACE created
    """
    if len(p) < 5:
        p[0] = p[2]
    else:
        p[0] = p[4]
        
def p_rename(p):
    """
    rename : TO identifier
    """
    p[0] = Rename(Rename.Table(None, p[2]))
        
def p_renameColumn(p):
    """
    renameColumn : COLUMN identifier TO identifier
    """
    p[0] = Rename(Rename.Column(p[2], p[4]))
    
def p_drop(p):
    """
    drop : DROP drops SEMICOLON
    """
    x = p[2]
    p[0] = p[2]
    
def p_adds(p):
    """
    adds : tdef
        | tmod
        | LPAREN tdefs RPAREN
        | LPAREN tmods RPAREN
    """
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = (p[1],)

def p_drops(p):
    """
    drops : TABLE identifier
        | INDEX identifier
        | SEQUENCE identifier
        | SYNONYM identifier
        | COLUMN identifier
        | CONSTRAINT identifier
    """
    p[0] = Drop(p[1], p[2])
    
def p_columns(p):
    """
    columns : column
        | columns COMMA column
    """
    if len(p) > 2:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1],]
    
def p_modifyColumns(p):
    """
    modifyColumns : column
        | LPAREN columns RPAREN 
    """
    if len(p) == 2:
        p[0] = Modify((p[1],))
    else:
        p[0] = Modify(p[2])
    
def p_baseAlterTable(p):
    """
    baseAlterTable : ALTER TABLE identifier
    """
    p[0] = p[3]

def p_alterTable(p):
    """
    alterTable : baseAlterTable tmods SEMICOLON
        | baseAlterTable ADD adds SEMICOLON
        | baseAlterTable DROP drops SEMICOLON
        | baseAlterTable RENAME renameColumn SEMICOLON
        | baseAlterTable RENAME rename SEMICOLON
        | baseAlterTable MODIFY modifyColumns SEMICOLON
    """
    if isinstance(p[3], Drop):
        p[0] = Alter.Table(p[1], drops=(p[3],))
        return
    if isinstance(p[3], (Rename, Modify)):
        p[0] = Alter.Table(p[1], mods=(p[3],))
        return
    if len(p) < 5:
        p[0] = Alter.Table(p[1], mods=p[2])
    else:
        p[0] = Alter.Table(p[1], adds=p[3])
        
def p_alterIndex(p):
    """
    alterIndex : ALTER INDEX identifier imods SEMICOLON
    """
    p[0] = Alter.Index(p[3], mods=p[4])
    
def p_values(p):
    """
    values : value
        | values COMMA value
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]
        
def p_baseInsert(p):
    """
    baseInsert : INSERT INTO identifier
    """
    p[0] = p[3]
    
def p_insertColumns(p):
    """
    insertColumns : LPAREN reflist RPAREN
    """
    p[0] = p[2]

def p_insertValues(p):
    """
    insertValues : VALUES LPAREN values RPAREN
    """
    p[0] = p[3]
    
def p_insert(p):
    """
    insert : baseInsert insertValues SEMICOLON
        | baseInsert insertColumns insertValues SEMICOLON
    """
    if len(p) == 4:
        p[0] = Insert(p[1], (), p[2])
    else:
        p[0] = Insert(p[1], p[2], p[3])
        
def p_commit(p):
    """
    commit : COMMIT SEMICOLON
    """
    p[0] = Commit()
    
def p_include(p):
    """
    include : INCLUDE
    """
    p[0] = Include(p[1])
    
def p_ddl(p):
    """ 
    ddl : create
        | drop
        | alterTable
        | alterIndex
        | comment
        | insert
        | commit
        | include
        | clutter
    """
    p[0] = p[1]

def p_script(p):
    """
    script : ddl 
            | script ddl
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]
    
def p_error(p):
    if p is None:
        msg = 'EOF encountered and not expected'
        raise Exception(msg)
    s = []
    if hasattr(p, 'lexer'):
        pos, snip = column(p.lexer)
        pos =+ len(p.value)
    else:
        pos, snip = (0, '')
    s.append('Syntax Error:')
    s.append(' {%s}' % p.type)
    s.append(' "%s"' % p.value)
    s.append(' found at:')
    s.append(' %d:%d' % (p.lineno, pos))
    s.append(' snip: "%s"' % snip)
    msg = ''.join(s)
    print msg
    raise Exception(msg)


#######################################################
# Utility
#######################################################

def getsnip(data, offset):
    width = 60
    start = offset
    for n in range(0, width/2):
        if start < 1: break
        if data[start-1] == '\n':
            break
        start -= 1
    end = offset
    for n in range(0, width/2):
        if data[end] == '\n':
            break
        end += 1
    return data[start:end] 
        
def column(lexer):
    pos = 0
    offset = (lexer.lexpos-1)
    data = lexer.lexdata
    i = offset
    while i > 0:
        c = data[i]
        if c == '\n':
            break
        pos += 1
        i -= 1
    snip = getsnip(data, offset)
    return (pos, snip)


#######################################################
# Parse()
#######################################################

def parse(input, optimized=0):
    lexer = lex.lex(optimize=optimized)
    parser = yacc.yacc(start='script', optimize=optimized)
    return parser.parse(input, lexer=lexer)

