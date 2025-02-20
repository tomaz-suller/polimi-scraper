from datetime import date

import requests
from bs4 import BeautifulSoup

from polimi_scraper.config import OCCUPANCY_URL


def soup(url: str, params: dict = {}) -> BeautifulSoup:
    return BeautifulSoup(
        requests.get(url, params=params, timeout=5).text, "html.parser"
    )


def occupancy_soup(sede_id: str, date: date) -> BeautifulSoup:
    parameters = {
        "csic": sede_id,
        "categoria": "tutte",
        "tipologia": "tutte",
        "giorno_day": date.day,
        "giorno_month": date.month,
        "giorno_year": date.year,
        "evn_visualizza": "",
    }
    return soup(OCCUPANCY_URL, parameters)
