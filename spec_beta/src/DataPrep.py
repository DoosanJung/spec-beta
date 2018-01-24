#!/usr/bin/env python
'''
'''
import pandas as pd
import logging
from logging import config
from spec_beta.conf.SpecBetaConfig import SpecBetaConfig

config.fileConfig("spec_beta/conf/SpecBeta.cfg")
logger = logging.getLogger()


class DataPrep(object):
    '''
    Data preparation
    '''
    def __init__(self):
        self.HOME_PATH = SpecBetaConfig.HOME_PATH
        pass

    def get_symbols_lst(self):
        symbols = pd.read_csv(self.HOME_PATH + '/spec_beta/data/symbol.csv')
        self.symbols_lst = symbols.columns.tolist()
        logger.info("testing")
        return self.symbols_lst
