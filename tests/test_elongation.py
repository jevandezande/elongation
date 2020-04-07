import sys
import numpy as np

from numpy.testing import assert_almost_equal as aae

from pytest import raises

sys.path.insert(0, '..')

from elongation.elongation import *


def test_read():
    elongs = read_elongation('tests/test_files/test1.prn')
    assert len(elongs) == 3


def test_read_prn():
    e0, e1, e2 = read_prn('tests/test_files/test1.prn')

    assert e0.sample_thickness == 1.000
    assert e0.sample_width == 1.000
    assert e0.gauge_length == 6.000
    assert len(e0.xs) == 2344
    assert len(e0.xs) == len(e0.ys)

    assert e1.sample_thickness == 1.000
    assert e1.sample_width == 1.000
    assert e1.gauge_length == 60.000
    assert len(e1.xs) == 73
    assert len(e1.xs) == len(e1.ys)

    assert e2.sample_thickness == 1.000
    assert e2.sample_width == 1.000
    assert e2.gauge_length == 60.000
    assert len(e2.xs) == 65
    assert len(e2.xs) == len(e2.ys)


def test_read_csv(tmp_path):
    infile = 'tests/test_files/test1.csv'
    elong, *others = read_elongation(infile)
    assert len(others) == 0

    outfile = f'{tmp_path}/test1_write.csv'
    elong.write(outfile)


def test_eq():
    elong1 = Elongation(np.arange(10), np.arange(10) + 1, 1, 1, 1, 'A')
    elong2 = Elongation(np.arange(10), np.arange(10) + 1, 1, 1, 1, 'A')
    elong2.spam = 99
    assert elong1 == elong1
    assert elong1 == elong2


def test_copy():
    elong = Elongation(np.arange(10), np.arange(10) + 1, 1, 1, 1, 'A')
    assert elong == elong.copy()


def test_cross_section():
    elong = read_prn('tests/test_files/test1.prn')[0]
    assert elong.cross_section == 1


def test_smoothed():
    elong = read_prn('tests/test_files/test1.prn')[0]
    assert all(elong.smoothed().xs == elong.xs)
    assert all(elong.smoothed(1).ys == elong.ys)
    assert elong.smoothed().ys[0] == 0
    aae(sum(elong.smoothed().ys - elong.ys), 0, 2)  # ensure there is no baseline shift


def test_cropped():
    elong = read_prn('tests/test_files/test1.prn')[0]
    cropped = elong.cropped(1, 10)
    cropped2 = elong.cropped(1, 10, shifted=False)

    aae(cropped.xs[0], 0)
    aae(cropped.xs[-1], 8.982818)

    aae(cropped.xs + 1.030183, cropped2.xs)
    assert all(cropped.ys == cropped.ys)


def test_cleaned():
    elong = read_prn('tests/test_files/test1.prn')[0]

    assert len(elong.cleaned(None, None).xs) == len(elong.xs)
    assert len(elong.cleaned().xs) == 2327
    assert len(elong.cleaned(0.01, None).xs) == 2334
    assert len(elong.cleaned(None, 0.5).xs) == 2337
    assert len(elong.cleaned(None, 0.9).xs) == 2331


def test_peaks():
    elong = read_prn('tests/test_files/test1.prn')[0]
    peak_indices, properties = elong.peak_indices()
    peaks, properties = elong.peaks()
    assert len(peaks) == 1
    aae(peaks[0], 180.735337)
    aae(peaks[0], elong.xs[peak_indices[0]])


def test_youngs_modulus_array():
    elong = read_prn('tests/test_files/test1.prn')[0]
    for val in elong.youngs_modulus_array:
        if val is np.nan:
            print(9)
    aae(elong.youngs_modulus_array[:7], [0, 0.4067902, 0, 0, 0, 0.5543513, 0])


def test_youngs_modulus():
    elong = read_prn('tests/test_files/test1.prn')[0]
    aae(elong.youngs_modulus, 1.4498419835141907)


def test_break():
    elong = read_prn('tests/test_files/test1.prn')[0]
    idx = elong.break_index()
    aae(elong.xs[idx], 180.735337)
    aae(elong.ys[idx], 17.3902)
    aae(elong.xs[idx], elong.break_elongation())


def test_yield():
    elong = read_prn('tests/test_files/test1.prn')[0]
    idx = elong.yield_index()
    aae(elong.xs[idx], 180.735337)
    aae(elong.ys[idx], 17.3902)
    aae(elong.xs[idx], elong.yield_elongation())
    aae(elong.break_elongation(), elong.yield_elongation())
