import sys
import numpy as np

from datetime import datetime

sys.path.insert(0, '..')

from elongation.tools import compare_dictionaries


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
