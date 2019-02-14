from ply import lex
from ply.lex import TOKEN
import ply.yacc as yacc
import json
import argparse
import sys

"""
CITE:
  Most of the token definations are taken from documentation
  of golang(go docs), and some from the token (go/token)
  package of golang: https://golang.org/src/go/token/token.go
"""

# reserved words in language
reserved = {
    'break':    'BREAK',
    'default':    'DEFAULT',
    'select':    'SELECT',
    'func':    'FUNC',
    'case':    'CASE',
    'interface':    'INTERFACE',
    'defer':    'DEFER',
    'go':    'GO',
    'struct':    'STRUCT',
    'goto':    'GOTO',
    'chan':    'CHAN',
    'else':    'ELSE',
    'map':    'MAP',
    'fallthrough':    'FALLTHROUGH',
    'package':    'PACKAGE',
    'switch':    'SWITCH',
    'const':    'CONST',
    'range':    'RANGE',
    'type':    'TYPE',
    'if':    'IF',
    'continue':    'CONTINUE',
    'return':    'RETURN',
    'for':    'FOR',
    'import':    'IMPORT',
    'var':    'VAR',
}


# token list (compulsary)
tokens = [
    # literals
    'IDENT',            # main
    'INT',              # 123
    'FLOAT',            # 123.4
    'IMAG',             # 123.4i
    'CHAR',             # 'a'
    'STRING',           # "abc"

    # operator
    'ADD',              # +
    'SUB',              # -
    'MUL',              # *
    'QUO',              # /
    'REM',              # %

    'ADD_ASSIGN',       # +=
    'SUB_ASSIGN',       # -=
    'MUL_ASSIGN',       # *=
    'QUO_ASSIGN',       # %=
    'REM_ASSIGN',       # %=

    # bitwise operators
    'AND',              # &
    'OR',               # |
    'XOR',              # ^
    'SHL',              # <<
    'SHR',              # >>
    'AND_NOT',          # &^

    'AND_ASSIGN',       # &=
    'OR_ASSIGN',        # |=
    'XOR_ASSIGN',       # ^=
    'SHL_ASSIGN',       # <<=
    'SHR_ASSIGN',       # >>=
    'AND_NOT_ASSIGN',   # &^=

    'LAND',             # &&
    'LOR',              # ||
    'ARROW',            # <-
    'INC',              # ++
    'DEC',              # --

    'EQL',              # ==
    'LSS',              # <
    'GTR',              # >
    'ASSIGN',           # =
    'NOT',              # !

    'NEQ',              # !=
    'LEQ',              # <=
    'GEQ',              # >=
    'DEFINE',           # :=
    'ELLIPSIS',         # ...

    'LPAREN',           # (
    'LBRACK',           # [
    'LBRACE',           # {
    'COMMA',            # ,
    'PERIOD',           # .

    'RPAREN',           # )
    'RBRACK',           # ]
    'RBRACE',           # }
    'SEMICOLON',        # ;
    'COLON',            # :

] + list(reserved.values())

# Mathematical operators
t_ADD = r"\+"
t_SUB = r"-"
t_MUL = r"\*"
t_QUO = r"/"
t_REM = r"%"

t_ADD_ASSIGN = r"\+="
t_SUB_ASSIGN = r"-="
t_MUL_ASSIGN = r"\*="
t_QUO_ASSIGN = r"/="
t_REM_ASSIGN = r"%="

# bitwise operators
t_AND = r"&"
t_OR = r"\|"
t_XOR = r"\^"
t_SHL = r"<<"
t_SHR = r">>"
t_AND_NOT = r"&\^"

AND_ASSIGN = r"&="
OR_ASSIGN = r"!="
XOR_ASSIGN = r"\^="
SHL_ASSIGN = r"<<="
SHR_ASSIGN = r">>="
AND_NOT_ASSIGN = r"&\^="

t_LAND = r"&&"
t_LOR = r"\|\|"
t_ARROW = r"<-"
t_INC = r"\+\+"
t_DEC = r"--"

t_EQL = r"=="
t_LSS = r"<"
t_GTR = r">"
t_ASSIGN = r"="
t_NOT = "!"

t_NEQ = r"!="
t_LEQ = r"<="
t_GEQ = r">="
t_DEFINE = r":="
t_ELLIPSIS = r"\.\.\."

t_LPAREN = r"\("
t_LBRACK = r"\["
t_LBRACE = r"\{"
t_COMMA = r","
t_PERIOD = r"\."

t_RPAREN = r"\)"
t_RBRACK = r"\]"
t_RBRACE = r"\}"
t_SEMICOLON = r";"
t_COLON = r":"

letter = r"[_A-Za-z]"
decimal_digit = r"[0-9]"
octal_digit = r"[0-7]"
hexa_digit = r"[0-9a-fA-F]"

identifier = letter + r"(" + letter + r"|" + decimal_digit + r")*"

octal_literal = r"0[0-7]*"
hexa_literal = r"0[xX][0-9a-fA-F]+"
decimal_literal = r"[1-9][0-9]*"
t_INT = decimal_literal + r"|" + octal_literal + r"|" + hexa_literal

decimals = decimal_digit + r"(" + decimal_digit + r")*"
exponent = r"(e|E)" + r"(\+|-)?" + decimals
t_FLOAT = r"(" + decimals + r"\." + decimals + exponent + r")|(" + \
    decimals + exponent + r")|(" + r"\." + decimals + exponent + r")"

t_IMAG = r"(" + decimals + r"|" + t_FLOAT + r")" + r"i"

t_ignore = " \t"

# t_STRING = r"\"[.]+\""
ctr = 1
# Definig functions for each token


@TOKEN(identifier)
def t_IDENT(t):
    t.type = reserved.get(t.value, "IDENT")
    return t


def t_NL(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    pass


def t_COMMENT(t):
    r"(//.*)|(/\*(.|\n)*?)\*/"
    pass


def t_STRING(t):
    r"(\"(.|\n)*?)\""
    return t


def t_error(t):
    print("[ERROR] Invalid token:", t.value[0])
    t.lexer.skip(1)  # skip ahead 1 character


myout = ""


class Node:
    def __init__(self, leaf=None, children=None):
        if children:
            self.children = children
        else:
            self.children = None
        self.leaf = leaf


def gendot(x, parent):
    global myout
    global ctr

    if x.children == None:
        return
    for i in x.children:
        if i == None:
            continue
        myout += str(ctr) + ' [label="' + i.leaf + '"];\n'
        myout += str(parent) + ' -> ' + str(ctr) + ';\n'
        ctr += 1
        gendot(i, ctr - 1)


precedence = (
    ('right', 'ASSIGN', 'NOT'),
    ('left', 'LOR'),
    ('left', 'LAND'),
    ('left', 'OR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'EQL', 'NEQ'),
    ('left', 'LSS', 'GTR', 'LEQ', 'GEQ'),
    ('left', 'SHL', 'SHR'),
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'QUO', 'REM'),
)

# ------------------------START----------------------------


def p_start(p):
    '''start : SourceFile'''
    p[0] = Node("Start", [p[1]])
# -------------------------------------------------------


# -----------------------TYPES---------------------------
def p_type(p):
    '''Type : TypeName
                    | TypeLit
                    | LPAREN Type RPAREN'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_type_name(p):
    '''TypeName : TypeToken
                            | QualifiedIdent'''
    p[0] = p[1]


def p_type_token(p):
    '''TypeToken : INT
                             | FLOAT
                             | IMAG
                             | STRING
                             | TYPE IDENT'''
    if len(p) == 2:
        p[0] = Node(p[1])
    else:
        p[1] = Node(p[1])
        p[2] = Node(p[2])
        p[0] = Node("", [p[1], p[2]])


def p_type_lit(p):
    '''TypeLit : ArrayType
                       | StructType
                       | PointerType'''
    p[0] = p[1]


def p_type_opt(p):
    '''TypeOpt : Type
                       | epsilon'''
    p[0] = Node("", [p[1]])
# -------------------------------------------------------


# ------------------- ARRAY TYPE -------------------------
def p_array_type(p):
    '''ArrayType : LBRACK ArrayLength RBRACK ElementType'''
    p[0] = Node("", "[", p[2], "]", p[4])


def p_array_length(p):
    ''' ArrayLength : Expression '''
    p[0] = Node("", [p[1]])


def p_element_type(p):
    ''' ElementType : Type '''
    p[0] = Node("", [p[1]])

# --------------------------------------------------------


# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
    '''StructType : STRUCT LBRACE FieldDeclRep RBRACE'''
    p[0] = Node("", "struct", "{", p[3], "}"]


def p_field_decl_rep(p):
    ''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
                                    | epsilon '''
    if len(p) == 4:
        p[0] = Node("", p[1], p[2], ";"]
    else:
        p[0] = Node("", [p[1]])


def p_field_decl(p):
    ''' FieldDecl : IdentifierList Type TagOpt'''
    p[0] = Node("", p[1], p[2], p[3])


def p_TagOpt(p):
    ''' TagOpt : Tag
                           | epsilon '''
    p[0] = Node("", [p[1]])


def p_Tag(p):
    ''' Tag : STRING '''
    p[0] = Node("", [p[1]])
# ---------------------------------------------------------


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
    '''PointerType : MUL BaseType'''
    p[0] = Node("", "*", p[2])


def p_base_type(p):
    '''BaseType : Type'''
    p[0] = Node("", [p[1]])
# ---------------------------------------------------------


# ---------------FUNCTION TYPES----------------------------
def p_sign(p):
    '''Signature : Parameters ResultOpt'''
    p[0] = Node("", p[1], p[2])


def p_result_opt(p):
    '''ResultOpt : Result
                             | epsilon'''
    p[0] = Node("", [p[1]])


def p_result(p):
    '''Result : Parameters
                      | Type'''
    p[0] = Node("", [p[1]])


def p_params(p):
    '''Parameters : LPAREN ParameterListOpt RPAREN'''
    p[0] = Node("", "(", p[2], ")"]


def p_param_list_opt(p):
    '''ParameterListOpt : ParametersList
                                                     | epsilon'''
    p[0] = Node("", [p[1]])


def p_param_list(p):
    '''ParametersList : Type
                                      | IdentifierList Type
                                      | ParameterDeclCommaRep'''
    if len(p) == 3:
        p[0] = Node("", p[1], p[2])
    else:
        p[0] = Node("", [p[1]])


def p_param_decl_comma_rep(p):
    '''ParameterDeclCommaRep : ParameterDeclCommaRep COMMA ParameterDecl
                                                     | ParameterDecl COMMA ParameterDecl'''
    p[0] = Node("", p[1], ",", p[3])


def p_param_decl(p):
    '''ParameterDecl : IdentifierList Type
                                     | Type'''
    if len(p) == 3:
        p[0] = Node("", p[1], p[2])
    else:
        p[0] = Node("", [p[1]])
# ---------------------------------------------------------


# -----------------------BLOCKS---------------------------
def p_block(p):
    '''Block : LBRACE StatementList RBRACE'''
    p[0] = Node("", "{", p[2], "}"]


def p_stat_list(p):
    '''StatementList : StatementRep'''
    p[0] = Node("", [p[1]])


def p_stat_rep(p):
    '''StatementRep : StatementRep Statement SEMICOLON
                                    | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], p[2], ';']
    else:
        p[0] = Node("", [p[1]])
# -------------------------------------------------------


# ------------------DECLARATIONS and SCOPE------------------------
def p_decl(p):
    '''Declaration : ConstDecl
                                   | TypeDecl
                                   | VarDecl'''
    p[0] = Node("", [p[1]])


def p_toplevel_decl(p):
    '''TopLevelDecl : Declaration
                                    | FunctionDecl'''
    p[0] = Node("", [p[1]])
# -------------------------------------------------------


# ------------------CONSTANT DECLARATIONS----------------
def p_const_decl(p):
    '''ConstDecl : CONST ConstSpec
                             | CONST LPAREN ConstSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = Node("", "const", p[2])
    else:
        p[0] = Node("", "const", '(', p[3], ')']


def p_const_spec_rep(p):
    '''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
                                    | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], p[2], ';']
    else:
        p[0] = Node("", [p[1]])


def p_const_spec(p):
    '''ConstSpec : IdentifierList TypeExprListOpt'''
    p[0] = Node("", p[1], p[2])


def p_type_expr_list(p):
    '''TypeExprListOpt : TypeOpt ASSIGN ExpressionList
                                       | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], "=", p[3])
    else:
        p[0] = Node("", [p[1]])


def p_identifier_list(p):
    '''IdentifierList : IDENT IdentifierRep'''
    p[0] = Node("", p[1], p[2])


def p_identifier_rep(p):
    '''IdentifierRep : IdentifierRep COMMA IDENT
                                     | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], ",", p[3])
    else:
        p[0] = Node("", [p[1]])


def p_expr_list(p):
    '''ExpressionList : Expression ExpressionRep'''
    p[0] = Node("", p[1], p[2])


def p_expr_rep(p):
    '''ExpressionRep : ExpressionRep COMMA Expression
                                     | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], ',', p[3])
    else:
        p[0] = Node("", [p[1]])
# -------------------------------------------------------


# ------------------TYPE DECLARATIONS-------------------
def p_type_decl(p):
    '''TypeDecl : TYPE TypeSpec
                            | TYPE LPAREN TypeSpecRep RPAREN'''
    if len(p) == 5:
        p[0] = Node("", "type", "(", p[3], ")"]
    else:
        p[0] = Node("", "type", p[2])


def p_type_spec_rep(p):
    '''TypeSpecRep : TypeSpecRep TypeSpec SEMICOLON
                               | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], p[2], ";"]
    else:
        p[0] = Node("", [p[1]])


def p_type_spec(p):
    '''TypeSpec : AliasDecl
                            | TypeDef'''
    p[0] = Node("", [p[1]])


def p_alias_decl(p):
    '''AliasDecl : IDENT ASSIGN Type'''
    p[0] = Node("", p[1], '=', p[3])
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
    '''TypeDef : IDENT Type'''
    p[0] = Node("", p[1], p[2])
# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
    '''VarDecl : VAR VarSpec
                       | VAR LPAREN VarSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = Node("", "var", p[2])
    else:
        p[0] = Node("", "var", "(", p[3], ")"]


def p_var_spec_rep(p):
    '''VarSpecRep : VarSpecRep VarSpec SEMICOLON
                              | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], p[2], ";"]
    else:
        p[0] = Node("", [p[1]])


def p_var_spec(p):
    '''VarSpec : IdentifierList Type ExpressionListOpt
                       | IdentifierList ASSIGN ExpressionList'''
    if p[2] == '=':
        p[0] = Node("", p[1], "=", p[3])
    else:
        p[0] = Node("", p[1], p[2], p[3])


def p_expr_list_opt(p):
    '''ExpressionListOpt : ASSIGN ExpressionList
                                             | epsilon'''
    if len(p) == 3:
        p[0] = Node("", "=", p[2])
    else:
        p[0] = Node("", [p[1]])
# -------------------------------------------------------


# ----------------SHORT VARIABLE DECLARATIONS-------------
def p_short_var_decl(p):
    ''' ShortVarDecl : IDENT DEFINE Expression '''
    p[0] = Node("", p[1], ":=", p[3])
# -------------------------------------------------------


# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
    '''FunctionDecl : FUNC FunctionName Function
                                    | FUNC FunctionName Signature'''
    p[0] = Node("", "func", p[2], p[3])


def p_func_name(p):
    '''FunctionName : IDENT'''
    p[0] = Node("", [p[1]])


def p_func(p):
    '''Function : Signature FunctionBody'''
    p[0] = Node("", p[1], p[2])


def p_func_body(p):
    '''FunctionBody : Block'''
    p[0] = Node("", [p[1]])
# -------------------------------------------------------


# ----------------------OPERAND----------------------------
def p_operand(p):
    '''Operand : Literal
                       | OperandName
                       | LPAREN Expression RPAREN'''
    if len(p) == 2:
        p[0] = Node("", [p[1]])
    else:
        p[0] = Node("", "(", p[2], ")"]


def p_literal(p):
    '''Literal : BasicLit'''
    # | CompositeLit'''
    p[0] = Node("", [p[1]])


def p_basic_lit(p):
    '''BasicLit : INT
                            | FLOAT
                            | STRING
                            '''
    p[0] = Node("", str([p[1]])]


def p_operand_name(p):
    '''OperandName : IDENT'''
    p[0] = Node("", [p[1]])
# ---------------------------------------------------------


# -------------------QUALIFIED IDENT----------------
def p_quali_ident(p):
    '''QualifiedIdent : IDENT PERIOD TypeName'''
    p[0] = Node("", p[1], ".", p[3])
# -------------------------------------------------------


# -----------------COMPOSITE LITERALS----------------------
def p_comp_lit(p):
    '''CompositeLit : LiteralType LiteralValue'''
    p[0] = Node("", p[1], p[2])


def p_lit_type(p):
    '''LiteralType : ArrayType
                               | ElementType
                               | TypeName'''
    p[0] = Node("", [p[1]])


def p_lit_val(p):
    '''LiteralValue : LBRACE ElementListOpt RBRACE'''
    p[0] = Node("", "{", p[2], "}"]


def p_elem_list_comma_opt(p):
    '''ElementListOpt : ElementList
                                               | epsilon'''
    p[0] = Node("", [p[1]])


def p_elem_list(p):
    '''ElementList : KeyedElement KeyedElementCommaRep'''
    p[0] = Node("", p[1], p[2])


def p_key_elem_comma_rep(p):
    '''KeyedElementCommaRep : KeyedElementCommaRep COMMA KeyedElement
                                                    | epsilon'''
    if len(p) == 4:
        p[0] = Node("", p[1], ",", p[3])
    else:
        p[0] = Node("", [p[1]])


def p_key_elem(p):
    '''KeyedElement : Key COLON Element
                                    | Element'''
    if len(p) == 4:
        p[0] = Node("", p[1], ":", p[3])
    else:
        p[0] = Node("", [p[1]])


def p_key(p):
    '''Key : FieldName
               | Expression
               | LiteralValue'''
    p[0] = Node("", [p[1]])


def p_field_name(p):
    '''FieldName : IDENT'''
    p[0] = Node("", [p[1]])


def p_elem(p):
    '''Element : Expression
                       | LiteralValue'''
    p[0] = Node("", [p[1]])
# ---------------------------------------------------------


# ------------------PRIMARY EXPRESSIONS--------------------
def p_prim_expr(p):
    '''PrimaryExpr : Operand
                               | PrimaryExpr Selector
                               | PrimaryExpr Index
                               | PrimaryExpr Slice
                               | PrimaryExpr TypeAssertion
                               | PrimaryExpr Arguments'''
    if len(p) == 2:
        p[0] = Node("", [p[1]])
    else:
        p[0] = Node("", p[1], p[2])


def p_selector(p):
    '''Selector : PERIOD IDENT'''
    p[0] = Node("", ".", p[2])


def p_index(p):
    '''Index : LBRACK Expression RBRACK'''
    p[0] = Node("", "[", p[2], "]"]


def p_slice(p):
    '''Slice : LBRACK ExpressionOpt COLON ExpressionOpt RBRACK
                     | LBRACK ExpressionOpt COLON Expression COLON Expression RBRACK'''
    if len(p) == 6:
        p[0] = Node("", "[", p[2], ":", p[4], "]"]
    else:
        p[0] = Node("", "[", p[2], ":", p[4], ":", p[6], "]"]


def p_type_assert(p):
    '''TypeAssertion : PERIOD LPAREN Type RPAREN'''
    p[0] = Node("", ".", "(", p[3], ")"]


def p_argument(p):
    '''Arguments : LPAREN ExpressionListTypeOpt RPAREN'''
    p[0] = Node("", "(", p[2], ")"]


def p_expr_list_type_opt(p):
    '''ExpressionListTypeOpt : ExpressionList
                                                     | epsilon'''
    if len(p) == 3:
        p[0] = Node("", p[1], p[2])
    else:
        p[0] = Node("", [p[1]])

# def p_comma_opt(p):
#    '''CommaOpt : COMMA
#                | epsilon'''
#    if p[1] == ",":
#        p[0] = Node("", ","]
#    else:
#        p[0] = Node("", [p[1]])


def p_expr_list_comma_opt(p):
    '''ExpressionListCommaOpt : COMMA ExpressionList
                                                      | epsilon'''
    if len(p) == 3:
        p[0] = Node("", ",", p[2])
    else:
        p[0] = Node("", [p[1]])
# ---------------------------------------------------------


# ----------------------OPERATORS-------------------------
def p_expr(p):
    '''Expression : UnaryExpr
                              | Expression BinaryOp Expression'''
    if len(p) == 4:
        p[0] = Node("", p[1], p[2], p[3])
    else:
        p[0] = Node("", [p[1]])


def p_expr_opt(p):
    '''ExpressionOpt : Expression
                                     | epsilon'''
    p[0] = Node("", [p[1]])


def p_unary_expr(p):
    '''UnaryExpr : PrimaryExpr
                             | UnaryOp UnaryExpr
                             | NOT UnaryExpr'''
    if len(p) == 2:
        p[0] = Node("", [p[1]])
    elif p[1] == "!":
        p[0] = Node("", "!", p[2])
    else:
        p[0] = Node("", p[1], p[2])


def p_binary_op(p):
    '''BinaryOp : LOR
                            | LAND
                            | RelOp
                            | AddMulOp'''
    if p[1] == "||":
        p[0] = Node("", "||"]
    elif p[1] == "&&":
        p[0] = Node("", "&&"]
    else:
        p[0] = Node("", [p[1]])


def p_rel_op(p):
    '''RelOp : EQL
                     | NEQ
                     | LSS
                     | GTR
                     | LEQ
                     | GEQ'''
    if p[1] == "==":
        p[0] = Node("", "=="]
    elif p[1] == "!=":
        p[0] = Node("", "!="]
    elif p[1] == "<":
        p[0] = Node("", "<"]
    elif p[1] == ">":
        p[0] = Node("", ">"]
    elif p[1] == "<=":
        p[0] = Node("", "<="]
    elif p[1] == ">=":
        p[0] = Node("", ">="]


def p_add_mul_op(p):
    '''AddMulOp : UnaryOp
                            | OR
                            | XOR
                            | QUO
                            | REM
                            | SHL
                            | SHR'''
    if p[1] == "/":
        p[0] = Node("", "/"]
    elif p[1] == "%":
        p[0] = Node("", "%"]
    elif p[1] == "|":
        p[0] = Node("", "|"]
    elif p[1] == "^":
        p[0] = Node("", "^"]
    elif p[1] == "<<":
        p[0] = Node("", "<<"]
    elif p[1] == ">>":
        p[0] = Node("", ">>"]
    else:
        p[0] = Node("", [p[1]])


def p_unary_op(p):
    '''UnaryOp : ADD
                       | SUB
                       | MUL
                       | AND '''
    if p[1] == '+':
        p[0] = Node("", "+"]
    elif p[1] == '-':
        p[0] = Node("", "-"]
    elif p[1] == '*':
        p[0] = Node("", "*"]
    elif p[1] == '&':
        p[0] = Node("", "&"]
# -------------------------------------------------------


# -----------------CONVERSIONS-----------------------------
# def p_conversion(p):
#     '''Conversion : TYPECAST Type LPAREN Expression RPAREN'''
#     p[0] = Node("", p[1], p[2],  "(", p[4], ")"]
# ---------------------------------------------------------


# ---------------- STATEMENTS -----------------------
def p_statement(p):
    '''Statement : Declaration
                             | LabeledStmt
                             | SimpleStmt
                             | ReturnStmt
                             | BreakStmt
                             | ContinueStmt
                             | GotoStmt
                             | Block
                             | IfStmt
                             | SwitchStmt
                             | ForStmt '''
    p[0] = Node("", [p[1]])


def p_simple_stmt(p):
    ''' SimpleStmt : epsilon
                                   | ExpressionStmt
                                   | IncDecStmt
                                   | Assignment
                                   | ShortVarDecl '''
    p[0] = Node("", [p[1]])


def p_labeled_statements(p):
    ''' LabeledStmt : Label COLON Statement '''
    p[0] = Node("", p[1], ":", p[3])


def p_label(p):
    ''' Label : IDENT '''
    p[0] = Node("", [p[1]])


def p_expression_stmt(p):
    ''' ExpressionStmt : Expression '''
    p[0] = Node("", [p[1]])


def p_inc_dec(p):
    ''' IncDecStmt : Expression INC
                                   | Expression DEC '''
    if p[2] == '++':
        p[0] = Node("", p[1], "++"]
    else:
        p[0] = Node("", p[1], "--"]


def p_assignment(p):
    ''' Assignment : ExpressionList assign_op ExpressionList'''
    p[0] = Node("", p[1], p[2], p[3])


def p_assign_op(p):
    ''' assign_op : AssignOp'''
    p[0] = Node("", [p[1]])


def p_AssignOp(p):
    ''' AssignOp : ADD_ASSIGN
                             | SUB_ASSIGN
                             | MUL_ASSIGN
                             | QUO_ASSIGN
                             | REM_ASSIGN
                             | AND_ASSIGN
                             | OR_ASSIGN
                             | XOR_ASSIGN
                             | SHL_ASSIGN
                             | SHR_ASSIGN
                             | ASSIGN '''
    p[0] = Node("", [p[1]])


def p_if_statement(p):
    ''' IfStmt : IF Expression Block ElseOpt '''
    p[0] = Node("", "if", p[2], p[3], p[4])


def p_SimpleStmtOpt(p):
    ''' SimpleStmtOpt : SimpleStmt SEMICOLON
                                          | epsilon '''
    if len(p) == 3:
        p[0] = Node("", p[1], ";"]
    else:
        p[0] = Node("", [p[1]])


def p_else_opt(p):
    ''' ElseOpt : ELSE IfStmt
                            | ELSE Block
                            | epsilon '''
    if len(p) == 3:
        p[0] = Node("", "else", p[2])
    else:
        p[0] = Node("", [p[1]])

# ----------------------------------------------------------------


# ----------- SWITCH STATEMENTS ---------------------------------

def p_switch_statement(p):
    ''' SwitchStmt : ExprSwitchStmt
                                   | TypeSwitchStmt '''
    p[0] = Node("", [p[1]])


def p_expr_switch_stmt(p):
    ''' ExprSwitchStmt : SWITCH ExpressionOpt LBRACE ExprCaseClauseRep RBRACE'''
    p[0] = Node("", "switch", p[2], p[3], "{", p[5], "}"]


def p_expr_case_clause_rep(p):
    ''' ExprCaseClauseRep : ExprCaseClauseRep ExprCaseClause
                                                  | epsilon'''
    if len(p) == 3:
        p[0] = Node("", p[1], p[2])
    else:
        p[0] = Node("", [p[1]])


def p_expr_case_clause(p):
    ''' ExprCaseClause : ExprSwitchCase COLON StatementList'''
    p[0] = Node("", p[1], ":", p[3])


def p_expr_switch_case(p):
    ''' ExprSwitchCase : CASE ExpressionList
                                           | DEFAULT '''
    if len(p) == 3:
        p[0] = Node("", "case", p[2])
    else:
        p[0] = Node("", [p[1]])


def p_type_switch_stmt(p):
    ''' TypeSwitchStmt : SWITCH SimpleStmtOpt TypeSwitchGuard LBRACE TypeCaseClauseOpt RBRACE'''
    p[0] = Node("", "switch", p[2], p[3], "{", p[5], "}"]


def p_type_switch_guard(p):
    ''' TypeSwitchGuard : IdentifierOpt PrimaryExpr PERIOD LPAREN TYPE RPAREN '''

    p[0] = Node("", p[1], p[2], ".", "(", "type", ")"]


def p_identifier_opt(p):
    ''' IdentifierOpt : IDENT DEFINE
                                          | epsilon '''

    if len(p) == 3:
        p[0] = Node("", p[1], ":="]
    else:
        p[0] = Node("", [p[1]])


def p_type_case_clause_opt(p):
    ''' TypeCaseClauseOpt : TypeCaseClauseOpt TypeCaseClause
                                                  | epsilon '''
    if len(p) == 3:
        p[0] = Node("", p[1], p[2])
    else:
        p[0] = Node("", [p[1]])


def p_type_case_clause(p):
    ''' TypeCaseClause : TypeSwitchCase COLON StatementList'''
    p[0] = Node("", p[1], ":", p[3])


def p_type_switch_case(p):
    ''' TypeSwitchCase : CASE TypeList
                                           | DEFAULT '''
    if len(p) == 3:
        p[0] = Node("", p[1], p[2])
    else:
        p[0] = Node("", [p[1]])


def p_type_list(p):
    ''' TypeList : Type TypeRep'''
    p[0] = Node("", p[1], p[2])


def p_type_rep(p):
    ''' TypeRep : TypeRep COMMA Type
                            | epsilon '''
    if len(p) == 4:
        p[0] = Node("", p[1], ",", p[3])
    else:
        p[0] = Node("", [p[1]])

# -----------------------------------------------------------


# --------- FOR STATEMENTS AND OTHERS (MANDAL) ---------------
def p_for(p):
    '''ForStmt : FOR ConditionBlockOpt Block'''
    p[0] = Node("", "for", p[2], p[3])


def p_conditionblockopt(p):
    '''ConditionBlockOpt : epsilon
                           | Condition
                           | ForClause
                           | RangeClause'''
    p[0] = Node("", [p[1]])


def p_condition(p):
    '''Condition : Expression '''
    p[0] = Node("", [p[1]])


def p_forclause(p):
    '''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''
    p[0] = Node("", p[1], ";", p[3], ";", p[5])

# def p_initstmtopt(p):
#   '''InitStmtOpt : epsilon
#            | InitStmt '''
#   p[0] = Node("", [p[1]])

# def p_init_stmt(p):
#   ''' InitStmt : SimpleStmt'''
#   p[0] = Node("", [p[1]])


def p_conditionopt(p):
    '''ConditionOpt : epsilon
                    | Condition '''
    p[0] = Node("", [p[1]])

# def p_poststmtopt(p):
#   '''PostStmtOpt : epsilon
#            | PostStmt '''
#   p[0] = Node("", [p[1]])

# def p_post_stmt(p):
#   ''' PostStmt : SimpleStmt '''
#   # p[0] = Node("", [p[1]])


def p_rageclause(p):
    '''RangeClause : ExpressionIdentListOpt RANGE Expression'''
    p[0] = Node("", p[1], "range", p[3])


def p_expression_ident_listopt(p):
    '''ExpressionIdentListOpt : epsilon
                           | ExpressionIdentifier'''
    p[0] = Node("", [p[1]])


def p_expressionidentifier(p):
    '''ExpressionIdentifier : ExpressionList ASSIGN'''
    if p[2] == "=":
        p[0] = Node("", p[1], "="]
    else:
        p[0] = Node("", p[1], ":="]


def p_return(p):
    '''ReturnStmt : RETURN ExpressionListPureOpt'''
    p[0] = Node("", "return", p[2])


def p_expressionlist_pure_opt(p):
    '''ExpressionListPureOpt : ExpressionList
                           | epsilon'''
    p[0] = Node("", [p[1]])


def p_break(p):
    '''BreakStmt : BREAK LabelOpt'''
    p[0] = Node("", "break", p[2])


def p_continue(p):
    '''ContinueStmt : CONTINUE LabelOpt'''
    p[0] = Node("", "continue", p[2])


def p_labelopt(p):
    '''LabelOpt : Label
                  | epsilon '''
    p[0] = Node("", [p[1]])


def p_goto(p):
    '''GotoStmt : GOTO Label '''
    p[0] = Node("", "goto", p[2])
# -----------------------------------------------------------


# ----------------  SOURCE FILE --------------------------------
def p_source_file(p):
    '''SourceFile : PackageClause SEMICOLON ImportDeclRep TopLevelDeclRep'''
    if p[1] == None and p[3] == None and p[4] == None:
        p[0] = None
    else:
        p[0] = Node("SourceFile", [p[1], p[3], p[4]])


def p_import_decl_rep(p):
    '''ImportDeclRep : epsilon
                     | ImportDeclRep ImportDecl SEMICOLON'''
    if len(p) == 4:
        if p[1] == None and p[2] == None:
			p[0] = None
		else:
			mylist = p[1]
			mylist.append(p[2])
            p[0] = Node("Import", mylist)
    else:
        p[0] = None


def p_toplevel_decl_rep(p):
    '''TopLevelDeclRep : TopLevelDeclRep TopLevelDecl SEMICOLON
                                           | epsilon'''
    if len(p) == 4:
        p[0] = Node("", [p[1], p[2]])
    else:
        p[0] = None
# --------------------------------------------------------


# ---------- PACKAGE CLAUSE --------------------
def p_package_clause(p):
    '''PackageClause : PACKAGE PackageName'''
    p[1] = Node(p[1])


def p_package_name(p):
    '''PackageName : IDENT'''
    p[0] = Node("", [p[1]])
# -----------------------------------------------


# --------- IMPORT DECLARATIONS ---------------
def p_import_decl(p):
    '''ImportDecl : IMPORT ImportSpec
                    | IMPORT LPAREN ImportSpecRep RPAREN '''
    if len(p) == 3:
        p[0] = Node("", "import", p[2])
    else:
        p[0] = Node("", "import", "(", p[3], ")"]


def p_import_spec_rep(p):
    ''' ImportSpecRep : ImportSpecRep ImportSpec SEMICOLON
                          | epsilon '''
    if len(p) == 4:
        p[0] = Node("", p[1], p[2], ";"]
    else:
        p[0] = Node("", [p[1]])


def p_import_spec(p):
    ''' ImportSpec : PackageNameDotOpt ImportPath '''
    p[0] = Node("", p[1], p[2])


def p_package_name_dot_opt(p):
    ''' PackageNameDotOpt : PERIOD
                                                  | PackageName
                                                  | epsilon'''
    if p[1] == '.':
        p[0] = Node("", "."]
    else:
        p[0] = Node("", [p[1]])


def p_import_path(p):
    ''' ImportPath : STRING '''
    p[0] = Node("", [p[1]])
# -------------------------------------------------------


def p_empty(p):
    '''epsilon : '''
    p[0] = "epsilon"

# def p_import_decl(p):


# def p_start(p):
#   '''start : expression'''
#   # p[0] = "<start>" + p[1] + "</start>"
#   p[0] = Node('start', [p[1]])

# def p_expression_plus(p):
#     '''expression : expression ADD term
#                   | expression SUB term'''
#     if p[2] == '+':
#         # p[0] = "<expr>" + p[1] + "</expr> + " + p[3]
#         p[0] = Node("", p[1], '+', p[3])
#     else:
#         # p[0] = "<expr>" + p[1] + "</expr> - " + p[3]
#         p[0] = Node("", p[1], '-', p[3])
#         # p[0] = p[1] - p[3]
# # def p_expression_minus(p):
# #     'expression : '

# def p_expression_term(p):
#     'expression : term'
#     # p[0] = "<term>" + p[1] + "</term>"
#     p[0] = Node("", [p[1]])

# def p_term_times(p):
#     'term : term MUL factor'
#     # p[0] = "<term>" + p[1] + "</term> * " + "<factor>" + p[3] + "</factor>"
#     p[0] = Node("", p[1], "*", p[3])


# # def p_term_div(p):
# #     'term : term QUO factor'
# #     p[0] = p[1] / p[3]

# def p_term_factor(p):
#     'term : factor'
#     p[0] = Node("", [p[1]])

# def p_factor_num(p):
#     'factor : INTEGER'
#     # p[0] = str([p[1]])
#     p[0] = Node("", str([p[1]])]

# # def p_factor_expr(p):
# #     'factor : LPAREN expression RPAREN'
# #     p[0] = p[2]


# Error rule for syntax errors


def p_error(p):
    print("Error in parsing!")
    print("Error at: ", p.type)
    sys.exit()


# Build lexer
lexer = lex.lex()
# lexer.abcde = 0   # custom global varibales for lexer

# Read input file
in_file_location = "input.go"
in_file = open(in_file_location, 'r')
out_file = open("output.dot", "w")
out_file.write('strict digraph G {\n')

data = in_file.read()

# Iterate to get tokens
parser = yacc.yacc()
res = parser.parse(data)

out_file.write("}\n")
# Close file
out_file.close()
in_file.close()