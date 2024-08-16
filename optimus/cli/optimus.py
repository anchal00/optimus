import sys
from argparse import ArgumentParser

from optimus.__version__ import VERSION
from optimus.optimus_server.server import run_server


def main(argv):
    DEFAULT_WORKER_THREADS = 10
    DEFAULT_PORT = 53

    arg_parser = ArgumentParser(
        prog="Optimus",
        description="A toy DNS server made for fun ;)",
        epilog=f"Version {VERSION}",
    )
    arg_parser.add_argument("-r", action="store_true", help="Run DNS server")
    arg_parser.add_argument(
        "-p",
        metavar="PORT",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to run the server on (defaults to {DEFAULT_PORT})",
    )
    arg_parser.add_argument(
        "-t",
        metavar="THREADS",
        type=int,
        default=DEFAULT_WORKER_THREADS,
        help=f"Number of worker threads to spin up for handling requests (defaults to {DEFAULT_WORKER_THREADS})",
    )
    arg_parser.add_argument("-v", action="store_true", help="Get version info")
    args = arg_parser.parse_args(argv)
    if args.r:
        run_server(args.p, args.t)
    elif args.v:
        print(f"Optimus Version: {VERSION}")
    else:
        arg_parser.print_help()


def main_wrapper():
    main(sys.argv[1:])
