import sys
import re

class Token:

    def __init__(self, _type, value):

        #deixo como string pelo requerimento, mas preferiria um enum
        self.type= _type
        self.value= value

class Tokenizer:

    origin= None
    position= 0
    actual= None

    keywords=set(['begin', 'end', 'print'])

    def init(origin):
        Tokenizer.origin= origin
        position= 0
        actual= None

    def isIdentifiable(char):
        #Não deve ser usado para o primeiro caracter de um identifier

        return char.isdigit() or char.isalpha() or char=='_'

    def selectNext():
        #Pega o próximo token, dá um pop dele

        #curto-circuitar em EOF?
        if Tokenizer.position == len(Tokenizer.origin):
            Tokenizer.actual= None
            return None

        #eu assumo que eu decido o tipo aqui também
        char= Tokenizer.origin[Tokenizer.position]

        #limpar whitespaces, etc?
        if char== " " or char == "\t":
            Tokenizer.position+= 1
            return Tokenizer.selectNext()

        if char.isdigit():
            #numeric
            Tokenizer.position+= 1
            while(Tokenizer.position != len(Tokenizer.origin) and Tokenizer.origin[Tokenizer.position].isdigit()):
                char+= Tokenizer.origin[Tokenizer.position]
                Tokenizer.position+= 1

            Tokenizer.actual= Token('NUMERIC', int(char))

        elif char.isalpha():
            #keyword ou identifier
            Tokenizer.position+= 1
            while(Tokenizer.position != len(Tokenizer.origin) and Tokenizer.isIdentifiable(Tokenizer.origin[Tokenizer.position])):
                char+= Tokenizer.origin[Tokenizer.position]
                Tokenizer.position+= 1

            if char in Tokenizer.keywords:
                Tokenizer.actual= Token(char.upper(), char)
            else:
                Tokenizer.actual= Token('IDENTIFIER', char)

        elif char == '+':
            #plus
            Tokenizer.position+= 1
            Tokenizer.actual= Token('PLUS', char)

        elif char == '-':
            #minus
            Tokenizer.position+= 1
            Tokenizer.actual= Token('MINUS', char)

        elif char == '*':
            #minus
            Tokenizer.position+= 1
            Tokenizer.actual= Token('MULT', char)

        elif char == '/':
            #minus
            Tokenizer.position+= 1
            Tokenizer.actual= Token('DIV', char)

        elif char == '(':
            #minus
            Tokenizer.position+= 1
            Tokenizer.actual= Token('PARENTHESIS_OPEN', char)

        elif char == ')':
            #minus
            Tokenizer.position+=1
            Tokenizer.actual= Token('PARENTHESIS_CLOSE', char)

        elif char == '\n':
            #linebreak, que agora faz parte do léxico
            Tokenizer.position+=1
            Tokenizer.actual= Token('LINE_BREAK', char)

        else:
            #melhorar esse erro pra me dar o token inteiro incorreto
            raise Exception('Error: Unexpected character \"'+char+'\" at position '+str(Tokenizer.position)+", line:\n"+Tokenizer.origin)
        return Tokenizer.actual

class PrePro:

    def run(code):
        comment= False;
        sanitized= ""

        #poderia incluir caracter de escape, mas acho que a especificação não pede
        #por exemplo, string=(" \' isso vai ser lido como um comentário")
        for char in code:

            if char == "\'" and not comment:
                comment= True

            if not comment:
                sanitized+= char

            if char == "\n" and comment:
                comment= False
                sanitized+= char

        #limpar o whitespace aqui
        #sanitized = ''.join(sanitized.split())

        #que tal tirar os linebreaks e espaços consecutivos? só manter os "únicos"
        sanitized= re.sub(' +', ' ', sanitized)
        sanitized= re.sub(' \n', '\n', sanitized)
        sanitized= re.sub('\n ', '\n', sanitized)
        sanitized= re.sub('\n+', '\n', sanitized)

        #tirar canse-sensitiveness aqui
        sanitized= sanitized.lower()

        return sanitized

class SymbolTable:
    #Posso otimizar isso aqui pra ser uma classe mista

    current= None #salva o escopo atual em que estou trabalhando

    def __init__(self, parent=None):
        self.dict= {}
        if parent:
            self.dict=parent.dict.copy() #Se entro em um novo escopo de BEGIN/END, uso uma nova symboltable
        self.parent= parent #salva o escopo originário para voltar depois

        SymbolTable.current= self

    #por enquanto acho que não tem diferença prática entre definir e redefinir
    #estou assumindo também que é impossível declarar sem definir
    def update(self, key, value):
        self.dict[key]= value

    def read(self, key):
        if key in self.dict:
            return self.dict[key]
        raise Exception("Variable "+str(key)+" not initialized!")

class Node:


    def __init__(self, value=None):
        self.value= value
        self.child_counter= 0
        self.children=[]

    def add_child(self, node):
        #fazer um check se não estou adicionando filhos além do limite?
        self.children.append(node)

    def evaluate(self):
        raise NotImplementedError

    def is_filled(self):
        raise NotImplementedError

    def debug_print(self, tab = 0):
        tabs="  "*tab
        print(tabs+str(self.value)+" ("+str(type(self))+")")
        for child in self.children:
            child.debug_print(tab+1)

class NoOp(Node):
    #eu não tenho certeza de como vou usar isso

    def evaluate(self):
        return self.value

    def is_filled(self):
        return len(self.children) == 0

class Statements(Node):

    def evaluate(self):
        SymbolTable(SymbolTable.current)

        for statement in self.children:
            statement.evaluate()

        SymbolTable.current= SymbolTable.current.parent


    #não acho que faça sentido perguntar se statements está filled, ele não tem um número fixo de filhos

class BinOp(Node):
    # +
    # -
    # *
    # /

    def evaluate(self):
        if self.value=="+":
            return self.children[0].evaluate() + self.children[1].evaluate()
        if self.value=="-":
            return self.children[0].evaluate() - self.children[1].evaluate()
        if self.value=="*":
            return self.children[0].evaluate() * self.children[1].evaluate()
        if self.value=="/":
            #return self.children[0].evaluate() // self.children[1].evaluate()
            #um -2/4 retorna -1 em vez de 0, acho que esse não é o comportamento que eu quero
            return int( self.children[0].evaluate() / self.children[1].evaluate() )

    def is_filled(self):
        return len(self.children) == 2

class PrintOp(Node):

    def evaluate(self):
        print(self.children[0].evaluate())

    def is_filled(self):
        return len(self.children) == 1

class UnOp(Node):
    # +
    # -

    def evaluate(self):
        #pegar o filho, resolver num Int
        tmp= self.children[0].evaluate()
        if self.value == "-":
            tmp=-tmp
        return tmp

    def is_filled(self):
        return len(self.children) == 1

class IntVal(Node):

    def evaluate(self):
        return self.value

    def is_filled(self):
        return len(self.children) == 0

class Identifier(Node):

    def evaluate(self):
        #preciso garantir que meu SymbolTable setado sempre é o correto
        return SymbolTable.current.read(self.value)

    def is_filled(self):
        return len(self.children) == 0

class AssignOp(Node):

    def evaluate(self):
        key= self.children[0].value #não evaluo em assignment
        value= self.children[1].evaluate()

        SymbolTable.current.update(key, value)

class Parser():

    def run(code):
        Tokenizer.init(code)

        root= Statements()
        t= Tokenizer.selectNext()
        while(t):
            if t.type != "BEGIN":
                raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: BEGIN")
            root.add_child( StatementsParser.run() )
            t= Tokenizer.selectNext()

        return root


class StatementsParser(Parser):

    statement={'PRINT', 'IDENTIFIER', 'BEGIN', 'END'}

    def run():
        #TODO
        #Acho que estou encaminhado, só preciso de meus parsers
        #Meu pelo menos três mais, dos blocos, do print e do assignment.
        #Talvez eu ainda possa ter uma expressão pura como um statement
        #Também tenho que decidir como tratar as quebras de linha

        #assumir que quando cheguei aqui já lí um BEGIN
        EOF= False

        root= Statements()

        t= Tokenizer.selectNext()
        if t.type != 'LINE_BREAK':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: LINE_BREAK")

        while(Tokenizer.selectNext()):
            t= Tokenizer.actual

            if t.type == "END":
                EOF= True
                break;
            elif t.type == 'PRINT':
                node= PrintOp()
                node.add_child(ExpressionParser.run())
                root.add_child(node)
            elif t.type == 'IDENTIFIER':
                root.add_child(AssignmentParser.run( Identifier(t.value) ))

            elif t.type== 'BEGIN':
                root.add_child(StatementsParser.run())
            else:
                raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: "+str(StatementsParser.statement))

        if EOF:
            t= Tokenizer.selectNext()
            if t.type != 'LINE_BREAK':
                raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: LINE_BREAK")

            return root
        raise Exception('Reached EOF before END keyword')

class AssignmentParser:
    def run(floater= None):

        #Assumo que chegando aqui já lí o identifier

        root= AssignOp()
        root.add_child(floater)
        root.add_child(ExpressionParser.run())

        return root

class ExpressionParser:
    #TODO redefinir a condição de parada deste parser

    #Para cada estado, fazer um set de estados válidos seguintes
    states={
        'INIT': set(['NUMERIC', 'PLUS', 'MINUS', 'PARENTHESIS_OPEN']),
        'NUMERIC': set(['PLUS', 'MINUS', 'MULT', 'DIV', 'LINE_BREAK', 'PARENTHESIS_CLOSE']),
        'PLUS': set(['NUMERIC', 'PLUS', 'MINUS', 'PARENTHESIS_OPEN']),
        'MINUS': set(['NUMERIC', 'PLUS', 'MINUS', 'PARENTHESIS_OPEN']),
        'MULT': set(['NUMERIC', 'PARENTHESIS_OPEN']),
        'DIV': set(['NUMERIC', 'PARENTHESIS_OPEN']),
        'PARENTHESIS_OPEN': set(['NUMERIC']),
        'PARENTHESIS_CLOSE': set(['NUMERIC', 'PLUS', 'MINUS', 'MULT', 'DIV', 'LINE_BREAK']),
        'LINE_BREAK': set([])
    }
    #Meus Line Breaks funcionam como EOFs

    EOF= False
    emerge= -1

    '''
    def run():
        #TODO: Tenho que fazer o loop da expression independente do RootParser

        root= Parser.parseExpression()
        while(Tokenizer.actual):
            root= Parser.parseExpression(floater=root)

        #posso checar por EOF pelo tokenizer.actual
        if Parser.ptoken:
            raise Exception('Error: Mismatched parenthesis. "(" could not be matched')
        if 'EOF' not in Parser.states[Parser.state]:
            raise Exception('Error: Reached EOF before finishing Expression')

        return root
    '''

    def run(shortcircuit=False, scope_power=0):

        root= None #node em que tou trabalhando
        #floater segura um node cujo pai ainda não foi parseado
        ExpressionParser.EOF= False

        floater= None
        while(True):

            if not floater:
                t= Tokenizer.selectNext()

                if t.type == 'PARENTHESIS_OPEN':
                    floater= ExpressionParser.run(False, 1)
                elif t.type == 'NUMERIC':
                    floater= IntVal(t.value)
                elif t.type == 'PLUS' or t.type == 'MINUS':
                    #operador unário
                    floater= UnOp(t.value)
                    t= Tokenizer.selectNext()
                    curr= floater

                    while t.type == 'PLUS' or t.type == 'MINUS':
                        hold= UnOp(t.value)
                        curr.add_child( hold )
                        curr= hold
                        t= Tokenizer.selectNext()

                    if t.type== "NUMERIC":
                        curr.add_child( IntVal(t.value) )
                    else:
                        raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: NUMERIC")

                else:
                    raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: NUMERIC, PARENTHESIS_OPEN, PLUS or MINUS")

            if shortcircuit:
                return floater

            #pensar agora em possíveis EOFs (PARENTHESIS_CLOSE, LINE_BREAK)
            t= Tokenizer.selectNext()
            if t.type == 'LINE_BREAK':
                if scope_power == 0:
                    ExpressionParser.EOF= True
                    return floater
                else:
                    raise Exception('Error: Mismatched Parenthesis, end of expression reached before \')\'')
            elif t.type == 'PARENTHESIS_CLOSE':
                if scope_power == 0:
                    raise Exception('Error: Mismatched Parenthesis, \')\' found before \'(\' ')
                else:
                    ExpressionParser.emerge= scope_power
                    return floater

            #operação agora
            if t.type == 'PLUS' or t.type == 'MINUS':
                root= BinOp(t.value)
                root.add_child(floater)
                root.add_child(ExpressionParser.run(False, scope_power))
            elif t.type == "MULT" or t.type == "DIV":
                root= BinOp(t.value)
                root.add_child(floater)
                root.add_child(ExpressionParser.run(True, scope_power))
            else:
                raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: MULT, DIV, PLUS or MINUS")

            #tenho que checar por line_break, senão jogar root no meu floater e continuar
            shortcircuit= ExpressionParser.EOF
            if ExpressionParser.emerge!= -1:
                if ExpressionParser.emerge != scope_power:
                    ExpressionParser.emerge= -1
                else:
                    shortcircuit= True

            floater= root

            #print(shortcircuit)


if len(sys.argv) != 2:
    print("Run with: \'python3 main.py <filename.vbs> \'")
else:
    with open(sys.argv[1], 'r') as f:
        sanit= PrePro.run( f.read() )
        Parser.run( sanit ).evaluate()
