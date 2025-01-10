""" Docstring for the analyze.py file.

"""
import logging
import os

import pandas as pd

from analyzer.file_analyzer import FileAnalyzer
from analyzer.topographic_profile import TopographicProfile
from controller import PointController
from log import setup_logging

filename = f'{os.getcwd()}/files/antennas-RJ.csv'
OUTPUT_DIR = "outputs"


if __name__ == '__main__':
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info('Starting process to analyse the topographic profile of different points...')

    file_analyzer = FileAnalyzer(filename=filename)
    top_profile = TopographicProfile('google', 'AIzaSyB00vnm5fWSn7C6JLRgIkzL_EWe8oaCeRI')

    controller = PointController(OUTPUT_DIR, file_analyzer, top_profile)

    df = pd.read_csv('files/LATLONGs Projeto 22(Planilha1).csv', delimiter=';')
    lat_longs = [(row[0].item(), row[1].item()) for row in df.to_numpy()]

    for ref_lat_lon in lat_longs:
        controller.analyze_lat_lon(ref_lat_lon)
