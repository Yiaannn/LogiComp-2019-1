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
        else:
            raise Exception('Error: Unexpected character \"'+char+'\" at position '+str(Tokenizer.position)+", line:\n"+Tokenizer.origin)
        return Tokenizer.actual

class PrePro:

    def run(code):
        comment= False;
        sanitized= ""

        #poderia incluir caracter de escape, mas acho que a especificação não pede
        for char in code:

            #do exemplo não ficou completamente claro pra mim se o delimitador do comentário é o próprio ' ou uma quebra de linha
            #assumindo quebra de linha:

            if char == "\'" and not comment:
                comment= True

            if not comment:
                sanitized+= char

            if char == "\n" and comment:
                comment= False

        #limpar o whitespace aqui
        sanitized = ''.join(sanitized.split())

        return sanitized

class Parser:

    #Para cada estado, fazer um set de estados válidos seguintes
    states={
        'INIT': set(['NUMERIC']),
        'NUMERIC': set(['PLUS', 'MINUS', 'MULT', 'DIV', 'EOF']),
        'PLUS': set(['NUMERIC']),
        'MINUS': set(['NUMERIC']),
        'MULT': set(['NUMERIC']),
        'DIV': set(['NUMERIC']),
        'EOF': set([])
    }

    def run(code):
        Tokenizer.init(code)
        return Parser.parseExpression().value

    def parseExpression(state='INIT'):
        res= None #onde eu vou guardar a resolução da minha expressão
        op= None#guarda a operação a ser executada

        resolved_token= None #expressão reduzida em um token, usado em recursão

        while(resolved_token or Tokenizer.selectNext()):
            t= resolved_token
            resolved_token= None
            if not t:
                t= Tokenizer.actual

            #TODO: Confirmar porque não travo em string vazia
            if t.type not in Parser.states[state]:
                raise Exception('Error: Unexpected word \"'+t.value+"\" of type \""+t.type+"\", expected: "+str(Parser.states[state]))

            #agir de acordo com o tipo do token
            if  t.type == 'NUMERIC':

                if not res:
                    res= t.value
                else:
                    if op == 'PLUS':
                        res+= t.value

                    elif op == 'MINUS':
                        res-= t.value

                    elif op == 'MULT':
                        res*= t.value

                    elif op == 'DIV':
                        res//= t.value

            op= t.type
            if t.type == 'PLUS' or t.type == "MINUS":
                #Entrar num novo escopo
                resolved_token= Parser.parseExpression()

            #atualizar o estado
            state= t.type

        #checar se nao cheguei em EOF cedo demais
        if 'EOF' not in Parser.states[state]:
            raise Exception('Error: Rached EOF before finishing Expression')

        return Token('NUMERIC', res)

sanit= PrePro.run( input("Input teste: ") )
print( Parser.run( sanit ) )
