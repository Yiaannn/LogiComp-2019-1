import re

# quebrar em dois tipos de token, números e stacks de operadores
#única coisa que me falha fora token que não eprtence aos dois grupos é um número seguido de outro número sem operador (ex: "2 4")

def arithimize(line):
    result= 0

    re_ops= re.compile(r"^\s*[-,+]*")
    re_num= re.compile(r"^\s*[0-9]*")

    inverter= 1 #1 quando positivo, -1, quando negativo

    line="0"+line #simplifica algumas presunções
    while True:
        num= re_num.search(line).group()
        if not num:
            print("Erro ao evaluar a expressão")
            break;
        result+= int(num)*inverter
        line=re_num.split(line)[-1]
        print(line)

        if not line:
            break;

        ops= re_ops.search(line).group()
        if not ops:
            print("Erro ao evaluar a expressão")
            break;
        #calcular o inverter
        inverter= 1
        if ops.count('-')%2 == 1:
            inverter= -1
        line=re_ops.split(line)[-1]
        print(line)

    return result
'''
r= arithimize("1+2")
print("Teste 1: "+str(r))

r= arithimize("3-2")
print("Teste 2: "+str(r))

r= arithimize("1+2-3")
print("Teste 3: "+str(r))

r= arithimize("11+22-33")
print("Teste 4: "+str(r))

r= arithimize("789  +345  -   123")
print("Teste 5: "+str(r))
'''
