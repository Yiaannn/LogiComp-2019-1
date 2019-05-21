# LogiComp-2019-1
Repositório referente a disciplina de Lógica da Computação do aluno Alexandre Young

## Compilador - Etapa 2.2

***

### Diagrama Sintático

![Programa](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/program.png?raw=true)
![Expressão](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/expression.png?raw=true)
![Expressão Relacional](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/relexpr.png?raw=true)
![Termo](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/term.png?raw=true)
![Fator](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/factor.png?raw=true)
![Comandos](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/statements.png?raw=true)
![Comando](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/statement.png?raw=true)
![Tipo](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h7/type.png?raw=true)

### EBNF

```
Programa= 'sub', 'main', '(', ')', '\n', Comandos, 'end', 'sub' ;
Expressão= Termo, {('+'|'-'|'or'), Termo} ;
Expressão Relacional= Expressão, ('<'|'>'|'=') Expressão ;
Termo= Fator, {('*'|'/'), Fator} ;
Fator= ('+'|'-'|'not'), Fator | número | identificador | '(', Expressão ')' | input | 'true' | 'false' ;
Comandos= Comando, '\n', {Comando, '\n'} ;
Comando= 'if', Expressão Relacional, 'then', '\n', Comandos, ( __vazio__ | 'else', '\n', Comandos) , 'end', 'if', '\n' | 'while', Expressão Relacional, Comandos, 'wend', '\n' | identificador, '=', Expressão | 'PRINT', Expressão | 'dim', identificador, 'as', Tipo | __vazio__ ;
Tipo= 'integer' | 'boolean'

identificador= [a-z], {[a-z] | [0-9] | '_'} ;
número= [0-9] ;
```
