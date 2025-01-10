""" Docstring for the analyze.py file.

"""
import logging
import os

import pandas as pd

from analyzer.FileAnalyzer import FileAnalyzer
from analyzer.TopographicProfile import TopographicProfile
from controller import PointController
from log import setup_logging

filename = f'{os.getcwd()}/files/antennas-RJ.csv'
output_dir = "outputs"


if __name__ == '__main__':
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info(f'Starting process to analyse the topographic profile of different points...')

    file_analyzer = FileAnalyzer(filename=filename)
    top_profile = TopographicProfile('google', 'AIzaSyB00vnm5fWSn7C6JLRgIkzL_EWe8oaCeRI')

    controller = PointController(output_dir, file_analyzer, top_profile)

    df = pd.read_csv('files/LATLONGs Projeto 22(Planilha1).csv', delimiter=';')
    lat_longs = [(row[0].item(), row[1].item()) for row in df.to_numpy()]

    for ref_lat_lon in lat_longs:
        controller.analyze_lat_lon(ref_lat_lon)
