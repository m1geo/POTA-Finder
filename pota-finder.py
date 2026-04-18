# -*- coding: utf-8 -*-
"""
POTA Finder, V1.00
27/11/2024
George Smart, M1GEO
https://www.george-smart.co.uk/2024/11/finding-local-unactivated-potas/
https://github.com/m1geo/POTA-Finder

Script takes a POTA parklist country file CSV export and your location and returns POTAs that match your activation criteria
"""

## Command Line Parsing
import sys
import geopy.distance
import csv
import argparse
import maidenhead as mh

## Parse Inputs
parser = argparse.ArgumentParser(
                    prog=sys.argv[0],
                    description='POTA Finder: Filter POTA ParkList CSV exports to find rarely (never) activated Parks!',
                    epilog='George Smart, M1GEO. V1.00. 27/11/2024. https://github.com/m1geo/POTA-Finder')
parser.add_argument('parklist_export', help='The Parklist Export CSV file from https://pota.app/#/parklist')
parser.add_argument('-q', '--qth', required=True, help='Your reference location, can be a QRA locator like \'AA00bb\' or a lat,log like \'00.000,00.000\'. Use comma to separate lat,long. Numbers are negative for south or west.')
parser.add_argument('-s', '--show-max', type=int, default=3, help='Maximum results to print out')
parser.add_argument('-m', '--max-activations', type=int, default=-1, help='Maximum activations to display')
parser.add_argument('-u', '--show-urls', action='store_true', default=False, help='Output URLs to be clicked on')
args = parser.parse_args()

progname = sys.argv[0]
potafile = args.parklist_export
qthlocation = args.qth
showcount = args.show_max
maxactivations = args.max_activations
showurls = args.show_urls

## Location varables
myqth = (None,None)

## Convert Maidenhead Locator
if any(c.isalpha() for c in qthlocation):
    myqth = mh.to_location(qthlocation, center=True)

## Convert "Lat,Lon" String
if "," in qthlocation:
    split = qthlocation.strip().split(',')
    qthlat = float(split[0])
    qthlon = float(split[1])
    myqth = (qthlat,qthlon)

print("POTA Finder, V1.00")
print("27/11/2024")
print("George Smart, M1GEO")
print("Home QTH - QRA: %s, Lat: %f, Lon: %f" % (qthlocation, myqth[0], myqth[1]))
print("")

class ParkObj:
    def __init__(self, reference, name, latitude, longitude, grid, locationDesc, attempts, activations, qsos, my_activations, my_hunted_qsos):
        self.reference = reference
        self.name = name
        self.latlon = (float(latitude), float(longitude))
        self.grid = grid
        self.locationDesc = locationDesc
        self.attempts = self._checkinp(attempts)
        self.activations = self._checkinp(activations)
        self.qsos = self._checkinp(qsos)
        self.my_activations = self._checkinp(my_activations)
        self.my_hunted_qsos = self._checkinp(my_hunted_qsos)
        self.distance = geopy.distance.distance(myqth, self.latlon).km # also ".miles"
        #print("%s is %.1f km away." % (self.name, self.distance))
    
    def __str__(self):
        str = ""
        str += "%s / %s:    %s\n" % (self.locationDesc, self.reference, self.name)
        if showurls:
            str += ("\tPark Link:   https://pota.app/#/park/%s\n" % (self.reference))
        str += "\tLocation:    %f %f (%s)\n" % (self.latlon[0], self.latlon[1], self.grid)
        str += "\tDistance:    %.1f km from %s\n" % (self.distance, qthlocation)
        str += "\tAttempts:    %u (%u qsos)\n" % (self.attempts, self.qsos)
        str += "\tActivations: %u" % (self.activations)
        if self.my_activations > 0:
            str += " (%u by me)" % (self.my_activations)
        str += "\n"
        if self.my_hunted_qsos > 0:
            str += ("\tMy Hunted:   %u\n" % (self.my_hunted_qsos))
        return str

    def _checkinp(self, strval):
        """Check that the input string can be parsed as an integer, else return -1"""
        try:
            val = int(strval)
        except:
            val = -1
        return val

## Read in CSV
# CSV FORMAT: reference,name,latitude,longitude,grid,locationDesc,attempts,activations,qsos,my_activations,my_hunted_qsos
park_list = []
with open(potafile, newline='',encoding='utf-8') as csvfile:
    potalist = csv.reader(csvfile)
    for park in potalist:
        if "reference" not in park:
            park_list.append(ParkObj(park[0],park[1],park[2],park[3],park[4],park[5],park[6],park[7],park[8],park[9],park[10]))
print("Imported %u parks from database." % (len(park_list)))

## Sort the Park List
park_list.sort(key=lambda x: x.distance, reverse=False)

## Filter the Park List
if maxactivations > -1:
    park_list = list(filter(lambda x: x.activations <= maxactivations, park_list))

## Print requested
print("Showing %u closest parks (%s)\n" % (showcount, ("filtered: maximum of %u activations" % (maxactivations)) if maxactivations >= 0 else "unfiltered"))
showcount = len(park_list) + 1 if showcount == 0 else showcount
for park in park_list[0:showcount]:
    print(park)
    
print("Showed %u parks out of %u matching." % (len(park_list[0:showcount]), len(park_list)))
