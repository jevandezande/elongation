import itertools
import numpy as np

from datetime import datetime

from scipy import signal
from .tools import (MyIter, compare_dictionaries, read_key_value, smooth_curve,
                    try_to_num)


class Elongation:
    def __init__(self, xs, ys, gauge_length, sample_width, sample_thickness, name=None):
        """
        Container for elongation data.

        :param xs: elongation (in units of strain)
        :param ys: force (in Newtons)
        :param name: optional name for the Elongation
        """
        assert len(xs) == len(ys)

        self.xs = np.array(xs)
        self.ys = np.array(ys)
        self.gauge_length = gauge_length
        self.sample_width = sample_width  # mm
        self.sample_thickness = sample_thickness  # mm
        self.name = name

    def __eq__(self, other):
        """
        Check if two Elongation objects are equivalent.

        :param other: other Elongation object to compare with
        """
        return isinstance(other, Elongation)\
            and len(self.xs) == len(other.xs)\
            and all(self.xs == other.xs) and all(self.ys == other.ys)\
            and self.gauge_length == other.gauge_length\
            and self.sample_width == other.sample_width\
            and self.sample_thickness == other.sample_thickness\
            and self.name == other.name

    def copy(self):
        """
        Make a copy of the Elongation object.
        """
        return self.__class__(
            self.xs.copy(), self.ys.copy(),
            self.gauge_length,
            self.sample_width,
            self.sample_thickness,
            self.name
        )

    def write(self, file_name, style=None):
        """
        Write Elongation object to file.

        :param file_name: file to write to.
        :param style: format to write to (guesses based on file extension if None)
        """
        write_elongation(self, file_name, style=style)

    @property
    def max(self):
        """
        Determine the max strain and coordinate stress.

        :return: stress, max_strain
        """
        max_i = np.nanargmax(self.ys)
        return self.xs[max_i], self.ys[max_i]

    @property
    def cross_section(self):
        """
        Cross sectional area of the material.

        :return: cross_section in mm^2
        """
        return self.sample_thickness*self.sample_width  # mm^2

    def smoothed(self, box_pts=True):
        """
        Generate a smoothed version of the Elongation.

        :param box_pts: number of data points to convolve, if True, use default
        :return: smoothed Elongation
        """
        elong = self.copy()
        elong.ys = smooth_curve(self.ys, box_pts)
        return elong

    def cropped(self, start=None, end=None, shifted=True):
        """
        Crop the Elongation by x-value.

        :param start: x-value at which to start
        :param end: x-value at which to end
        :return: cropped Elongation object
        """
        start_i, end_i, i = None, None, 0

        if start is not None:
            for i, val in enumerate(self.xs):
                if val > start:
                    start_i = i
                    break

        if end is not None:
            for i, val in enumerate(self.xs[i:], start=i):
                if val > end:
                    end_i = i + 1
                    break

        return self.cropped_index(start_i, end_i, shifted)

    def cropped_index(self, start_i=None, end_i=None, shifted=True):
        """
        Crop the Elongation by index.

        :param start_i: index at which to start
        :param end_i: index at which to end
        :param shifted: shift the x-values so that they start at 0
        """
        xs = self.xs[start_i:end_i]
        ys = self.ys[start_i:end_i]

        if shifted:
            xs = xs - xs[0]

        return self.__class__(xs, ys, self.gauge_length, self.sample_width, self.sample_thickness, self.name)

    def cleaned(self, start_threshold=0.01, end_threshold=0.25, shifted=True):
        """
        Remove the slack at the beginning and post-break at the end.

        :param start_threshold: threshold of max for starting
        :param end_threshold: threshold of max for break
        """
        start_i, end_i = None, None

        max_i = np.nanargmax(self.ys)
        max_y = self.ys[max_i]

        if start_threshold is not None:
            # includes the value before threshold is met
            for i, y in enumerate(self.ys[1:]):
                if y > max_y*start_threshold:
                    start_i = i
                    break

        if end_threshold is not None:
            for i, y in enumerate(self.ys[max_i:], start=max_i):
                if y < max_y*end_threshold:
                    end_i = i
                    break

        return self.cropped_index(start_i, end_i, shifted)

    @property
    def youngs_modulus(self, x_limit=None):
        """
        Determine the Young's modulus of the Elongation.

        Modulus is calculated as the peak of the derivative of the stress strain curve.

        :return: Young's modulus (units of Pa)
        """
        if x_limit is not None:
            raise NotImplementedError('Limits on x not yet implemented, see youngs_modulus_array().')

        return max(self.youngs_modulus_array)

    @property
    def youngs_modulus_array(self):
        """
        Determine the Young's modulus at all points on the Elongation.

        :return: Young's modulus array (units of Pa)
        """
        return self.derivative()/self.cross_section  # N/L·ΔL * A

    def derivative(self):
        """
        :return: derivative
        """
        return np.diff(self.ys)/np.diff(self.xs)  # N/L·ΔL

    def peaks(self, **kwargs):
        """
        Finds the location of peaks in the Elongation.

        Utilizes scipy.signal.find_peaks and the parameters therein.

        :param **kwargs: kwargs for scipy.signal.find_peaks
        :return: peak x-values, properties
        """
        peaks, properties = self.peak_indices(**kwargs)
        return self.xs[peaks], properties

    def peak_indices(self, **kwargs):
        """
        Finds the location of peaks in the Elongation.

        Utilizes scipy.signal.find_peaks and the parameters therein.

        :param **kwargs: kwargs for scipy.signal.find_peaks
        :return: peak indices, properties
        """
        kwarg_defaults = {
            'width': 5,  # ensure small spikes are ignored
        }
        kwarg_defaults.update(kwargs)
        return signal.find_peaks(self.ys, **kwarg_defaults)

    def break_index(self, **kwargs):
        """
        Determine the strain index of break.

        Break is defined herein as the last peak in the stress/strain curve.

        :param **kwargs: see peaks()
        :return: index of break
        """
        return self.peak_indices(**kwargs)[0][-1]

    def break_elongation(self, **kwargs):
        return self.xs[self.break_index(**kwargs)]

    def break_load(self, **kwargs):
        return self.ys[self.break_index(**kwargs)]

    def break_strength(self, **kwargs):
        return self.break_load(**kwargs)/self.cross_section

    def yield_index(self, **kwargs):
        """
        Determine the location and force at yield.

        Yield is defined herein as the first peak in the stress/strain curve.

        :param **kwargs: see peaks()
        :return: index of yield
        """
        return self.peak_indices(**kwargs)[0][0]

    def yield_elongation(self, **kwargs):
        return self.xs[self.yield_index(**kwargs)]

    def yield_load(self, **kwargs):
        return self.ys[self.yield_index(**kwargs)]

    def yield_strength(self, **kwargs):
        return self.yield_load(**kwargs)/self.cross_section


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
        raise NotImplementedError()
    else:
        raise NotImplementedError()


def write_csv(elongation, file_name):
    """
    Write Elongation object to a csv file.

    :param: Elongation object
    :param file_name: name of the file to be written to
    """
    e = elongation

    with open(file_name, 'w') as f:
        f.write(f"""\
Break Load, {e.break_load()}
Break Strength, {e.break_strength()}
Break Elongation, {e.break_elongation()}
Yield Load, {e.yield_load()}
Yield Strength, {e.yield_strength()}
Yield Elongation, {e.yield_elongation()}
Gauge Length, {e.gauge_length}
Sample Width, {e.sample_width}
Sample Thickness, {e.sample_thickness}

Points
   mm,       N""")
        for x, y in zip(e.xs, e.ys):
            f.write(f'\n{x:>8.4f}, {y:>8.4f}')


def read_elongations(file_names):
    """
    Read an iterable of elongation files.

    :param file_names: name of elongation files
    :return: list of Elongation objects.
    """
    return list(itertools.chain(*(read_elongation(f) for f in file_names)))


def read_elongation(file_name):
    """
    Read an elongation file.

    :param file_name: name of the file
    :return: list of Elongation objects
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

    :param file_name: name of the file
    :return: list of Elongation objects

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
            data['x_units'] = 's'
        if data['y_units'] == 'Newtons':
            data['y_units'] = 'N'
        if results['date']:
            results['date'] = datetime.strptime(results['date'], '%d %b, %Y')

        xs = data['xs']*float(data['crosshead_speed'])
        elongations.append(
            Elongation(
                xs, data['ys'],
                float(data['gauge_length']),
                float(data['sample_width']),
                float(data['sample_thickness']),
                None
            )
        )

    return elongations


def read_csv(file_name):
    """
    Read a csv file.

    :param file_name: name of the file
    :return: list of Elongation objects (currently only a single item in list).
    """
    data = {}
    with open(file_name) as f:
        f = MyIter(f)
        try:
            for line in f:
                if not line.strip():
                    continue
                if line == 'Points\n':
                    break
                key, val = read_key_value(line, separator=',')
                key = key.lower().replace(' ', '_')
                data[key] = val

            x_units, y_units = next(f).split(',')
            data['x_units'], data['y_units'] = x_units.strip(), y_units.strip()

            xs, ys = [], []
            for line in f:
                x, y = line.split(',')
                xs.append(float(x.strip()))
                ys.append(float(y.strip()))
        except Exception as e:
            print(f'Error on line {f._index}')
            print(f._line)
            raise e

    elong = Elongation(
        np.array(xs), np.array(ys),
        float(data['gauge_length']),
        float(data['sample_width']),
        float(data['sample_thickness'])
    )
    return [elong]


if __name__ == "__main__":
    elongs = read_prn('../test/test_files/test1.prn')
    elongs = read_elongation('../test/test_files/test1.prn')
    elong = elongs[0]
    elong.write('a.csv')
    open('a.out', 'w').write(str(elong.__dict__))
