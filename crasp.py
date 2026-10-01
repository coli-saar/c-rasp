import argparse
import sys

from parser import parse_file
from tracing import TraceToFile, TraceToHTML


def parse_args():
    parser = argparse.ArgumentParser(description="Run a C-RASP program.")

    # Mandatory: c-rasp program file
    parser.add_argument(
        "-c", "--c-rasp-file",
        type=str,
        help="Path to the C-RASP program file"
    )

    # Mandatory: tokens from command-line argument
    parser.add_argument(
        "tokens",
        nargs="?",
        default=None,
        help="Whitespace-separated list of tokens (e.g. '( ( ) )')"
    )

    # # Optional: tracing type
    # parser.add_argument(
    #     "--tracing",
    #     choices=["txt", "html"],
    #     help="Tracing output type (txt or html)"
    # )

    # Conditionally required: trace filename
    parser.add_argument(
        "-t", "--trace-file",
        default=None,
        help="Filename for tracing output (use filename extensions *.txt or *.html or *.htm)"
    )

    parser.add_argument(
        "--c-star", action="store_true",
        help="Use C*-RASP: numeric tokens are object IDs, accessible only through match"
    )
    args = parser.parse_args()

    return args


# read program
args = parse_args()
program = parse_file(args.c_rasp_file)

# prepare input
if args.tokens is not None:
    input_iterable = [args.tokens]
else:
    input_iterable = sys.stdin

# set up tracing
tr = None
if args.trace_file.lower().endswith(".txt"):
    tr = TraceToFile(args.trace_file)
elif args.trace_file.lower().endswith(".html") or args.trace_file.lower().endswith(".htm"):
    tr = TraceToHTML(args.trace_file)

input_id = 1
for line in input_iterable:
    if not line.startswith("//"):
        tokens = line.strip().split()
        if len(tokens) > 0:
            result = program.execute(tokens, tracing=tr, c_star=args.c_star)
            print(f"{input_id} {line.strip()}: {result}")
            input_id += 1

if tr is not None:
    tr.close()
    print(f"Trace written to {args.trace_file}")

