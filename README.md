# fmio-server
Automated FMI open data scraper, processor and database

This is the backend used in the sataako-service.

Heroku: https://sataako2017.herokuapp.com/

## Example queries
- View rainfall map: https://sataako2017.herokuapp.com/rainmap
- Helsinki centrum rain data: https://sataako2017.herokuapp.com/forecast/24.938379/60.169856
- Kumpula campus rain data: https://sataako2017.herokuapp.com/forecast/24.961839/60.204419

## Setup
Requires python 2.7 and pip.
After installing them install required packages with `pip install -r requirements.txt`.

Set environment variables:
- `FMI_API_KEY` is a key for the [weather data](#weather-data)
- `LD_LIBRARY_PATH` should be appended with a path to the `pyoptflow` folder. For example `LD_LIBRARY_PATH=${LD_LIBRARY_PATH}/path/to/pyoptflow:`

Run the server with `./run_server.sh`.

## Data sources
### Weather data
- Source: https://en.ilmatieteenlaitos.fi/open-data
- License: Creative Commons Attribution 4.0 International 

### Base maps
- Source: http://www.naturalearthdata.com/
- License: Public domain
