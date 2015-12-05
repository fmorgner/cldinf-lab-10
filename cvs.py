#!/usr/bin/python

import re

validIpAddressRegex = "(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
pattern = "^" + validIpAddressRegex + "," + validIpAddressRegex + "$"

f = open("rules.csv", "r")
lines = f.read().split("\n") # "\r\n" if needed

rule = [ ]

for line in lines:
    if re.match(pattern, line):
        rule.append(tuple(line.split(',')))

