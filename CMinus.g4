// CMinus.g4 - Grammar for C-Minus language (Lexer only)
lexer grammar CMinus;

// Keywords
IF       : 'if';
ELSE     : 'else';
VOID     : 'void';
INT      : 'int';
REPEAT   : 'repeat';
BREAK    : 'break';
UNTIL    : 'until';
RETURN   : 'return';

// Symbols
SEMI     : ';';
COMMA    : ',';
LBRACK   : '[';
RBRACK   : ']';
LPAREN   : '(';
RPAREN   : ')';
LBRACE   : '{';
RBRACE   : '}';
PLUS     : '+';
MINUS    : '-';
MULT     : '*';
ASSIGN   : '=';
EQ       : '==';
LT       : '<';
DIV      : '/';

// Comments
COMMENT  : '/*' .*? '*/' -> skip;

// Whitespace
WS       : [ \t\r\n\v\f]+ -> skip;

// Identifiers and numbers
ID       : [A-Za-z][A-Za-z0-9]*;
NUM      : [0-9]+;

// Error handling
UNMATCHED_COMMENT : '*/' {print("Unmatched comment")} -> skip;
INVALID           : . ;
