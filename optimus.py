from argparse import ArgumentParser

from server import run_server

arg_parser = ArgumentParser(
    prog="Optimus",
    description="A toy DNS server made for fun :)"
)

arg_parser.add_argument("-r", action="store_true", help="Run DNS server")
arg_parser.add_argument("-p", metavar="PORT", type=int, default=53,
                        help="Port to run the server on (defaults to 53)")
arg_parser.add_argument("-t", metavar="THREADS", type=int, default=100,
                        help="Number of worker threads to spin up for handling requests (defaults to 100)"
)

if __name__ == '__main__':
    args = arg_parser.parse_args()
    if args.r:
        run_server(args.p, args.t)
