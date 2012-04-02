#!/usr/bin/env python

"""aug2cmds converts an Augeas tree into a set of Augeas commands

Designed for use with augtool and Puppet.
"""

import __init__ as aug2cmds
import outputs
import argparse

def main():
    """Runs aug2cmds as an interactive tool"""
    parser = argparse.ArgumentParser(
        description="Convert file tree to Augeas commands for use in\
augtool/Puppet")
    parser.add_argument('-r', '--root',
        help='use ROOT as the root of the filesystem')
    parser.add_argument('-l', '--lens',
        help='lens to parse PATH with (e.g.  Sudoers.lns)')
    parser.add_argument('-y', '--yes',
        action='store_const', const='yes',
        help='always take default choices')
    parser.add_argument('-f', '--format',
        choices=['augtool', 'puppet'], default="augtool",
        help='output format')
    parser.add_argument('path',
        help='filename relative to ROOT to parse')
    parser.add_argument('augpath',
        nargs='?',
        help='optional Augeas path inside file to process')
    args = parser.parse_args()

    pathnode = aug2cmds.PathNode(args.path, root=args.root, lens=args.lens)
    if args.format == "augtool":
        output = outputs.Augtool()
    else:
        raise RuntimeError("Unknown output format")
    for cmd in output.visit(pathnode, args.augpath):
        print cmd

if __name__ == "__main__":
    main()
