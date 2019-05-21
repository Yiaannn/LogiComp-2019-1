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

    #keywords=set(['begin', 'end', 'print', 'or', 'and', 'not'])
    #não tenho mais begin e end então?
    keywords=set(['print', 'input', 'or', 'and', 'not', 'if', 'then', 'else', 'end', 'while', 'wend', 'sub', 'main', 'dim', 'as', 'integer', 'boolean'])

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
            Tokenizer.position+= 1
            Tokenizer.actual= Token('PLUS', char)

        elif char == '-':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('MINUS', char)

        elif char == '*':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('MULT', char)

        elif char == '/':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('DIV', char)

        elif char == '(':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('PARENTHESIS_OPEN', char)

        elif char == ')':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('PARENTHESIS_CLOSE', char)

        elif char == '=':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('EQUALS', char)

        elif char == '<':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('LOWER_THAN', char)

        elif char == '>':
            Tokenizer.position+= 1
            Tokenizer.actual= Token('GREATER_THAN', char)

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
        '''
        if parent:
            self.dict=parent.dict.copy() #Se entro em um novo escopo de BEGIN/END, uso uma nova symboltable
        '''
        #em vez de copy, repopular a ST de tráz? tou na dúvida agora
        self.parent= parent #salva o escopo originário para voltar depois

        SymbolTable.current= self

    #por enquanto acho que não tem diferença prática entre definir e redefinir
    #estou assumindo também que é impossível declarar sem definir

    def start(self, key, type):
        if key in self.dict:
            raise Exception("Variable "+str(key)+" already declared, redeclaration is not possible.")

        self.dict[key]= [None, type] #lista na forma valor, tipo

    def update(self, key, value):
        if key not in self.dict:
            raise Exception("Variable "+str(key)+" has not yet been declared, assigning it a value is not possible.")

        if( (isinstance(value, int) and self.dict[key][1] != 'integer') or (isinstance(value, bool) and self.dict[key][1] != 'boolean')  ):
            raise Exception("Value "+str(value)+" assigned to variable "+str(key)+" is not of type "+str(self.dict[key][1])+".")

        self.dict[key][0]= value

    def read(self, key):
        if key in self.dict:
            if self.dict[key] == None:
                raise Exception("Variable "+str(key)+" not initialized before operation.")
            else:
                return self.dict[key][0]
        else:
            raise Exception("Variable "+str(key)+" has not yet been declared, no value can be obtained from it.")

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

class Main_Node(Node):

    def evaluate(self):
        #apenas um filho, classe statements
        self.children[0].evaluate()

    def is_filled(self):
        return len(self.children) == 0

class NoOp(Node):
    #eu não tenho certeza de como vou usar isso

    def evaluate(self):
        return self.value

    def is_filled(self):
        return len(self.children) == 0

class Statements(Node):

    def evaluate(self):
        #SymbolTable(SymbolTable.current)
        #pausar a questão de symbol table até a parte que precisa
        if not SymbolTable.current:
            SymbolTable()

        for statement in self.children:
            statement.evaluate()

        #SymbolTable.current= SymbolTable.current.parent


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
        if self.value=='or':
            return self.children[0].evaluate() or self.children[1].evaluate()
        if self.value=='and':
            return self.children[0].evaluate() and self.children[1].evaluate()

        if self.value=="=":
            return int( self.children[0].evaluate() == self.children[1].evaluate() )
        if self.value=="<":
            return int( self.children[0].evaluate() < self.children[1].evaluate() )
        if self.value==">":
            return int( self.children[0].evaluate() > self.children[1].evaluate() )

    def is_filled(self):
        return len(self.children) == 2

class PrintOp(Node):

    def evaluate(self):
        print(self.children[0].evaluate())

    def is_filled(self):
        return len(self.children) == 1

class IfOp(Node):
    #três partes, RelExpr, statements 1, statements 2 (opcional)

    def evaluate(self):
        boo= self.children[0].evaluate()

        if boo == 1:
            self.children[1].evaluate()
        elif boo == 0 and len(self.children) == 3:
            self.children[2].evaluate()

class WhileOp(Node):

    def evaluate(self):
        #Pra ser sincero eu estou meio confuso aqui
        #é isso mesmo?
        while(self.children[0].evaluate()):
            self.children[1].evaluate()


    def is_filled(self):
        return len(self.children) == 2

class UnOp(Node):
    # +
    # -
    # not

    def evaluate(self):
        #pegar o filho, resolver num Int
        tmp= self.children[0].evaluate()
        if self.value == "-":
            tmp=-tmp
        elif self.value == 'not':
            tmp=int(not tmp)
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
        return SymbolTable.current.read(self.value)

    def is_filled(self):
        return len(self.children) == 0

class Input(Node):

    def evaluate(self):
        return int(input())

    def is_filled(self):
        return len(self.children) == 0

class AssignOp(Node):

    def evaluate(self):
        key= self.children[0].value #não evaluo em assignment
        value= self.children[1].evaluate()

        SymbolTable.current.update(key, value)

    def is_filled(self):
        return len(self.children) == 2

class Declaration(Node):

    def evaluate(self):
        #primeiro filho é o identifier, segundo é o tipo
        key= self.children[0].value #não evaluo em declaration
        type= self.children[1].evaluate()

        SymbolTable.current.start(key, type)

    def is_filled(self):
        return len(self.children) == 2

class Type_Node(Node):

    def evaluate(self):
        return self.value

    def is_filled(self):
        return len(self.children) == 0

#class Comparison_BinOP(Node):
#Juntei esse no BinOP, tem o mesmo formato de entrada e saída então why not

class Parser():
    #A partir do 2.3, vou pensar neste como o Program

    def run(code):
        Tokenizer.init(code)

        root= Main_Node()
        #checar o boilerplate inicial
        if Tokenizer.selectNext().type != 'SUB':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: SUB")

        if Tokenizer.selectNext().type != 'MAIN':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: MAIN")

        if Tokenizer.selectNext().type != 'PARENTHESIS_OPEN':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: PARENTHESIS_OPEN")

        if Tokenizer.selectNext().type != 'PARENTHESIS_CLOSE':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: PARENTHESIS_CLOSE")

        if Tokenizer.selectNext().type != 'LINE_BREAK':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: LINE_BREAK")

        root.add_child( StatementsParser.run('sub') )

        return root


class StatementsParser(Parser):

    statement={'PRINT', 'IDENTIFIER', 'IF', 'WHILE'} #Input vai aqui?

    def run(end_context):
        #TODO
        #Acho que estou encaminhado, só preciso de meus parsers
        #Meu pelo menos três mais, dos blocos, do print e do assignment.
        #Talvez eu ainda possa ter uma expressão pura como um statement
        #Também tenho que decidir como tratar as quebras de linha

        #preciso estar atento que posso ter 0 statesments no meu bloco

        root= Statements()

        while(Tokenizer.selectNext()):
            t= Tokenizer.actual

            if t.type == "END" and end_context == 'if':
                if Tokenizer.selectNext().type == "IF":
                    if Tokenizer.selectNext().type == 'LINE_BREAK':
                        return root
                    else:
                        raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: "+"LINE_BREAK")
                else:
                    raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: "+"IF")
            elif t.type == "ELSE" and end_context == 'if':
                return root
            elif t.type == "WEND" and end_context == 'while':
                if Tokenizer.selectNext().type == "LINE_BREAK":
                    return root
                else:
                    raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: "+"LINE_BREAK")
            elif t.type == "END" and end_context == 'sub':
                if Tokenizer.selectNext().type == 'SUB':
                    return root
                else:
                    raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: "+"SUB")


            #Todo: tratar o EOF de verdade (fim do arquivo)

            elif t.type == 'PRINT':
                node= PrintOp()
                node.add_child(ExpressionParser.run())
                root.add_child(node)

            elif t.type == 'IDENTIFIER':
                root.add_child(AssignmentParser.run( Identifier(t.value) ))

            elif t.type == 'DIM':
                root.add_child(DeclarationParser.run())

            elif t.type== 'IF':
                root.add_child(BranchParser.run())

            elif t.type == 'WHILE':
                root.add_child(LoopParser.run())

            else:
                raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: "+str(StatementsParser.statement))

        '''
        if EOF:
            t= Tokenizer.selectNext()
            if t.type != 'LINE_BREAK':
                raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: LINE_BREAK")

            return root
        '''
        #raise Exception('Reached EOF before END keyword')
        return root

class DeclarationParser:
    def run():
        node= Declaration()
        t= Tokenizer.selectNext()
        if t.type != 'IDENTIFIER':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: IDENTIFIER")
        node.add_child(Identifier(t.value))
        t= Tokenizer.selectNext()
        if t.type != 'AS':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: AS")
        t= Tokenizer.selectNext()
        if t.type != 'INTEGER' and t.type != 'BOOLEAN':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: [INTEGER, BOOLEAN]")
        node.add_child(Type_Node(t.value))
        t= Tokenizer.selectNext()
        if t.type != 'LINE_BREAK':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: LINE_BREAK")

        return node


class AssignmentParser:
    def run(floater= None):

        #Assumo que chegando aqui já lí o identifier

        root= AssignOp()
        root.add_child(floater)
        t= Tokenizer.selectNext()
        if t.type != 'EQUALS':
            raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: EQUALS")
        root.add_child(ExpressionParser.run())

        return root

class LoopParser:
    def run(floater= None):
        #aqui tem a RelExp e os Statements
        node= WhileOp()

        #node.add_child(RelExpressionParser.run())
        node.add_child(ExpressionParser.run())
        node.add_child(StatementsParser.run('while'))

        return node

class BranchParser:
    def run(floater=None):
        #Acho que tenho que especificar o Then como um possivel fim de expressão

        node = IfOp()
        node.add_child(ExpressionParser.run())
        node.add_child(StatementsParser.run('if'))

        #implementar também meu else!
        if Tokenizer.actual.type == 'ELSE':
            if Tokenizer.selectNext().type == 'LINE_BREAK':
                node.add_child(StatementsParser.run('if'))
            else:
                raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: "+"LINE_BREAK")

        return node

'''
class RelExpressionParser:
    #ughhhh
    #segundo o DS, RelExpression tem sempre uma cara dual (expr op expr)
    #imagino que isso mude no futuro

    #problema 1: como identifico o fim da expressão?
    #e se eu passar finais especiais como parâmetros?

    #melhor pergunta, o que me impede de tratar RelExpression como um expression?
    #não posso adicionar os comparadores na árvore como operadores?
    pass
'''

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
                elif t.type == 'IDENTIFIER':
                    floater= Identifier(t.value)
                elif t.type == 'INPUT':
                    floater= Input(t.value)
                elif t.type == 'PLUS' or t.type == 'MINUS' or t.type == 'NOT':
                    #operador unário
                    floater= UnOp(t.value)
                    t= Tokenizer.selectNext()
                    curr= floater

                    while t.type == 'PLUS' or t.type == 'MINUS' or t.type == 'NOT':
                        hold= UnOp(t.value)
                        curr.add_child( hold )
                        curr= hold
                        t= Tokenizer.selectNext()

                    if t.type == "NUMERIC":
                        curr.add_child( IntVal(t.value) )
                    elif t.type == "IDENTIFIER":
                        curr.add_child( Identifier(t.value) )
                    elif t.type == "INPUT":
                        curr.add_child( Input(t.value) )
                    else:
                        raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: NUMERIC or IDENTIFIER")

                else:
                    raise Exception('Error: Unexpected word \"'+str(t.value)+"\" of type \""+str(t.type)+"\", expected: NUMERIC, PARENTHESIS_OPEN, PLUS or MINUS")

            if shortcircuit:
                return floater

            #pensar agora em possíveis EOFs (PARENTHESIS_CLOSE, LINE_BREAK)
            t= Tokenizer.selectNext()

            #fazer uma gambiarrinha aqui pro THEN
            #ele é redundante pelo LINE_BREAK
            if t.type == 'THEN':
                t= Tokenizer.selectNext()
            #fim da gambiarrinha

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
            if t.type == 'PLUS' or t.type == 'MINUS' or t.type == 'OR':
                root= BinOp(t.value)
                root.add_child(floater)
                root.add_child(ExpressionParser.run(False, scope_power))
            elif t.type == 'GREATER_THAN' or t.type == 'LOWER_THAN' or t.type == 'EQUALS':
                root= BinOp(t.value)
                root.add_child(floater)
                root.add_child(ExpressionParser.run(False, scope_power))
            elif t.type == "MULT" or t.type == "DIV" or t.type == 'AND':
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
