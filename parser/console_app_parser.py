# -*- coding: utf-8 -*-

import argparse
from app_parser import ApplicationStoreParser


class AppParserManager:
    def __init__(self):
        self.scanner_parser = argparse.ArgumentParser('Script collects information about '
                                                      'applications in google play store using key word.')

    def add_arguments(self):
        self.scanner_parser.add_argument('-k', '--key_word', required=True,
                                         help='Input key word to collect information about all application'
                                              'in google play store that has'
                                              'this word in name or description')
        return self.scanner_parser.parse_args()

    def run(self):
        args = self.add_arguments()
        print('Running ...')
        extractor = ApplicationStoreParser(args.key_word)
        extractor.run()


manager = AppParserManager()
manager.run()
