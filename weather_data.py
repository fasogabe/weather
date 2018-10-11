#!/usr/bin/env python

# weather_data.py
# Fabian Gaspero-Beckstrom

'''
    This is a basic script that uses the wunderground.com api to retreive
    json files containing weather data. The data is then put into a bar graph
    using pygal, which is rendered to an svg file in the local directory.
'''

import urllib2
import json
import pygal
import string

_debug = False

api_key = 'd49a94a65ea775e9'

base_url = 'http://api.wunderground.com/api/%s/' % (api_key)

locations = ['OR/Portland','WA/Seattle','VT/Burlington','IL/Chicago','TX/Austin','PA/Philadelphia','FL/Miami']
temps = []

def main():

    for loc in locations:
        data = retreive_json('conditions', loc)
        temp = get_temp(data)

        if _debug:
            info = "City: %s\nTemperature: %s\n" % (loc, temp)
            print info

        temps.append(temp)

    bar_chart = pygal.Bar()
    bar_chart.x_labels = map(str, locations)
    bar_chart.add('Temperature',temps)
    bar_chart.render_to_file('temps.svg')




# Retreives JSON file. Takes category and location as arguments.
def retreive_json(category, location):

    url = base_url + category + '/q/' + location + '.json'   # build url string

    json_file = urllib2.urlopen(url)         # request json file
    data = json.loads(json_file.read())    # load/decode json file
    json_file.close()

    if _debug:
        print json.dumps(data, indent=4)

    return data


def get_temp(data):

    temp = data['current_observation']['temp_f']
    return temp



if __name__ = "__main__":
    main()














