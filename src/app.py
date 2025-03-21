from flask import Flask, jsonify, request
from recipe_scrapers import scrape_html, SCRAPERS
import logging

import requests


app = Flask(__name__)
# Variable "application" is picked up by uWSGI server
application = app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')


@app.get("/api/v1/scrape-recipe/supported-hosts")
def get_supported_hosts():
    return jsonify(list(SCRAPERS.keys())), 200


@app.get("/api/v1/scrape-recipe")
def import_recipe():
    scrape_url = request.args.get("url")

    if not scrape_url:
        return jsonify({"error": "No recipe provided via parameter 'url'"}), 400

    try: 
        html = requests.get(scrape_url, headers={"User-Agent": "Recipe Scraper"}).content
    except Exception as e:
        logging.error("Error retrieving html of recipe "+ scrape_url)
    
    try:
        scraper = scrape_html(html, scrape_url, supported_only=False,online=False )
    except Exception as e:
        logging.warn("Error while scraping " + scrape_url)
        logging.info("Trying with wild mode")
        try:
            scraper = scrape_html(html, scrape_url, supported_only=False, online=False)
        except Exception as e:
            logging.error("Error retrying with wild mode")
            return jsonify({"error": "Given recipe url not supported"}), 501

    response = {
        "language": get_info(scraper, "language"),
        "title": get_info(scraper, "title"),
        "category": get_info(scraper, "category"),
        "author": get_info(scraper, "author"),
        "total_time": get_info(scraper, "total_time"),
        "cook_time": get_info(scraper, "cook_time"),
        "prep_time": get_info(scraper, "prep_time"),
        "yields": get_info(scraper, "yields"),
        "image": get_info(scraper, "image"),
        "ingredients": get_info(scraper, "ingredients"),
        "nutrients": get_info(scraper, "nutrients"),
        "instructions": get_info(scraper, "instructions"),
        "ratings": get_info(scraper, "ratings"),
        "cuisine": get_info(scraper, "cuisine"),
        "host": get_info(scraper, "host"),
        "links": get_info(scraper, "links"),
    }
    return jsonify(response)


def get_info(scraper, attribute):
    try:
        method = getattr(scraper, attribute, None)
        return method()
    except Exception as e:
        logging.warn(
            "Error getting info from scraper for attribute " + attribute)
        return ""
