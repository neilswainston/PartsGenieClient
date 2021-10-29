from logging import Logger
from .Args import build_args_parser
from .client import PartsGenieClient


def entry_point():
    parser = build_args_parser(
        prog = 'partsgenie_client',
        description='Requests a input (SBOL) file to a PartsGenie server'
    )
    args = parser.parse_args()

    client = PartsGenieClient(args.url)
    client.run(
        args.infile,
        args.taxonomy_id,
        args.outfile
    )

if __name__ == '__main__':
    entry_point()
