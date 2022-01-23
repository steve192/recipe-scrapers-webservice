# recipe-scrapers-webservice

This is a wrapper for [hhursev/recipe-scrapers](https://github.com/hhursev/recipe-scrapers) which provides the api as a webservice, to be consumed as a microservice by other languages.


## Usage
### docker compose
```
version: "2.1"
services:
  recipe-scrapers-webservice:
    image: ghcr.io/steve192/recipe-scrapers-webservice
    container_name: recipe-scrapers-webservice
    ports:
      - 9090:9090
    restart: unless-stopped

```
### docker cli
```bash
    docker run -d \
        --name=recipe-scrapers-webservice \
        -p 9090:9090 \
        --restart unless-stopped \
        ghcr.io/steve192/recipe-scrapers-webservice
```


### Routes
```GET /api/v1/scrape-recipe?url=<url to your recipe>```\
responds with a recipe
```json
{
	"author": "AuthorHere",
	"category": "CategoryHere",
	"cook_time": "100",
	"cuisine": "French",
	"host": "recipehost.com",
	"imgage": "https://recipehost.com/image-for-recipe.jpg",
	"ingredients": ["10 g Ingredients1", "20g Ingredients2"],
	"instructions": "Instructions to the recipe\nSeparated by newlines",
	"language": "de",
	"links": [],
	"nutrients": {
		"calories": "631 kcal",
		"carbohydrateContent": "69 g",
		"fatContent": "26 g",
		"proteinContent": "14 g",
		"saturatedFatContent": "6 g",
		"servingSize": "504",
		"sodiumContent": "2 g",
		"sugarContent": "5 g"
	},
	"prep_time": "",
	"ratings": "",
	"title": "Title to a delicious recipe",
	"total_time": 30,
	"yields": "2 serving(s)"
}

```

```GET /api/v1/scrape-recipe/supported-hosts```\
responds with a list of supported hosts
```json
[
   "acouplecooks.com",
   "claudia.abril.com.br",
   "afghankitchenrecipes.com",
   "allrecipes.com",
   "alltommat.se",
   "amazingribs.com",
.
.
.
   "yemek.com",
   "yummly.com",
   "zeit.de",
   "zenbelly.com"
]

```
