

from antlr4 import *
from antlr.craspLexer import craspLexer as CRaspLexer
from antlr.craspParser import craspParser as CRaspParser
from antlr.craspVisitor import craspVisitor as CRaspVisitor
from program import *


class MyCraspVisitor(CRaspVisitor):
    def __init__(self):
        super().__init__()
        self.imports = []
        self.c_star = False

    def visitProgram(self, ctx):
        stmts = [self.visit(s) for s in ctx.statement()]
        stmts = [s for s in stmts if s is not None]
        return Program(stmts, self.imports, self.c_star)

    def visitStatement(self, ctx):
        if ctx.CSTAR():
            self.c_star = True
            return None
        if ctx.IMPORT():
            # Handle the import statement: 'IMPORT VARIABLE'
            var_name = ctx.VARIABLE().getText()
            self.imports.append(var_name)
            return None
        else:
            # Handle the assignment: 'VARIABLE ASSIGN (bool_expr | count_expr)'
            var_name = ctx.VARIABLE().getText()
            expr = self.visit(ctx.getChild(2))
            return Assignment(var_name, expr)

    def visitBool_expr(self, ctx):
        if ctx.STRING_LITERAL():
            return StringLiteral(ctx.STRING_LITERAL().getText().strip('"'))

        elif ctx.LT():
            return Comparison(
                left=self.visit(ctx.count_expr(0)),
                op="<",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.GT():
            return Comparison(
                left=self.visit(ctx.count_expr(0)),
                op=">",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.EQ():
            return Comparison(
                left=self.visit(ctx.count_expr(0)),
                op="==",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.NEQ():
            return Comparison(
                left=self.visit(ctx.count_expr(0)),
                op="!=",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.LEQ():
            return Comparison(
                left=self.visit(ctx.count_expr(0)),
                op="<=",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.GEQ():
            return Comparison(
                left=self.visit(ctx.count_expr(0)),
                op=">=",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.AND():
            return BinaryBoolExpr(
                left=self.visit(ctx.bool_expr(0)),
                op="and",
                right=self.visit(ctx.bool_expr(1))
            )

        elif ctx.OR():
            return BinaryBoolExpr(
                left=self.visit(ctx.bool_expr(0)),
                op="or",
                right=self.visit(ctx.bool_expr(1))
            )

        elif ctx.NOT():
            return NotExpr(self.visit(ctx.bool_expr(0)))

        elif ctx.VARIABLE():
            return BoolVariable(ctx.VARIABLE().getText())

        elif ctx.TRUE():
            return BoolLiteral(True)

        elif ctx.FALSE():
            return BoolLiteral(False)

        elif ctx.LPAREN():
            return self.visit(ctx.bool_expr(0))
        

    def visitCount_expr(self, ctx):
        if ctx.COUNT():
            expr = self.visit(ctx.bool_expr()) if ctx.bool_expr() else BoolLiteral(True)
            if ctx.match_expr():
                bound = ctx.match_bound()
                if bound and [name.getText() for name in bound.VARIABLE()] != ["j", "i"]:
                    raise ValueError("A match count bound must be j < i or j <= i")
                return Match(
                    expr=expr,
                    predicate=self.visit(ctx.match_expr()),
                    inclusive=bound is None or bound.LEQ() is not None
                )
            if ctx.VARIABLE():
                return GuardedCount(expr=expr, guard=ctx.VARIABLE().getText())
            return Count(expr)

        elif ctx.IF():
            return IfExpr(
                then_branch=self.visit(ctx.count_expr(0)),
                condition=self.visit(ctx.bool_expr()),
                else_branch=self.visit(ctx.count_expr(1))
            )

        elif ctx.PLUS():
            return BinaryOp(
                left=self.visit(ctx.count_expr(0)),
                op="+",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.MINUS():
            return BinaryOp(
                left=self.visit(ctx.count_expr(0)),
                op="-",
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.TIMES():
            return MultiplicationOp(
                factor=int(ctx.INT_LITERAL().getText()),
                expr=self.visit(ctx.count_expr(0))
            )

        elif ctx.MAX():
            return BinaryOp(
                op="max",
                left=self.visit(ctx.count_expr(0)),
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.MIN():
            return BinaryOp(
                op="min",
                left=self.visit(ctx.count_expr(0)),
                right=self.visit(ctx.count_expr(1))
            )

        elif ctx.match_expr():
            return Match(
                predicate=self.visit(ctx.match_expr()),
                expr=BoolLiteral(True),
                inclusive=True
            )

        elif ctx.INT_LITERAL():
            return CountLiteral(int(ctx.INT_LITERAL().getText()))

        elif ctx.VARIABLE():
            return CountVariable(ctx.VARIABLE().getText())

        elif ctx.LPAREN():
            return self.visit(ctx.count_expr(0))


    def visitMatch_expr(self, ctx):
        constraints = [
            tuple(int(value.getText()) for value in item.signed_integer())
            for item in ctx.match_constraints().offset_list()
        ]
        return MatchPredicate(constraints)


def parse_file(filename) -> Program:
    input_stream = FileStream(filename, encoding="utf-8")
    lexer = CRaspLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CRaspParser(stream)

    # Replace 'startRule' with your actual entry rule
    tree = parser.program()
    # print(tree.toStringTree(recog=parser))

    visitor = MyCraspVisitor()
    ast : Program = visitor.visit(tree)

    return ast
