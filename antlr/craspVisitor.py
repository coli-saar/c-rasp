# Generated from crasp.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .craspParser import craspParser
else:
    from craspParser import craspParser

# This class defines a complete generic visitor for a parse tree produced by craspParser.

class craspVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by craspParser#program.
    def visitProgram(self, ctx:craspParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#statement.
    def visitStatement(self, ctx:craspParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#bool_expr.
    def visitBool_expr(self, ctx:craspParser.Bool_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#count_expr.
    def visitCount_expr(self, ctx:craspParser.Count_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#match_bound.
    def visitMatch_bound(self, ctx:craspParser.Match_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#match_expr.
    def visitMatch_expr(self, ctx:craspParser.Match_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#match_constraints.
    def visitMatch_constraints(self, ctx:craspParser.Match_constraintsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#offset_list.
    def visitOffset_list(self, ctx:craspParser.Offset_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by craspParser#signed_integer.
    def visitSigned_integer(self, ctx:craspParser.Signed_integerContext):
        return self.visitChildren(ctx)



del craspParser