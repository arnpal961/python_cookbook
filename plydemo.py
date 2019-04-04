# plydemo.py
# --- Sample

from sly import Lexer, Parser

code = """
a = 3 * 4 + 5
print(a)
"""

# ----- Tokens
class MyLexer(Lexer):
    tokens = {ID, NUM, PLUS, TIMES, 
              EQ, LPAREN, RPAREN, PRINT}
              
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUM = r'[0-9]+'
    PLUS = r'\+'
    TIMES = r'\*'
    EQ = r'='
    LPAREN = r'\('
    RPAREN = r'\)'
    ID['print'] = PRINT
    ignore = ' \t'

    def NUM(self, t):
        t.value = int(t.value)
        return t

lexer = MyLexer()

# --- Grammar
class MyParser(Parser):
    tokens = MyLexer.tokens

    precedence = (
        ('left', PLUS),
        ('left', TIMES)
    )
    
    @_('statements statement')
    def statements(self, p):
        return p.statements + [ p.statement ]

    @_('statement')
    def statements(self, p):
        return [ p.statement ]
    
    @_('ID EQ expr')
    def statement(self, p):
        return ('assign', p.ID, p.expr)
    
    @_('PRINT LPAREN expr RPAREN')
    def statement(self, p):
        return ('print', p.expr)
    
    @_('expr PLUS expr',
       'expr TIMES expr')
    def expr(self, p):
        return (p[1], p.expr0, p.expr1)
    
    @_('NUM')
    def expr(self, p):
        return ('num', p.NUM)
    
    @_('ID')
    def expr(self, p):
        return ('id', p.ID)

parser = MyParser()