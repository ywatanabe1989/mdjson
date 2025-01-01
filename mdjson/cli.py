#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-01 19:26:43 (ywatanabe)"
# File: /home/ywatanabe/proj/mdjson/mdjson/cli.py

__file__ = "/home/ywatanabe/proj/mdjson/mdjson/cli.py"

import argparse
from mdjson import mdjson

def main():
    parser = argparse.ArgumentParser(description='Convert between Markdown and JSON')
    parser.add_argument('input_file', help='Input file (.md or .json)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--indent', '-i', type=int, default=2, help='JSON indent level')
    args = parser.parse_args()

    return mdjson(args.input_file, args.output, args.indent)

if __name__ == '__main__':
    exit(main())
