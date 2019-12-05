import numpy as np

from datetime import datetime

from .tools import MyIter, compare_dictionaries, read_key_value, try_to_num


class Elongation:
    def __init__(self, xs, ys, x_units, y_units, **other):
        """
        Container for elongation data
        :param xs: x-values (elongation)
        :param ys: y-values (force)
        :param x_units, y_units: units for x and y
        :param **other: other data to be saved
        """
        self.xs = xs
        self.x_units = x_units
        self.ys = ys
        self.y_units = y_units
        self.break_load = other['break_load']
        self.break_elongation = other['break_elongation']
        self.break_strength = other['break_strength']
        self.crosshead_speed = other['crosshead_speed']
        self.gauge_length = other['gauge_length']
        self.yield_strength = other['yield_strength']
        self.yield_load = other['yield_load']
        self.data = other

    def __eq__(self, other):
        """
        Check if two elongation objects are equivalent.

        :param other: other Elongation objects to compare to
        """
        compare_dictionaries(self.data, other.data)

        return all(self.xs == other.xs) and all(self.ys == other.ys) \
            and self.x_units == other.x_units and self.y_units == other.y_units

    def write(self, file_name, style=None):
        """
        Write elongation object to file.

        :param file_name: file to write to.
        :param style: format to write to (guesses based on file extension if None)
        """
        write_elongation(self, file_name, style=style)

    def convert_x_units(self, to, factor):
        """
        Convert the x_units.

        :param to: units to convert to
        :param factor: factor to multiply by
        """
        self.x_units = to
        self.xs *= factor
        self.break_elongation *= factor

    def convert_y_units(self, to, factor):
        """
        Convert the y_units.

        :param to: units to convert to
        :param factor: factor to multiply by
        """
        self.x_units = to
        self.ys *= factor
        self.break_load *= factor
        self.break_strength *= factor
        self.yield_strength *= factor
        self.yield_load *= factor

    def convert_x_units_to_strain(self):
        """
        Convert the x_units to strain (ΔL/L).
        """
        factor = None
        if self.x_units == 'strain':
            return
        elif self.x_units in ['seconds', 'Secs.']:
            factor = self.crosshead_speed / self.gauge_length
        elif self.x_units in ['mm', 'cm', 'm', 'in', 'ft']:
            factor = 1 / self.gauge_length
        else:
            raise NotImplementedError(f'Converting from {self.x_units} to strain is no yet implemented.')

        self.convert_x_units('strain', factor)

    @property
    def modulus(self):
        modulus = 1

        return modulus

    def derivative(self, units='N/m'):
        """
        Take the derivative of the curve, first converts to the corresponding units.

        :param units: units to be used. Derivative is with respect to numerator and denominator.
        :return derivative:
        """
        if units == 'N/m':
            assert (self.x_units == 'm') and (self.y_units == 'N')
            return np.diff(self.y)/np.diff(self.x)

    def cropped(self, start, end):
        """
        Crop the elongation by x-value

        :param start: x-value at which to start
        :param end: x-value at which to end
        :return: cropped Elongation object
        """
        start_i = self.xs.index(start) if not start is None else None
        end_i = self.xs.index(end) if not end is None else None

        return self.cropped_index(start_i, end_i)

    def cropped_index(self, start_i=None, end_i=None):
        """
        Crop the elongation by index

        :param start: x-value at which to start
        :param end: x-value at which to end
        """
        elong = Elongation(**self.__dict__)
        elong.xs = self.xs[start_i:end_i]
        elong.ys = self.ys[start_i:end_i]
        return elong

    def cleaned(self, start_threshold=None, end_threshold=0.25):
        """
        Remove the slack at the beginning and post-break at the end.

        :param start_threshold: threshold for starting, ignores if False
        :param end_threshold: threshold for break, ignores if False
        """
        if not start_threshold is None:
            raise NotImplementedError('Start_threshold is not yet implemented')

        start_i = None

        max_i = np.argmax(self.ys)
        max_x, max_y = self.xs[max_i], self.max_ys[max_i]
        end_i = bisect(self.ys, 0.25*max_y, lo=max_i) if not end_threshold is None else None

        return self.cropped_index(start_i, end_i)


def write_elongation(elongation, file_name, style=None):
    """
    Write Elongation object to file.

    :param: Elongation object
    :param file_name: name of the file to be written to
    :param style: format to write to (guesses based on file extension if None)
    """
    style = file_name.split('.')[-1] if style is None else style

    if style == 'csv':
        write_csv(elongation, file_name)
    elif style == 'prn':
        write_prn(elongation, file_name)
    else:
        raise NotImplementedError()


def write_csv(elongation, file_name):
    """
    Write Elongation object to a CSV file.

    :param: Elongation object
    :param file_name: name of the file to be written to
    """
    e = elongation
    with open(file_name, 'w') as f:
        f.write("""\
Thickness, {thickness}
Break Load, {break_load}
Break Strength, {break_strength}
Break Elongation, {break_elongation}
Crosshead Speed, {crosshead_speed}
Gauge Length, {gauge_length}
Yield Strength, {yield_strength}
Yield Load, {yield_load}

Points
{x_units},   {y_units}
""".format(x_units=e.x_units, y_units=e.y_units, **e.data))
        for x, y in zip(e.xs, e.ys):
            f.write(f'{x:>8.4f}, {y:>8.4f}\n')

def write_prn(elongation, file_name):
    """
    Write Elongation object to a prn file.

    :param: Elongation object
    :param file_name: name of the file to be written to
    """
    e = elongation
    with open(file_name, 'w') as f:
        f.write("""prn:13|
subtype = MT2500
Doc={MT2500:14|
  Film={12.1|
""" +
"""\
    Test_Mode = {Test_Mode}
    Setup_Name = {Setup_Name}
    Unit_System = {Unit_System}
    Graph_Mode = {Graph_Mode}
    Sample_Length = {Sample_Length}
    CrossheadVlcty = {CrossheadVlcty}
    VelocityUnitId = {VelocityUnitId}
    CrossheadSpeed = {CrossheadSpeed}
    Loadcell_Mode = {Loadcell_Mode}
    Loadcell_Type = {Loadcell_Type}
    Start_Threshold = {Start_Threshold}
    Stop_Threshold = {Stop_Threshold}
    Auto_Stop = {Auto_Stop}
    Auto_Return = {Auto_Return}
    ExtnsnResetOnStart = {ExtnsnResetOnStart}
    Yield_Type = {Yield_Type}
    COF_Sled_Load = {COF_Sled_Load}
    }}
""".format(**e.data['film_data']) +
"""\
  Test_Info={{2|
    Color = {Color}
    Order_Id = {Order_Id}
    Technician = {Technician}
    Test_Method = {Test_Method}
    Sample_Conditioning = {Sample_Conditioning}
    Test_Conditions = {Test_Conditions}
    Product_Name = {Product_Name}
    Test_Direction = {Test_Direction}
    }}
""".format(**e.data['test_info']) +
"""\
  Test_Data=(
    {{6|
      Crosshead_speed = {crosshead_speed}
      X_unit = {x_units}
      Y_unit = {y_units}
      Sample_Thkness = {sample_thickness}
      Sample_Width = {sample_width}
      Grip_Separation = {gauge_length}
      Start_Threshhold = {start_threshhold}
      Stop_Threshhold = {stop_threshhold}
      Number_Of_Points = {number_of_points}
      Points = [""".format(number_of_points=len(e.xs), x_units=e.x_units, y_units=e.y_units, **e.data) +
''.join(f'   {x:> 8.4f}, {y:> 8.4f}\n' for x, y in zip(e.xs, e.ys)) +
"""\
         ]
      }},
    )
  Test_Results=(
    {{6|
      TestDate = {date}
      Length_Cnvrsn = {length_conversion}
      Force_Cnvrsn = {force_conversion}
      LoadCell_Capacity = {loadcell_capacity}
      LoadCell_CpctyUnit = {loadcell_capacity_unit}
      LoadCell_BitsOfReso = {loadcell_bits_of_resolution}
      Analysis={{ATensile:1|
        Slack_time = {slack_time}
        SampleThickness = {sample_thickness}
        BreakLoad = {break_load}
        BreakStrength = {break_strength}
        BreakElongation = {break_elongation}
        BreakPctElongation = {break_percent_elongation}
        YieldStrength1 = {yield_strength}
        YieldLoad1 = {yield_load}
        }}
      }},
    )
  }}
""".format(**e.data)
)


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


if __name__ == "__main__":
    elongs = read_prn('../test/test_files/test1.prn')
    elongs = read_elongation('../test/test_files/test1.prn')
    elong = elongs[0]
    elong.convert_x_units_to_strain()
    elong.write('a.csv')
    open('a.out', 'w').write(str(elong.__dict__))
