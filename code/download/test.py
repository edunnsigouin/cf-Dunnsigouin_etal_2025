#!/usr/bin/env python
from ecmwfapi import ECMWFService

"""
server = ECMWFService("mars")
server.execute(
    {
    "class": "od",
    "date": "2019-01-03",
    "expver": "1",
    "hdate":"1999-01-03",
    "levtype": "sfc",
    "param": "228.128",
    "step": "0",
    "stream": "enfh",
    "time": "00:00:00",
    "type": "cf"
    },
    "target.grib")
"""


server = ECMWFService("mars")
req = {
    "class": "od",
    "date": "20210104",
    "hdate": "20200104",
    "expver": "1",
    "levtype": "sfc",
    "param": "228.128",
    "step": "0",
    "stream": "enfh",
    "time": "00",
    "type": "cf"
    }
 
kv=['{}={}'.format(k, v) for k, v in req.items()]
kv='list,output=cost,{}'.format(','.join(kv))

server.execute(kv,'target.txt')
