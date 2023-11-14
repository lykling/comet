#!/usr/bin/env python3
"""Main module for the application.
"""
import argparse
from . import commands

COMMANDS = {}


def register_command(parser: argparse.ArgumentParser, name: str,
                     command: callable, args_parser: callable):
    """register command
    """
    if args_parser is not None:
        args_parser(parser)

    COMMANDS[name] = {'name': name, 'command': command}


def main():
    """Main entry point of the application.
    """
    parser = argparse.ArgumentParser(description='yycli')
    subparsers = parser.add_subparsers(help='commands',
                                       title='valid commands',
                                       dest='command')
    crypt_parser = subparsers.add_parser('crypt', help='crypt help')
    register_command(crypt_parser, 'crypt', commands.crypt.crypt,
                     commands.crypt.args_parser)
    confuse_parser = subparsers.add_parser('confuse', help='confuse help')
    register_command(confuse_parser, 'confuse', commands.confuse.entrypoint,
                     commands.confuse.args_parser)
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    COMMANDS[args.command]['command'](args)


if __name__ == '__main__':
    main()
