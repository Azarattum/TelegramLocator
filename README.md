# Telegram Locator
Python script that creates a precise map of people around you

## Features:
  - Collects data using **people nearby** telegram feature
  - [Trilaterates](https://en.wikipedia.org/wiki/True_range_multilateration) the exact position of each person
  - Renders all the results on *map.html*

### Example:
[![example.jpg](https://i.postimg.cc/7Zcjm5kN/example.jpg)](https://postimg.cc/DSrCzymW)

### Usage: 
1. Install dependencies:
```sh
python -m pip install -r ./requirements.txt
```
2. Run script:
```sh
python ./locate.py --number NUMBER --latitude LATITUDE --longitude LONGITUDE [--offset OFFSET] [--help]
```
3. Authenticate (if prompted):
```
Code: 
Password: 
```

### Arguments:
| Long                  | Short         | Description                                                |
| --------------------- | ------------- | ---------------------------------------------------------- |
| --help                | -h            | Show help message                                          |
| --number NUMBER       | -n NUMBER     | Telephone number (aka Telegram login)                      |
| --latitude LATITUDE   | -la LATITUDE  | Latitude of your starting location                         |
| --longitude LONGITUDE | -lo LONGITUDE | Longitude of your starting location                        |
| --offset OFFSET       | -o OFFSET     | Trilateration scanning offset in degrees (default: 0.0007) |

### Third-party libraries:
* [Telethon](https://github.com/LonamiWebs/Telethon) - Pure Python 3 MTProto API Telegram client library.
* [gmplot](https://github.com/gmplot/gmplot) - A matplotlib-like interface to render all the data you'd like on top of Google Maps.