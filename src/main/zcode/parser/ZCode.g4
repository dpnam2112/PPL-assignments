/**
 * Student's name: Do Phuong Nam
 * Student's ID: 2114111
 **/

grammar ZCode;

@lexer::header {
from lexererr import *
import re
}

options {
	language=Python3;
}

program: (funcDecl | COMMENT_EOF | nlList)* EOF;

// newline list
nlList: NEWLINE+ ;

stmtList
    : (stmt | nlList)+ ;

stmt
    : callStmt
    | assignmentStmt
    | blockStmt
    | ifStmt
    | returnStmt
    | forStmt
    | loopCtrlStmt
    | variableDecl
    ;

callStmt : functionCall NEWLINE ;

returnStmt : RETURN expr? NEWLINE ;

arrayDim : '[' NUM_LIT (',' NUM_LIT)* ']' ;

index : '[' exprList ']' ;

assignmentStmt : ID index? ASSIGN expr NEWLINE ;

forStmt : 'for' ID 'until' expr 'by' expr nlList? stmt ;

variableDecl 
    : (BOOL | STRING | NUMBER) ID arrayDim? (ASSIGN expr)? NEWLINE
    | DYNAMIC ID (ASSIGN expr)? NEWLINE
    | VAR ID ASSIGN expr NEWLINE ;

// Function declaration
funcDecl 
: 'func' ID '(' paramListDecl? ')'
    ( blockStmt | returnStmt | NEWLINE+ (blockStmt | returnStmt)?);

paramListDecl
    : paramDecl (',' paramDecl)* ;

paramDecl
    : (BOOL | NUMBER | STRING) ID arrayDim? ;

ifStmt 
    :   'if' '(' expr ')' nlList? stmt (nlList? elsePart)? ;

elsePart
    : 'else' nlList? stmt
    | 'elif' '(' expr ')' nlList? stmt (nlList? elsePart)? ;

loopCtrlStmt : (BREAK | CONTINUE) NEWLINE ;

blockStmt :
BEGIN NEWLINE
    stmtList?
END NEWLINE;

primary
    : STR_LIT
    | array
    | NUM_LIT
    | ID
    | TRUE
    | FALSE
    | functionCall
    | '(' expr ')' ;

exprList
    : expr (',' expr)* ;

functionCall: ID '(' exprList? ')' ;

array
	: '[' exprList? ']' ;

literalList
     : (NUM_LIT | STR_LIT | TRUE | FALSE | array) (',' (NUM_LIT | STR_LIT | TRUE | FALSE | array))*
     ;

indexExpr
    : primary
    | indexExpr '[' exprList ']' ;

signExpr
    : indexExpr
    | MINUS indexExpr ;

negationExpr
    : signExpr
    | NOT negationExpr ;

termExpr
    : negationExpr
    | termExpr (STAR | SLASH | PERCENT) negationExpr ;

additionExpr
    : termExpr
    | additionExpr (PLUS | MINUS) termExpr ;

boolExpr
    : additionExpr
    | boolExpr (AND | OR) additionExpr ;

relationalExpr
    : boolExpr
    | boolExpr (EQ | NOT_EQ | GT | LT | GT_EQ | LT_EQ | EQ_EQ) boolExpr ;

expr
    : relationalExpr
    | relationalExpr TRIP_DOT relationalExpr ;
 
// Single character tokens

EQ : '=' ;
COMMA : ',' ;
PLUS: '+' ;
MINUS: '-' ;
STAR : '*' ;
SLASH: '/' ;
LPAREN : '(' ;
RPAREN : ')' ;
LBRACK : '[' ;
RBRACK : ']' ;
PERCENT: '%' ;
GT: '>' ;
LT: '<' ;

// Multiple character token

LT_EQ: '<=' ;
GT_EQ: '>=' ;
EQ_EQ: '==' ;
NOT_EQ: '!=' ;
ASSIGN: '<-' ;
TRIP_DOT: '...' ;

// Keywords

BREAK: 'break' ;
BEGIN: 'begin' ;
END: 'end' ;
FUNC: 'func' ;
RETURN: 'return' ;
UNTIL: 'until' ;
IF: 'if' ;
ELIF: 'elif' ;
ELSE: 'else' ;
CONTINUE: 'continue' ;
AND : 'and' ;
OR : 'or' ;
NOT : 'not' ;
TRUE: 'true' ;
FALSE: 'false' ;
VAR: 'var' ;
DYNAMIC: 'dynamic' ;
NUMBER: 'number' ;
BOOL: 'bool' ;
STRING: 'string' ;
FOR: 'for' ;
BY: 'by' ;

fragment
NEWLINE_CHAR: '\r'? '\n' ;

NEWLINE
 : '##'(~[\n])*? ('\r'? '\n') {self.text = self.text[-1] }
 | ('\r'? '\n') ;

fragment
DIGIT: [0-9] ;

fragment
DIGITS: DIGIT+ ;

fragment
SCI_NOTATION: [eE] [+-]? DIGITS ;   // Scientific notation

fragment
DECIMAL_PART :  '.' DIGITS? ;

NUM_LIT : DIGITS DECIMAL_PART? SCI_NOTATION? ;

COMMENT_EOF : '##' (~[\n])*? EOF -> skip ;

fragment
ESCAPE_SEQ: '\\' [\\frtnb'] | '\'"' ;

STR_LIT 
	: '"' (ESCAPE_SEQ | ~[\r\n\\"] )*? '"' 
    { self.text = self.text[1:-1] };

INVALID_ESC 
	: '"' (ESCAPE_SEQ | ~[\r\n\\"])* ('\\' ~[\\frtnb'] | '\\' EOF) 
{ 
content = self.text[1:]
raise IllegalEscape(content)
};

UNCLOSED_STR : '"' ('\\' [\\frtnb'] | '\'"' | ~['"\\])*? ('\n' | EOF) {
content = self.text
content = content[1:] if content[-1] != '\n' else content[1:-1]
raise UncloseString(content)
};   // unclosed string


ID: [a-zA-Z_][a-zA-Z_0-9]* ;

WS: [ \t\r\f]+ -> skip ;

UNRECOGNIZED_CHAR: .  {
raise ErrorToken(self.text[-1])
} ; 
