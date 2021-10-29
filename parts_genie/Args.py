from argparse  import ArgumentParser
from ._version import __version__

def build_args_parser(
    prog: str,
    description: str = '',
    epilog: str = ''
) -> ArgumentParser:

    parser = ArgumentParser(
        prog = prog,
        description = description,
        epilog = epilog
    )

    # Build Parser
    parser = add_arguments(parser)

    return parser


def add_arguments(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        'url',
        type=str,
        help='URL to PartsGenie server'
    )
    parser.add_argument(
        'infile',
        type=str,
        help='specify input (SBOL) file'
    )
    parser.add_argument(
        'taxonomy_id',
        type=int,
        help='Taxonomy ID of the chassis'
    )
    parser.add_argument(
        'outfile',
        type=str,
        help='Filename to store the modified SBOL input file'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )
    return parser
