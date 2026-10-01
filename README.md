# Interpreter for C-RASP

This is an interpreter for [C-RASP](https://arxiv.org/abs/2404.04393) programs, written in Python.

## Installation

```
pip install -r requirements.txt
```

## Usage

Write a C-RASP grammar and save it to a file. An example is in [dyck1_yc24.cr](https://github.com/coli-saar/c-rasp/blob/main/dyck1_yc24.cr)
(this is the program for Dyck languages with one type of brackets from Yang & Chiang 2024).

Run the interpreter as follows. Tokens are specified in a whitespace-separated string on the command line.

```
python crasp.py -c examples/dyck1_yc24.cr "( ( ) ( ) )" -t trace.html
```

Instead of passing tokens on the command line, you can also read them from stdin. This can be useful if you want to run the C-RASP program against an entire testsuite.

```
python crasp.py -c examples/count3_yc24.cr -t trace.html < examples/count3_examples.txt
```

The interpreter will run the given C-RASP program on every nonempty line that does not start with `//`, and will generate one line of output per input instance. If you ask for tracing (see below), the trace file will contain a trace for each input instance.


## Tracing

The interpreter will print `True` or `False` to the command line, depending on whether the last position of the final expression
evaluated to true or not. We interpret this as the program accepting the input tokens.

You can also save a trace of the intermediate results in a file. Specify `-t filename.txt` to save the trace in a plain text file
or `-t filename.html` to save it in an HTML table that you can inspect with a browser. The trace file will
show the list of variable assignments with their new values as they happen.


## C-RASP programs

You can use all the operations from the [C-RASP paper](https://arxiv.org/abs/2404.04393). The counting operator is written with a hashtag, e.g. `# "a"` counts the number of positions up to the current one where the token is `a`. The operator $Q_a(i)$ from C-RASP, which is true if the token at position $i$ is $a$, is expressed as `"a"` in this tool. 

In addition to the logical and arithmetic operations defined in the paper, both conjunction `&&` and disjunction `||`, as well as `+` and `-` are available. Min and max are written as `min(a,b)` and `max(a,b)`. All arithmetic comparisons are available (`==`, `!=`, `<`, `>`, `<=`, `>=`).

You should not trust too deeply in any particular rules for operator precedence. When in doubt, put an expression in brackets.


### Unary and binary predicates
In addition to the basic operations of C-RASP, this tool also supports the unary and binary predicates of [Huang et al. 2025](https://arxiv.org/abs/2410.02140), cf. the phi and psi in their Definition 8. You can define these predicates by adding them as functions in [predefined.py](https://github.com/coli-saar/c-rasp/blob/main/predefined.py) (see the examples there for details). You can then make them available to your program using the statement `#import predicatename` (see e.g. [contains\_ab\_h25.cr](https://github.com/coli-saar/c-rasp/blob/main/examples/contains_ab_h25.cr) for an example). 

You can simply use unary predicate names like a variable; its value will be the list of boolean values obtained by evaluating the predicate name on each input position (e.g. `pos_even` in [aa\_star\_h25.cr](https://github.com/coli-saar/c-rasp/blob/main/examples/aa_star_h25.cr)).

You can use binary predicates as guards for the `#` operator; this will restrict the iteration over positions to the left to ones that satisfy the binary predicate (e.g. `pred` in [contains\_ab\_h25.cr](https://github.com/coli-saar/c-rasp/blob/main/examples/contains_ab_h25.cr)).

Note that unlike in Huang et al., we count the first input token as position 0 and not as position 1. Keep this in mind when defining predicates that rely on numerical properties of the positions; for instance, the check for even input positions in `pos_even` changes its meaning.



## C*-RASP

Enable the split alphabet with `#cstar` in the program or `--c-star` on the
command line (or `execute(..., c_star=True)`). Without either flag, programs
retain the previous C-RASP behavior.

```
#cstar
has_increment_pair = (# [j <= i, match([(0, 0, -1)])] true) > 0
```

Numeric input tokens become nonnegative object IDs. Quoted literals query only
fixed-alphabet symbols; numeric literal queries are rejected. Default C-RASP
mode retains the original string-token behavior. The final C*-RASP statement
must be Boolean.

`match([(delta, gamma, tau), ...])` follows [Definition 3.3](https://arxiv.org/html/2603.19954v2#S3.SS2):
`c[j-delta] == c[i-gamma] + tau` for every tuple. `delta` and `gamma` are
nonnegative lookbacks, while `tau` is signed. Out-of-bounds or non-object
comparisons are false. An empty list gives true. As a count expression, match
defaults to **j <= i**; write `j < i` explicitly for prior positions only.

Existing guarded counts can use an imported binary predicate. Match counts can
optionally include a Boolean body evaluated at `j`; if omitted, the body defaults
to `true`. If the bound is omitted, it defaults to `j <= i`; use `j < i` to
count only earlier positions:

```
#import pos_even
n = # [j < i, match([(0, 0, 0)])] pos_even
```

The body is evaluated at `j`; `pos_even` supplies its Boolean value at each
position. The body may be omitted, as in `# [j <= i, match([...])]`, to count
all matching positions. Standalone `match(...)` is also an inclusive shorthand.


## Recompiling the ANTLR parser

```
cd antlr
java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor crasp.g4 
```

