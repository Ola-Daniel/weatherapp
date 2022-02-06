import argparse
from configparser import ConfigParser
from urllib import error, parse, request
from pprint import pp
import json
import sys
import style

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

#    Weather condition codes
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)



def read_user_cli_args():
    """
    Handles the CLI user interactions.

    Returns:
    argparse.Namespace: Populated namespace object

    """
    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city"
    )
    parser.add_argument(
        "city", nargs="+", type=str, help="enter the city name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="display the temperature in imperial units",
    )
    return parser.parse_args()


def _get_api_key():
    """
    Fetch the API key from your configuration file.
    Expects a configuration file named "secrets.ini" with structure:
    [openweather]
    api_key=<api_key>

    """

    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


def build_weather_query(city_input, imperial=False):
    """
    Builds the URL for an API request to OpenWeather's weather's API.
    :param city_input: ([str]): Name of a city as collected by argparse
    :param imperial: (bool): whether or not to use imperial units for temperature
    :return: str: URL formatted for a call to OpenWeather's city name endpoint
    """
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url


def get_weather_data(query_url):
    """
    Makes an API request to a URL and returns the data as a Python object.

    :param query_url:  (str) URL formateed for OpenWeather's city name endpoint

    :return:
    dict: Weather information for a specific city
    """
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401: # Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:    #not found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong...({http_error.code})")

    data = response.read()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_weather_info(weather_data, imperial=False):
    city = weather_data["name"]
    weather_id = weather_data['weather'][0]["id"]
    weather_description = weather_data['weather'][0]["description"]
    temperature = weather_data["main"]["temp"]

    style.change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}", end="")
    style.change_color(style.RESET)

    weather_symbol, color = _select_weather_display_params(weather_id)

    style.change_color(color)
    print(f"\t{weather_symbol}", end=" ")
    print(
        f"\t{weather_description.capitalize():^{style.PADDING}}",
        end=" ",
    )
    style.change_color(style.RESET)
    print(f"({temperature}o{'F' if imperial else 'C'})")


def _select_weather_display_params(weather_id):
    if weather_id in THUNDERSTORM:
        display_params = ("\U0001F329", style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("\U0001F326", style.CYAN)
    elif weather_id in RAIN:
        display_params = ("\U0001F326", style.BLUE)
    elif weather_id in SNOW:
        display_params = ("\U0001F328", style.WHITE)
    elif weather_id in ATMOSPHERE:
        display_params = ("\U0001F343", style.BLUE)
    elif weather_id in CLEAR:
        display_params = ("\U0001F324", style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("\U0001F325", style.WHITE)
    else:
        display_params = ("\U0001F308", style.RESET)
    return display_params


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)
