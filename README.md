# LogiComp-2019-1
Repositório referente a disciplina de Lógica da Computação do aluno Alexandre Young

## Compilador - Etapa 2.2

***

### Diagrama Sintático

![Expressão](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h6/expression.png?raw=true)
![Expressão Relacional](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h6/relexpr.png?raw=true)
![Termo](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h6/term.png?raw=true)
![Fator](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h6/factor.png?raw=true)
![Comandos](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h6/statements.png?raw=true)
![Comando](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h6/statement.png?raw=true)

### EBNF

```
Expressão= Termo, {('+'|'-'|'or'), Termo} ;
Expressão Relacional= Expressão, ('<'|'>'|'=') Expressão ;
Termo= Fator, {('*'|'/'), Fator} ;
Fator= ('+'|'-'|'not'), Fator | número | identificador | '(', Expressão ')' | input ;
Comandos= Comando, '\n', {Comando, '\n'} ;
Comando= 'if', Expressão Relacional, 'then', '\n', Comandos, ( __vazio__ | 'else', '\n', Comandos) , 'end', 'if', '\n' | 'while', Expressão Relacional, Comandos, 'wend', '\n' | identificador, '=', Expressão | 'PRINT', Expressão | __vazio__ ;

identificador= [a-z], {[a-z] | [0-9] | '_'} ;
número= [0-9] ;
```
