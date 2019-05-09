'''
command line interface for document store transaction family.

Parses command line args and passes it to the DocumentStoreClient class to process.
'''

import argparse
import getpass
import logging
import os
import sys
import traceback
import pkg_resources

from colorlog import ColoredFormatter

from docstore.documentstore_client import DocumentStoreClient

DISTRIBUTION_NAME = 'document_store'

DEFAULT_URL = 'http://localhost:8008'

def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)
    clog.setLevel(logging.DEBUG)
    return clog

def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def add_store_parser(subparser,parent_parser):
    '''define the document store command line parsing.'''

    parser = subparser.add_parser(
        'store',
        help='stores hash of the documnet',
        parents=[parent_parser])

    parser.add_argument(
        'hash_value',
        type=str,
        help='hash of the documnet'
    )

    parser.add_argument(
        'username',
        type=str,
        help='name of the user'
    )


def add_retrieve_parser(subparseer,parent_parser):
    '''define the parser to retrieve doc hash from command line'''
    parser = subparseer.add_parser(
        'retrieve',
        help='shows hash of the doc',
        parents=[parent_parser])

    parser.add_argument(
        'username',
        type=str,
        help='name of the user'
    )

def create_parent_parser(prog_name):
    '''Define the -V/--version command line options.'''
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser

def create_parser(prog_name):
    '''Define the command line parsing for all the options and subcommands.'''
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to manage your document store',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_store_parser(subparsers,parent_parser)
    add_retrieve_parser(subparsers,parent_parser)

    return parser

def _get_keyfile(username):
    '''Get the private key for a user.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)

def _get_pubkeyfile(username):
    '''Get the public key for a user.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.pub'.format(key_dir, username)

def do_store(args):
    '''implements the "store" subcommand by calling the client class.'''
    keyfile = _get_keyfile(args.username)

    client = DocumentStoreClient(baseUrl=DEFAULT_URL, keyFile=keyfile)

    response = client.store(args.hash_value)

    print("Response: {}".format(response))

def do_retrieve(args):
    '''implements the "retrieve" subcommand by calling client class.'''

    keyfile = _get_keyfile(args.username)

    client = DocumentStoreClient(baseUrl=DEFAULT_URL, keyFile=keyfile)
    
    data = client.retrieve()
    print("data:"+str(data))
    if data is not None:
        print("\n {} has a document with hash :{} ".format(args.username,data.decode()))
    else:
        raise Exception("Document not found for: {}".format(args.username))

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    '''Entry point function for the client CLI.'''
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    verbose_level = 0

    setup_loggers(verbose_level=verbose_level)

    #Get the commands from command line and call respective handlers.
    if args.command == 'store':
        do_store(args)
    elif args.command == 'retrieve':
        do_retrieve(args)
    else:
        raise Exception("Invalid command {}".format(args.command))

def main_wrapper():
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
