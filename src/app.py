from flask import Flask, jsonify, request
from recipe_scrapers import scrape_me
import logging


app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')


@app.get("/api/v1/scrape-recipe")
def import_recipe():
    scrape_url = request.args.get("url")

    try:
        scraper = scrape_me(scrape_url)
    except Exception as e:
        logging.warn("Error while scraping " + scrape_url)
        logging.info("Trying with wild mode")
        try:
            scraper = scrape_me(scrape_url, wild_mode=True)
        except Exception as e:
            logging.error("Error retrying with wild mode")
            return "", 501

    response = {
        "language": getInfo(scraper, "language"),
        "title": getInfo(scraper, "title"),
        "category": getInfo(scraper, "category"),
        "author": getInfo(scraper, "author"),
        "total_time": getInfo(scraper, "total_time"),
        "cook_time": getInfo(scraper, "cook_time"),
        "prep_time": getInfo(scraper, "prep_time"),
        "yields": getInfo(scraper, "yields"),
        "imgage": getInfo(scraper, "image"),
        "ingredients": getInfo(scraper, "ingredients"),
        "nutrients": getInfo(scraper, "nutrients"),
        "instructions": getInfo(scraper, "instructions"),
        "ratings": getInfo(scraper, "ratings"),
        "cuisine": getInfo(scraper, "cuisine"),
        "host": getInfo(scraper, "host"),
        "links": getInfo(scraper, "links"),
    }
    return jsonify(response)


def getInfo(scraper, attribute):
    try:
        method = getattr(scraper, attribute, None)
        return method()
    except Exception as e:
        logging.warn(
            "Error getting info from scraper for attribute " + attribute)
        return ""
