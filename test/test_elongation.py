import sys
import numpy as np
import pytest

sys.path.insert(0, '..')

from elongation import Elongation
from elongation.tools import read_prn


def test_convert():
    elongs = read_prn('test_files/test1.prn')


def test_write_csv(tmp_path):
    elongs = read_prn('test_files/test1.prn')
    outfile = f'{tmp_path}/test1.csv'
    elongs[0].write(outfile)
    assert open(outfile).read() == open('test_files/test1.csv').read()


def test_write_prn(tmp_path):
    infile = 'test_files/test1.prn'
    elongs = read_prn(infile)
    outfile = f'{tmp_path}/test1.prn'
    elongs[0].write(outfile)


def test_modulus():
    elongs = read_prn('test_files/test1.prn')
    assert elongs[0].modulus == 1

def test_eq():
    elong1 = Elongation(np.arange(10), np.arange(10) + 1, '%', 'N')
    elong2 = Elongation(np.arange(10), np.arange(10) + 1, '%', 'N')
    elong3 = Elongation(np.arange(10), np.arange(10) + 1, '%', 'N')
    assert elong1 == elong1
    assert elong1 == elong2
    assert elong1 == elong3
