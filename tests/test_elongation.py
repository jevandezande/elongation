import sys
import numpy as np

from pytest import raises

sys.path.insert(0, '..')

from elongation.elongation import *


def test_convert():
    elongs = read_prn('tests/test_files/test1.prn')


def test_write_csv(tmp_path):
    elongs = read_prn('tests/test_files/test1.prn')
    outfile = f'{tmp_path}/test1.csv'
    elongs[0].write(outfile)
    assert open(outfile).read() == open('tests/test_files/test1.csv').read()


def test_write_prn(tmp_path):
    infile = 'tests/test_files/test1.prn'
    elongs = read_prn(infile)
    outfile = f'{tmp_path}/test1.prn'
    elongs[0].write(outfile)


def test_smoothed():
    elong = read_prn('tests/test_files/test1.prn')[0]
    assert all(elong.smoothed().xs == elong.xs)
    assert all(elong.smoothed(1).ys == elong.ys)
    elong.smoothed().ys == 0


def test_cross_section():
    elong = read_prn('tests/test_files/test1.prn')[0]
    assert elong.cross_section == 1


def test_modulus():
    elongs = read_prn('tests/test_files/test1.prn')
    assert elongs[0].modulus == 1

def test_eq():
    data = {
        'break_load': 1.2,
        'break_elongation': 12.34,
        'break_strength': 12.3,
        'crosshead_speed': 123.4,
        'gauge_length': 123.45,
        'sample_width': 9,
        'sample_thickness': 10,
        'yield_strength': 1234.5,
        'yield_load': 12346.7,
        'a': np.array([1, 0, 10])
    }
    data2 = {
        'break_load': 1.2,
        'break_elongation': 12.3,
        'break_strength': 12.3,
        'crosshead_speed': 123.4,
        'gauge_length': 123.45,
        'sample_width': 9,
        'sample_thickness': 10,
        'gauge_length': 123.45,
        'yield_strength': 1234.5,
        'yield_load': 12346.7,
        'a': np.array([1, 0, 10])
    }

    elong1 = Elongation(np.arange(10), np.arange(10) + 1, '%', 'N', **data)
    elong2 = Elongation(np.arange(10), np.arange(10) + 1, '%', 'N', **data2)
    elong3 = Elongation(np.arange(10), np.arange(10) + 1, '%', 'N', **data)
    assert elong1 == elong1
    assert elong1 == elong2
    assert elong1 == elong3


def test_read_prn():
    e0, e1, e2 = read_prn('tests/test_files/test1.prn')

    assert e0.crosshead_speed == 0.787
    assert e0.x_units == 's'
    assert e0.y_units == 'N'
    assert e0.data['sample_thickness'] == 1.000
    assert e0.data['sample_width'] == 1.000
    assert e0.data['gauge_length'] == 6.000
    assert e0.data['start_threshhold'] == 0.100
    assert len(e0.xs) == 2344
    assert len(e0.xs) == len(e0.ys)
    assert e0.data['date'] == datetime(2019, 8, 21)
    assert e0.data['length_conversion'] == 0.333333
    assert e0.data['force_conversion'] == 1.0
    assert e0.data['loadcell_capacity'] == 100
    assert e0.data['loadcell_capacity_unit'] == 1
    assert e0.data['loadcell_bits_of_resolution'] == 14
    assert e0.data['slack_time'] == 0.0
    assert e0.data['thickness'] == 1.0
    assert e0.break_load == 16.9010
    assert e0.break_strength == 16900.9524
    assert e0.data['break_elongation'] == 77.8917
    assert e0.data['break_percent_elongation'] == 1298.1944
    assert e0.yield_strength == 5199.9639
    assert e0.yield_load == 5.2

    with raises(AttributeError):
        e0.Number_of_Points

    assert e1.crosshead_speed == 21.260
    assert e1.x_units == 's'
    assert e1.y_units == 'N'
    assert e1.data['sample_thickness'] == 1.000
    assert e1.data['sample_width'] == 1.000
    assert e1.data['gauge_length'] == 60.000
    assert e1.data['start_threshhold'] == 0.100
    assert len(e1.xs) == 73
    assert len(e1.xs) == len(e1.ys)
    assert e1.data['date'] == datetime(2019, 8, 21)
    assert e1.data['length_conversion'] == 9.0
    assert e1.data['force_conversion'] == 1.0
    assert e1.data['loadcell_capacity'] == 100
    assert e1.data['loadcell_capacity_unit'] == 1
    assert e1.data['loadcell_bits_of_resolution'] == 14
    assert e1.data['slack_time'] == 0.0
    assert e1.data['thickness'] == 1.0
    assert e1.break_load == 34.3801
    assert e1.break_strength == 34380.0952
    assert e1.data['break_elongation'] == 51.534
    assert e1.data['break_percent_elongation'] == 85.89
    assert e1.yield_strength == 36025.7143
    assert e1.yield_load == 36.0257

    assert e2.crosshead_speed == 21.260
    assert e2.x_units == 's'
    assert e2.y_units == 'N'
    assert e2.data['sample_thickness'] == 1.000
    assert e2.data['sample_width'] == 1.000
    assert e2.data['gauge_length'] == 60.000
    assert e2.data['start_threshhold'] == 0.100
    assert len(e2.xs) == 65
    assert len(e2.xs) == len(e2.ys)
    assert e2.data['date'] == datetime(2019, 8, 21)
    assert e2.data['length_conversion'] == 9.0
    assert e2.data['force_conversion'] == 1
    assert e2.data['loadcell_capacity'] == 100
    assert e2.data['loadcell_capacity_unit'] == 1
    assert e2.data['loadcell_bits_of_resolution'] == 14
    assert e2.data['slack_time'] == 0.0
    assert e2.data['thickness'] == 1.0
    assert e2.break_load == 44.2093
    assert e2.break_strength == 44209.3333
    assert e2.data['break_elongation'] == 47.2410
    assert e2.data['break_percent_elongation'] == 78.7350
    assert e2.yield_strength == 44209.3333
    assert e2.yield_load == 44.2093


def test_read_csv(tmp_path):
    infile = 'tests/test_files/test1.csv'
    elong = read_elongation(infile)
    outfile = f'{tmp_path}/test1_write.csv'
    elong.write(outfile)
    assert open(outfile).read() == open(infile).read()


def test_read():
    elongs = read_elongation('tests/test_files/test1.prn')
    assert len(elongs) == 3
    assert elongs[0].x_units == 's'
    assert elongs[0].y_units == 'N'


