import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '..')

from elongation.plot import *
from elongation.elongation import *


def setup():
    pass


def teardown():
    pass


def test_setup_axis():
    fig, ax = plt.subplots()

    setup_axis(ax, 'None', xticks=range(100), xlim=(0, 100))


def test_cycle_values():
    assert next(cycle_values(None)) is None
    assert next(cycle_values(1)) == 1

    it = cycle_values([0, 1, 2])
    assert next(it) == 0
    assert next(it) == 1
    assert next(it) == 2
    assert next(it) == 0


def test_plotter(tmp_path):
    elongs = read_prn('tests/test_files/test1.prn')

    fig, ax = plt.subplots()
    plotter(
        elongs,
        title='Hello World', style='stress/strain',
        smoothed=False,
        plot=(fig, ax), xlim=(0, 300), xticks=[0, 100, 200, 300], xticks_minor=3,
        legend=True, colors=None, markers=None, linestyles=None,
        savefig=f'{tmp_path}/my_elongation_figure_1.png',
    )

    plotter(
        elongs,
        title='Hello Again', style='stress/strain',
        smoothed=True,
        plot=None,
        legend=False, colors='b', markers='x', linestyles='--',
        savefig=f'{tmp_path}/my_elongation_figure_2.png',
    )
