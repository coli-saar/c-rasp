grammar crasp;


program
    : NL* statement (NL+ statement)* NL* EOF
    ;

statement: 
    VARIABLE ASSIGN (bool_expr | count_expr)
    | CSTAR
    | IMPORT VARIABLE
    ;


bool_expr:
    STRING_LITERAL
    | count_expr LT count_expr
    | count_expr GT count_expr
    | count_expr EQ count_expr
    | count_expr NEQ count_expr
    | count_expr LEQ count_expr
    | count_expr GEQ count_expr
    | bool_expr AND bool_expr
    | bool_expr OR bool_expr
    | NOT bool_expr
    | TRUE
    | FALSE
    | VARIABLE
    | LPAREN bool_expr RPAREN
    ;
    
count_expr:
    COUNT bool_expr
    | COUNT '[' VARIABLE ']' bool_expr
    | COUNT '[' match_expr ']' bool_expr?
    | COUNT '[' match_bound COMMA match_expr ']' bool_expr?
    | VARIABLE
    | INT_LITERAL
    | count_expr PLUS count_expr
    | count_expr MINUS count_expr
    | INT_LITERAL TIMES count_expr
    | MAX LPAREN count_expr COMMA count_expr RPAREN
    | MIN LPAREN count_expr COMMA count_expr RPAREN
    | match_expr
    | count_expr IF bool_expr ELSE count_expr // low precedence
    | LPAREN count_expr RPAREN
    ;

match_bound
    : VARIABLE (LT | LEQ) VARIABLE
    ;

match_expr
    : MATCH LPAREN NL* match_constraints NL* RPAREN
    ;
match_constraints
    : '[' NL* (offset_list (COMMA NL* offset_list)*)? NL* ']'
    ;

offset_list
    : LPAREN NL* signed_integer COMMA NL* signed_integer COMMA NL* signed_integer NL* RPAREN
    ;

signed_integer
    : MINUS? INT_LITERAL
    ;
    



////////////////////////////////////////////////

// starts comments
LINE_COMMENT: '//' ~[\r\n]* -> skip;

// define keywords before variables
CSTAR: '#cstar';
IMPORT: '#import';
TRUE : 'true';
FALSE: 'false';
IF: 'if';
ELSE: 'else';
MIN: 'min';
MAX: 'max';
MATCH: 'match';


VARIABLE: [a-zA-Z_][a-zA-Z_0-9]*;
STRING_LITERAL: '"' (~["])* '"';
INT_LITERAL : [0-9]+ ;


AND : '&&' ;
OR : '||';
NOT : '!' ;

EQ : '==' ;
NEQ : '!=' ;
LT : '<';
GT: '>';
LEQ: '<=';
GEQ: '>=';

ASSIGN: '=';
QUESTION: '?';
COLON: ':';
PLUS: '+';
MINUS: '-';
TIMES: '*';

COUNT : '#';

LPAREN : '(' ;
RPAREN : ')' ;
COMMA : ',';

NL
    : ('\r'? '\n')+
    ;

WS: [ \t]+ -> skip ;
