# LogiComp-2019-1
Repositório referente a disciplina de Lógica da Computação do aluno Alexandre Young

## Compilador - Etapa 2.1

***

### Diagrama Sintático

![Expressão](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h5/expression.png?raw=true)
![Termo](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h5/term.png?raw=true)
![Fator](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h5/factor.png?raw=true)
![Comandos](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h5/statements.png?raw=true)
![Comando](https://github.com/Yiaannn/LogiComp-2019-1/blob/master/res/h5/statement.png?raw=true)

### EBNF

Expressão= Termo, {('+'|'-'), Termo} ;
Termo= Fator, {('\*'|'/'), Fator} ;
Fator= ('+'|'-'), Fator | número | identificador | '(', Expressão ')' ;
Comandos= 'BEGIN', '\n', Comando, '\n', {Comando, '\n'}, 'END' ;
Comando= Comandos | identificador, '=', Expressão | 'PRINT' Expressão | __vazio__ ;

identificador= [a-z], {[a-z] | [0-9] | '\_'} ;
número= [0-9] ;
