#!/usr/bin/env python
from ecmwfapi import *

server = ECMWFService("mars")

dic = {
    'class': 'od',
    'expver': '1',
    'stream': 'enfh',
    'time': '00:00:00',
    'param': '228.128',
    'levtype': 'sfc',
    'step': '0',
    'number':'1',
    'type': 'pf',
    'date': '2021-01-04',
    'hdate':'2020-01-04'
}

path     = '/nird/projects/NS9853K/DATA/S2S/MARS/hindcast/ECMWF/sfc/tp/'
filename = 'test.grib'

server.execute(dic, path + filename)



