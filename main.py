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
        #Tokenizer.origin= origin
        #limpar o whitespace aqui
        Tokenizer.origin = ''.join(origin.split())
        position= 0
        actual= None

    def selectNext():
        #Pega o próximo token, dá um pop dele

        #curto-circuitar em EOF?
        if Tokenizer.position == len(Tokenizer.origin):
            #actual= Token('EOF', None)
            #return actual
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

            Tokenizer.actual= Token('NUMERIC', char)

        elif char == '+':
            #plus
            Tokenizer.position+=1
            Tokenizer.actual= Token('PLUS', char)

        elif char == '-':
            #minus
            Tokenizer.position+=1
            Tokenizer.actual= Token('MINUS', char)
        else:
            raise Exception('Unexpected character \"'+char+'\" at position '+str(Tokenizer.position)+", line:\n"+Tokenizer.origin)
        return Tokenizer.actual

class Parser:
    #Para cada estado, fazer um set de estados válidos seguintes
    states={
        'INIT': set(['NUMERIC']),
        'NUMERIC': set(['PLUS', 'MINUS', 'EOF']),
        'PLUS': set(['NUMERIC']),
        'MINUS': set(['NUMERIC']),
        'EOF': set([])
    }

    #salvar o estado atual
    current= None

    tokens= Tokenizer

    res=0
    op= 1 #1 soma, -1 subtração

    def run(code):
        Parser.current= 'INIT'
        Parser.tokens.init(code)

        Parser.parseExpression()

        return Parser.res

    def parseExpression():
        while(Parser.tokens.selectNext()):
            t= Parser.tokens.actual
            if t.type not in Parser.states[Parser.current]:
                raise Exception('Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: "+str(Parser.states[Parser.current]))

            #agir de acordo com o tipo do token
            if  t.type == 'NUMERIC':
                Parser.res+= Parser.op*int(t.value)

            if t.type == 'PLUS':
                Parser.op= 1
            if t.type == 'MINUS':
                Parser.op= -1

            #atualizar o estado
            Parser.current= t.type

        #EOF

#testes
#s= "1+2"
#s= "3-2"
#s= "1+2-3"
#s= "11+22-33"
s= "789 +345 - 123"
print( Parser.run(s) )
