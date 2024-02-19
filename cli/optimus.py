import sys
from argparse import ArgumentParser

from optimus_server.server import run_server


def main(argv):
    arg_parser = ArgumentParser(
        prog="Optimus",
        description="A toy DNS server made for fun ;)"
    )
    arg_parser.add_argument("-r", action="store_true", help="Run DNS server")
    arg_parser.add_argument("-p", metavar="PORT", type=int, default=53,
                            help="Port to run the server on (defaults to 53)")
    arg_parser.add_argument("-t", metavar="THREADS", type=int, default=100,
                            help="Number of worker threads to spin up for handling requests (defaults to 100)")
    args = arg_parser.parse_args(argv)
    if args.r:
        run_server(args.p, args.t)
    else:
        arg_parser.print_help()


def main_wrapper():
    main(sys.argv[1:])
