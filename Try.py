from random import randint
from math import sin, cos, sqrt, atan2, radians
import params as params
import pyrebase
from flask import Flask, render_template, request, flash
import smtplib
import urllib
import requests, time

def get_distance():
    R = 6373.0
    latr = radians(19.0962884)
    lonr = radians(72.8483799)
    laty = radians(19.1502437)
    lony = radians(72.8342294)
    dlon = lony - lonr
    dlat = laty - latr
    a = sin(dlat / 2) * 2 + cos(latr) * cos(laty) * sin(dlon / 2) * 2
    a2 = sin(dlat / 2) ** 2 + cos(latr) * cos(laty) * sin(dlon / 2) ** 2

    c = 2 * atan2(sqrt(a2),sqrt(1 - a2))
    distance = R * c
    print(distance)


get_distance()