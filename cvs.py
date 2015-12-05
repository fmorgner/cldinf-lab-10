#!/usr/bin/python

f = open("rules.csv", "r")
lines = f.read().split("\n") # "\r\n" if needed

rule = [ ]

for line in lines:
    if line != "":
        rule.append(tuple(line.split(',')))

