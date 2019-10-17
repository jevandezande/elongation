import sys
import numpy as np

from datetime import datetime

import more_itertools as mit

sys.path.insert(0, '..')

from elongation import Elongation


class MyIter(mit.peekable):
    """
    Simple class for making it easier to debug reading of files.
    """
    def __init__(self, iterable):
        self._index = 0
        self._line = None
        super().__init__(iterable)

    def __next__(self):
        self._index += 1
        self._line = super().__next__()
        return self._line


def read_elongation(file_name):
    """
    Read an elongation file.

    :param file_name: name of the file
    :return: Elongation object
    """
    extension = file_name.split('.')[-1]

    if extension == 'prn':
        return read_prn(file_name)
    elif extension == 'csv':
        return read_csv(file_name)
    else:
        raise NotImplementedError(f'Reading {extension} files is not yet implemented.')


def read_prn(file_name):
    """
    Read a prn file.

```
prn:13|
subtype = MT2500
Doc={MT2500:14|
  Film={12.1|
    Test_Mode = tensile
    Setup_Name = -
    Unit_System = SI
    Graph_Mode = stress/strain
    Sample_Length = 60.00
    CrossheadVlcty = 540
    VelocityUnitId = 1
    CrossheadSpeed = 21.2598
    Loadcell_Mode = Tension
    Loadcell_Type = "SM Series"
    Start_Threshold = 0.10
    Stop_Threshold = 0.10
    Auto_Stop = True
    Auto_Return = True
    ExtnsnResetOnStart = False
    Yield_Type = 0
    COF_Sled_Load = 200.00
    }
  Test_Info={2|
    Color = e
    Order_Id = d
    Technician = a
    Test_Method = b
    Sample_Conditioning = f
    Test_Conditions = g
    Product_Name = c
    Test_Direction = up
    }
  Test_Data=(
    {6|
      Crosshead_speed = 0.787
      X_unit = Secs.
      Y_unit = Newtons
      Sample_Thkness = 1.000
      Sample_Width = 1.000
      Grip_Separation = 6.000
      Start_Threshhold = 0.100
      Stop_Threshhold = 0.100
      Number_Of_Points = 2344
      Points = [
      0.1800,   0.0000
      ...
      6.1130,  -1.2009
         ]
      },
      {6|
        ...
      }
    )
  Test_Results=(
    {6|
      TestDate = 21 Aug, 2019
      Length_Cnvrsn = 0.333333
      Force_Cnvrsn = 1.000000
      LoadCell_Capacity = 100
      LoadCell_CpctyUnit = 1
      LoadCell_BitsOfReso = 14
      Analysis={ATensile:1|
        Slack_time = 0.000000
        SampleThickness = 1.0000
        BreakLoad = 16.9010
        BreakStrength = 16900.9524
        BreakElongation = 77.8917
        BreakPctElongation = 1298.1944
        YieldStrength1 = 5199.9639
        YieldLoad1 = 5.2000
        }
      },
    {6|
        ...
      }
    )
  }
```
      """

    with open(file_name) as f:
        f = MyIter(f)
        try:
            assert next(f).strip() == 'prn:13|'
            assert next(f).strip() == 'subtype = MT2500'
            assert next(f).strip() == 'Doc={MT2500:14|'

            assert next(f).strip() == 'Film={12.1|'
            film_data = {}
            for line in f:
                if '}' in line:
                    break
                key, value = read_key_value(line)
                film_data[key] = value

            assert next(f).strip() == 'Test_Info={2|'
            test_info = {}
            for line in f:
                if '}' in line:
                    break
                key, value = read_key_value(line)
                test_info[key] = value

            assert next(f).strip() == 'Test_Data=('
            test_data = []
            for i, line in enumerate(f):
                if line.strip() != '{6|':
                    break

                test_data.append({})
                for line in f:
                    if '[' in line:
                        break
                    key, value = read_key_value(line)
                    test_data[i][key] = try_to_num(value)

                xs, ys = [], []
                for line in f:
                    if ']' in line:
                        break
                    x, y = line.split(',')
                    xs.append(x)
                    ys.append(y)

                test_data[i]['xs'] = np.array(xs, dtype='float')
                test_data[i]['ys'] = np.array(ys, dtype='float')
                assert int(test_data[i]['Number_Of_Points']) == len(xs)
                assert next(f).strip()[0] == '}'  # may have a comma

            assert 'Test_Results=(' == next(f).strip()
            test_results = []
            for i, line in enumerate(f):
                if line.strip() != '{6|':
                    break
                test_results.append({})
                for line in f:
                    if '}' in line:
                        break
                    key, value = read_key_value(line)
                    test_results[i][key] = try_to_num(value)
                assert next(f).strip()[0] == '}'  # may include comma

        except AssertionError as e:
            print(f._index, f._line)
            raise

    data_remove = ['Number_Of_Points']
    results_swaps = [
        ('TestDate', 'date'),
        ('Length_Cnvrsn', 'length_conversion'),
        ('Force_Cnvrsn', 'force_conversion'),
        ('LoadCell_Capacity', 'loadcell_capacity'),
        ('LoadCell_CpctyUnit', 'loadcell_capacity_unit'),
        ('LoadCell_BitsOfReso', 'loadcell_bits_of_resolution'),
        ('Slack_time', 'slack_time'),
        ('BreakStrength', 'break_strength'),
        ('BreakElongation', 'break_elongation'),
        ('BreakPctElongation', 'break_percent_elongation'),
        ('YieldStrength1', 'yield_strength'),
        ('YieldLoad1', 'yield_load'),
        ('SampleThickness', 'thickness'),
        ('BreakLoad', 'break_load'),
    ]
    results_remove = ['Analysis']
    data_swaps = [
        ('X_unit', 'x_units'),
        ('Y_unit', 'y_units'),
        ('Crosshead_speed', 'crosshead_speed'),
        ('Sample_Thkness', 'sample_thickness'),
        ('Sample_Width', 'sample_width'),
        ('Grip_Separation', 'gauge_length'),
        ('Start_Threshhold', 'start_threshhold'),
        ('Stop_Threshhold', 'stop_threshhold'),
    ]

    elongations = []
    assert len(test_data) == len(test_results)
    for data, results in zip(test_data, test_results):
        for original, to in data_swaps:
            data[to] = data.pop(original)
        for original, to in results_swaps:
            results[to] = results.pop(original)
        for key in data_remove:
            data.pop(key)
        for key in results_remove:
            results.pop(key)

        if data['x_units'] == 'Secs.':
            data['x_units'] = 'seconds'
        if results['date']:
            results['date'] = datetime.strptime(results['date'], '%d %b, %Y')

        elongations.append(Elongation(**data, **results, film_data=film_data, test_info=test_info))

    return elongations


def read_csv(file_name):
    data = {}
    with open(file_name) as f:
        for line in f:
            if not line.strip():
                continue
            if line == 'Points\n':
                break
            key, val = read_key_value(line, separator=',')
            key = key.lower().replace(' ', '_')
            data[key] = val

        x_units, y_units = f.readline().split(',')
        data['x_units'], data['y_units'] = x_units.strip(), y_units.strip()

        xs, ys = [], []
        for line in f:
            x, y = line.split(',')
            xs.append(float(x.strip()))
            ys.append(float(y.strip()))
        data['xs'], data['ys'] = xs, ys

    return Elongation(**data)


def read_key_value(line, separator='='):
    key, *value = line.split(separator)
    return key.strip(), separator.join(value).strip()


def try_to_num(in_str):
    for f in (int, float):
        try:
            return f(in_str)
        except Exception as e:
            pass
    return in_str


def compare_dictionaries(dict1, dict2):
    """
    Compare two dictionaries

    :return: True if the same, False if not
    """
    if len(dict1) != len(dict2):
        return False

    for key in dict1:
        try:
            val1, val2 = dict1[key], dict2[key]
            if val1 != val2:  # different values
                return False
        except KeyError:  # different keys
            return False
        except ValueError:  # non-comparable types
            if isinstance(val1, dict):
                if not compare_dictionaries(val1, val2):
                    return False
            elif any(val1 != val2):  # Compare all values
                return False
    return True


if __name__ == "__main__":
    elongs = read_prn('../test/test_files/test1.prn')
    elongs = read_elongation('../test/test_files/test1.prn')
    elong = elongs[0]
    elong.convert_x_units_to_strain()
    elong.write('a.csv')
    open('a.out', 'w').write(str(elong.__dict__))
