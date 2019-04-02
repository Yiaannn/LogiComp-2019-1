import sys

class Token:

    def __init__(self, _type, value):

        #deixo como string pelo requerimento, mas preferiria um enum
        self.type= _type
        self.value= value

class Tokenizer:

    origin= None
    position= 0
    actual= None

    def init(origin):
        Tokenizer.origin= origin
        position= 0
        actual= None

    def selectNext():
        #Pega o próximo token, dá um pop dele

        #curto-circuitar em EOF?
        if Tokenizer.position == len(Tokenizer.origin):
            Tokenizer.actual= None
            return None

        #eu assumo que eu decido o tipo aqui também
        char= Tokenizer.origin[Tokenizer.position]

        #limpar whitespaces, etc?
        #if char.isspace():

        if char.isdigit():
            #numeric
            Tokenizer.position+=1
            while(Tokenizer.position != len(Tokenizer.origin) and Tokenizer.origin[Tokenizer.position].isdigit()):
                char+= Tokenizer.origin[Tokenizer.position]
                Tokenizer.position+=1

            Tokenizer.actual= Token('NUMERIC', int(char))

        elif char == '+':
            #plus
            Tokenizer.position+=1
            Tokenizer.actual= Token('PLUS', char)

        elif char == '-':
            #minus
            Tokenizer.position+=1
            Tokenizer.actual= Token('MINUS', char)

        elif char == '*':
            #minus
            Tokenizer.position+=1
            Tokenizer.actual= Token('MULT', char)

        elif char == '/':
            #minus
            Tokenizer.position+=1
            Tokenizer.actual= Token('DIV', char)

        elif char == '(':
            #minus
            Tokenizer.position+=1
            Tokenizer.actual= Token('PARENTHESIS_OPEN', char)

        elif char == ')':
            #minus
            Tokenizer.position+=1
            Tokenizer.actual= Token('PARENTHESIS_CLOSE', char)
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

        #limpar o whitespace aqui
        sanitized = ''.join(sanitized.split())

        return sanitized

class Node:


    def __init__(self, value):
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

class NoOp(Node):
    #eu não tenho certeza de como vou usar isso

    def evaluate(self):
        return self.value

    def is_filled(self):
        return len(self.children) == 0

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
            return self.children[0].evaluate() // self.children[1].evaluate()

    def is_filled(self):
        return len(self.children) == 2

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
        #acho que não faço nada aqui além de retornar meu valor
        return self.value

    def is_filled(self):
        return len(self.children) == 0

class Parser:

    #Para cada estado, fazer um set de estados válidos seguintes
    states={
        'INIT': set(['NUMERIC', 'PLUS', 'MINUS', 'PARENTHESIS_OPEN']),
        'NUMERIC': set(['PLUS', 'MINUS', 'MULT', 'DIV', 'EOF', 'PARENTHESIS_CLOSE']),
        'PLUS': set(['NUMERIC', 'PLUS', 'MINUS', 'PARENTHESIS_OPEN']),
        'MINUS': set(['NUMERIC', 'PLUS', 'MINUS', 'PARENTHESIS_OPEN']),
        'MULT': set(['NUMERIC', 'PARENTHESIS_OPEN']),
        'DIV': set(['NUMERIC', 'PARENTHESIS_OPEN']),
        'PARENTHESIS_OPEN': set(['NUMERIC']),
        'PARENTHESIS_CLOSE': set(['NUMERIC', 'PLUS', 'MINUS', 'MULT', 'DIV', 'EOF']),
        'EOF': set([])
    }

    ptoken= 0
    state= 'INIT'

    def run(code):
        Tokenizer.init(code)

        root= Parser.parseExpression()
        while(Tokenizer.actual):
            root= Parser.parseExpression(floater=root)

        #posso checar por EOF pelo tokenizer.actual
        if Parser.ptoken:
            raise Exception('Error: Mismatched parenthesis. "(" could not be matched')
        if 'EOF' not in Parser.states[Parser.state]:
            raise Exception('Error: Reached EOF before finishing Expression')

        return root

    def parseExpression(floater= None, scope_power=0):
        root= None #node em que tou trabalhando
        #floater segura um node cujo pai ainda não foi parseado

        while( (   (root== None) or (root and not root.is_filled())   ) and Tokenizer.selectNext()):
            t= Tokenizer.actual

            #TODO: Confirmar porque não travo em string vazia
            if t.type not in Parser.states[Parser.state]:
                if t.type=='PARENTHESIS_CLOSE':
                    if Parser.ptoken:
                        Parser.ptoken-=1
                        break; #tratar como um EOF
                    raise Exception('Error: Mismatched Parenthesis, \')\' found before \'(\' ')
                raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: "+str(Parser.states[Parser.state]))
            Parser.state= t.type

            #agir de acordo com o tipo do token
            if  t.type == 'NUMERIC':
                    floater= IntVal(t.value)
                    if scope_power == 1:
                        root=floater
                        floater= None

            if t.type == 'PLUS' or t.type == "MINUS":
                if floater:
                    #operador binário
                    root= BinOp(t.value)
                    root.add_child(floater)
                    floater= None
                    root.add_child(Parser.parseExpression())
                else:
                    #operador unário
                    root= UnOp(t.value)
                    root.add_child(Parser.parseExpression())

            if t.type == "MULT" or t.type == "DIV":
                #não deveria existir um cenário que eu chego aqui sem um floater
                #digo, assumindo um código bem-formado
                root= BinOp(t.value)
                root.add_child(floater)
                floater= None
                root.add_child(Parser.parseExpression(scope_power=1))

            if t.type == 'PARENTHESIS_OPEN':
                Parser.ptoken+= 1
                root= Parser.parseExpression()

            if t.type == 'PARENTHESIS_CLOSE':
                #deveria só ter um floater neste ponto
                root= floater
                floater= None
                #preciso checar se meus parentesis fazem sentido aqui?
                Parser.ptoken-= 1
                if Parser.ptoken < 0:
                    raise Exception('Error: Mismatched parenthesis. ")" could not be matched')

        #TODO se eu chegar no final somente com um floater, preciso tratar isso de alguma forma
        #acho que promovo ele pro root?
        if root == None:
            root= floater

        return root

if len(sys.argv) != 2:
    print("Run with: \'python3 main.py <filename.vbs> \'")
else:
    with open(sys.argv[1], 'r') as f:
        sanit= PrePro.run( f.read() )
        print( Parser.run( sanit ).evaluate() )
