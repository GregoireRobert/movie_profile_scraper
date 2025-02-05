import re
from signal import signal
from typing import List

import requests
from bs4 import BeautifulSoup
from requests import JSONDecodeError


class LetterboxdScraper:
    PAGINATION_PAGE_SELECTOR = "div.pagination div.paginate-pages li.paginate-page"
    FILM_POSTER_SELECTOR = "div.film-poster"
    POSTER_CONTAINER_SELECTOR = "li.poster-container"
    URL_PROFILE_FORMATTER = "https://letterboxd.com/{user_id}/"
    DATA_FILM_SLUG = "data-film-slug"
    def __init__(self):
        pass

    def get_profile_movies(self, user_id):
        profile_url = LetterboxdScraper.URL_PROFILE_FORMATTER.format(user_id=user_id)
        movie_urls = tmdb_urls(self.scrap_profile_movies(profile_url))
        return movie_urls

    def scrap_profile_movies(self, url):
        max_page_reached = False
        page_counter = 1
        film_urls = []
        while not max_page_reached:
            formatted_url = f"{url}/films/by/date/size/large/page/{page_counter}/"
            page_source = self.get_movies_page_source(formatted_url, page_counter)
            if page_source:
                film_urls.extend(self.scrap_movie_page(page_source))
            else:
                max_page_reached = True
            page_counter += 1
        return film_urls

    def page_exists(self, soup: BeautifulSoup, counter: int):
        paginate_page_elems = soup.select(LetterboxdScraper.PAGINATION_PAGE_SELECTOR)
        return counter <= len(paginate_page_elems)

    def get_movies_page_source(self, url, counter):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup if self.page_exists(soup, counter) else None

    def scrap_movie_page(self, soup: BeautifulSoup) -> List[dict[str, str]]:

        poster_containers = soup.select(LetterboxdScraper.POSTER_CONTAINER_SELECTOR)
        film_urls = []
        for container in poster_containers:
            film_url = None
            film_poster = container.select_one(LetterboxdScraper.FILM_POSTER_SELECTOR)
            if film_poster:
                film_url = film_poster.attrs.get(LetterboxdScraper.DATA_FILM_SLUG)
            film_datetime = None
            time = container.select_one("time")
            if time:
                film_datetime = time.attrs.get("datetime")
            if film_url:

                film_urls.append({"url": film_url, "added": film_datetime})
        return film_urls


def formatted_values_query(site_ids: List[str]):
    formatted_ids = []
    for site_uid in site_ids:
        formatted_ids.append('\"' + site_uid.strip() + '\"')
    values = " ".join(formatted_ids)
    query = WikidataQuery.MULTIPLE_IMDB_IDS_QUERY.format(values=values)
    return query


class WikidataQuery:
    BOT_HEADERS = {
        "User-Agent": "MoviePickerBot/1.0 (https://www.greg-rbrt.fr/)",
        "Accept": "application/sparql-results+json"
    }
    TMDB_ID_QUERY = """SELECT ?tmdbId
   WHERE {{
    ?wdId ?p ?statement .
    ?statement ps:P6127 "{site_uid}" .
    ?wdId wdt:P4947 ?tmdbId .
}}
"""
    MULTIPLE_IMDB_IDS_QUERY = """SELECT ?tmdbId
   WHERE {{
     VALUES ?siteUid {{ {values} }}
    ?wdId ?p ?statement .
    ?statement ps:P6127 ?siteUid .
    ?wdId wdt:P4947 ?tmdbId .
}}"""

    TMDB_FORMATTER_URL = "https://www.themoviedb.org/movie/{}"

    def __init__(self):
        pass

    def get_tmdb_ids(self, site_ids: str | List[str]) -> List[str]:
        site_ids = [site_ids] if isinstance(site_ids, str) else site_ids
        query = formatted_values_query(site_ids)
        tmdb_ids = []
        try:
            response = requests.get("https://query.wikidata.org/sparql?query=" + query,
                                    headers=WikidataQuery.BOT_HEADERS)
            # match response.status_code:
            #     case 200:
            #         pass
            #     case 429:
            #         pass
            #     case 403:
            #         pass
            results = response.json()

            if results["results"]["bindings"]:
                for tmdb_id_dict in results["results"]["bindings"]:
                    tmdb_id = tmdb_id_dict["tmdbId"]["value"]
                    # tmdb_url = WikidataQuery.TMDB_FORMATTER_URL.format(tmdb_id)

                    tmdb_ids.append(tmdb_id)


        except JSONDecodeError:
            pass
        return tmdb_ids


def tmdb_urls(tmdb_dicts: List[dict[str, str]]) -> List[dict[str, str]]:
    FORMATTER_URL = "https://www.themoviedb.org/movie/{}"
    data = []
    for tmdb_dict in tmdb_dicts:
        url = FORMATTER_URL.format(tmdb_dict["url"])
        tmdb_dict["url"] = url
        data.append(tmdb_dict)

    return data


def main():
    scraper = LetterboxdScraper()
    query = WikidataQuery()

    movie_slugs = scraper.get_profile_movies("gregz2")


if __name__ == "__main__":
    main()