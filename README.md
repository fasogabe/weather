# weather and server code

#### http_server.py and proxy_server.py

> These scripts use the socket module from the python standard library to run a local server
> They each run weather_data as well, in order to have an svg file to host.

#### weather-data.py

> This script uses a wunderground.com api to retreive current weather information.
> It then uses pygal to create a bar graph of various temperatures across the US.

**Note:** pygal must be installed for these scripts to work.
