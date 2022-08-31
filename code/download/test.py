#!/usr/bin/env python
from ecmwfapi import ECMWFService
  
server = ECMWFService("mars")
server.execute(
    {
    "class": "od",
    "date": "20150101",
    "expver": "1",
    "levtype": "sfc",
    "param": "167.128",
    "step": "0/to/240/by/12",
    "stream": "oper",
    "time": "00",
    "type": "fc"
    },
    "target.grib")
