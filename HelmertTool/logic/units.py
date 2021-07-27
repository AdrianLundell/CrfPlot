from collections import namedtuple

Unit = namedtuple("Unit", ["symbol", "convertion_factor"])

#Length units
nano_meter = Unit("nm", 10**9)
micro_meter = Unit("µm", 10**6)
milli_meter = Unit("mm", 10**3)
centi_meter = Unit("cm", 10**2)
meter = Unit("m", 1)

#Angles
nano_radian = Unit("nrad", 10**9)
micro_arcsecond = Unit("mas", 206264.806 * 10**3)
timesecond = Unit("µts", 13750.9871*10**6)