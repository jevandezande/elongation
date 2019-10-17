import sys
import numpy as np
import pytest

from datetime import datetime

from pytest import raises

sys.path.insert(0, '..')

from elongation.tools import read_elongation, read_prn, compare_dictionaries


def test_read_prn():
    e0, e1, e2 = read_prn('test_files/test1.prn')

    assert e0.crosshead_speed == 0.787
    assert e0.x_units == 'seconds'
    assert e0.y_units == 'Newtons'
    assert e0.sample_thickness == 1.000
    assert e0.sample_width == 1.000
    assert e0.gauge_length == 6.000
    assert e0.start_threshhold == 0.100
    assert len(e0.xs) == 2344
    assert len(e0.xs) == len(e0.ys)
    assert e0.date == datetime(2019, 8, 21)
    assert e0.length_conversion == 0.333333
    assert e0.force_conversion == 1.0
    assert e0.loadcell_capacity == 100
    assert e0.loadcell_capacity_unit == 1
    assert e0.loadcell_bits_of_resolution == 14
    assert e0.slack_time == 0.0
    assert e0.thickness == 1.0
    assert e0.break_load == 16.9010
    assert e0.break_strength == 16900.9524
    assert e0.break_elongation == 77.8917
    assert e0.break_percent_elongation == 1298.1944
    assert e0.yield_strength == 5199.9639
    assert e0.yield_load == 5.2

    with raises(AttributeError):
        e0.Number_of_Points

    assert e1.crosshead_speed == 21.260
    assert e1.x_units == 'seconds'
    assert e1.y_units == 'Newtons'
    assert e1.sample_thickness == 1.000
    assert e1.sample_width == 1.000
    assert e1.gauge_length == 60.000
    assert e1.start_threshhold == 0.100
    assert len(e1.xs) == 73
    assert len(e1.xs) == len(e1.ys)
    assert e1.date == datetime(2019, 8, 21)
    assert e1.length_conversion == 9.0
    assert e1.force_conversion == 1.0
    assert e1.loadcell_capacity == 100
    assert e1.loadcell_capacity_unit == 1
    assert e1.loadcell_bits_of_resolution == 14
    assert e1.slack_time == 0.0
    assert e1.thickness == 1.0
    assert e1.break_load == 34.3801
    assert e1.break_strength == 34380.0952
    assert e1.break_elongation == 51.534
    assert e1.break_percent_elongation == 85.89
    assert e1.yield_strength == 36025.7143
    assert e1.yield_load == 36.0257

    assert e2.crosshead_speed == 21.260
    assert e2.x_units == 'seconds'
    assert e2.y_units == 'Newtons'
    assert e2.sample_thickness == 1.000
    assert e2.sample_width == 1.000
    assert e2.gauge_length == 60.000
    assert e2.start_threshhold == 0.100
    assert len(e2.xs) == 65
    assert len(e2.xs) == len(e2.ys)
    assert e2.date == datetime(2019, 8, 21)
    assert e2.length_conversion == 9.0
    assert e2.force_conversion == 1
    assert e2.loadcell_capacity == 100
    assert e2.loadcell_capacity_unit == 1
    assert e2.loadcell_bits_of_resolution == 14
    assert e2.slack_time == 0.0
    assert e2.thickness == 1.0
    assert e2.break_load == 44.2093
    assert e2.break_strength == 44209.3333
    assert e2.break_elongation == 47.2410
    assert e2.break_percent_elongation == 78.7350
    assert e2.yield_strength == 44209.3333
    assert e2.yield_load == 44.2093


def test_read_csv(tmp_path):
    infile = 'test_files/test1.csv'
    elong = read_elongation(infile)
    outfile = f'{tmp_path}/test1_write.csv'
    elong.write(outfile)
    assert open(outfile).read() == open(infile).read()


def test_read():
    elongs = read_elongation('test_files/test1.prn')
    assert len(elongs) == 3
    assert elongs[0].x_units == 'seconds'
    assert elongs[0].y_units == 'Newtons'


def test_compare_dictionaries():
    cd = compare_dictionaries
    a = {}
    a2 = {}
    b = {1:1}
    c = {1:'a'}
    d = {2:1}
    e = {1:1, 2:1}
    f = {1:'a', 2:[1, 2, 3]}
    f2 = {1:'a', 2:[1, 2, 3]}
    g = {1:'b', 2:[1, 2, 3]}
    h = {2:'a', 2:[1, 2, 3]}
    i = {1:'a', 2:[1, 2, 4]}
    j = {1:'a', 2:np.array([1, 2, 3])}
    k = {1:'a', 2:np.array([1, 2, 4])}
    l = {1:'a', 2:{2:np.array([1, 2, 3])}}
    l2 = {1:'a', 2:{2:np.array([1, 2, 3])}}
    m = {1:'a', 2:{2:np.array([1, 2, 4])}}

    assert cd(a, a)
    assert cd(a, a2)
    assert cd(b, b)
    assert cd(e, e)
    assert cd(f, f)
    assert cd(f, f2)
    assert cd(j, j)
    assert cd(l, l)
    assert cd(l, l2)

    assert not cd(a, b)
    assert not cd(b, c)
    assert not cd(b, d)
    assert not cd(b, e)
    assert not cd(f, g)
    assert not cd(f, h)
    assert not cd(f, i)

    assert cd(e, {**b, **d})
    assert not cd(e, {**c, **d})
    assert cd(f, {**g, **c})

    assert cd(f, j)
    assert cd(j, {**j})
    assert not cd(j, i)
    assert cd(j, {**i, 2:np.array([1, 2, 3])})

    assert not cd(l, m)
    assert cd(l, {**m, 2:{2:np.array([1, 2, 3])}})
