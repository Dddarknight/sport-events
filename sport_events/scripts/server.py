#!/usr/bin/env python

from sport_events.parser import Parser


def main():
    parser = Parser()
    parser.get_sports()
    parser.migrate_sports()


if __name__ == '__main__':
    main()
