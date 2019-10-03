import numpy as np


class Elongation:
    def __init__(self, xs, ys, x_units, y_units, **other):
        """
        Container for elongation data
        """
        self.xs = xs
        self.x_units = x_units
        self.ys = ys
        self.y_units = y_units
        self.__dict__ = {**other, **self.__dict__}

    def write(self, file_name):
        xs, ys = self.xs, self.ys
        extension = file_name.split('.')[-1]
        with open(file_name, 'w') as f:
            if extension == 'csv':
                f.write(f"""\
Thickness, {self.thickness}
Break Load, {self.break_load}
Crosshead Speed, {self.crosshead_speed}
Break Strength, {self.break_strength}
Yield Strength, {self.yield_strength}
Yield Load, {self.yield_load}

Points
{self.x_units},   {self.y_units}
""")
                for x, y in zip(xs, ys):
                    f.write(f'{x:>8.4f}, {y:>8.4f}\n')
            if extension == 'prn':
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
""".format(**self.film_data) +
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
""".format(**self.test_info) +
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
      Points = [""".format(**self.__dict__, number_of_points=len(self.xs)) +
''.join(f'   {x:> 8.4f}, {y:> 8.4f}\n' for x, y in zip(self.xs, self.ys)) +
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
""".format(**self.__dict__)
)

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
        self.yield_strength1 *= factor
        self.yield_load1 *= factor

    def convert_x_units_to_strain(self):
        if self.x_units == 'strain':
            return
        elif self.x_units in ['seconds', 'Secs.']:
            factor = self.crosshead_speed / self.gauge_length
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
