from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API Keys
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
BASE_URL = 'https://api.spoonacular.com/recipes'

def search_recipes(query, number=10):
    """
    Search for recipes using the Spoonacular API
    """
    endpoint = f'{BASE_URL}/complexSearch'
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'query': query,
        'number': number,
        'addRecipeInformation': True,
        'fillIngredients': True
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipes: {e}")
        return None

def translate_to_english(text):
    """
    Translate Russian text to English using Yandex Translate
    """
    try:
        response = requests.post(
            "https://translate.api.cloud.yandex.net/translate/v2/translate",
            json={
                "sourceLanguageCode": "ru",
                "targetLanguageCode": "en",
                "texts": [text]
            },
            headers={
                "Authorization": f"Api-Key {YANDEX_API_KEY}"
            }
        )
        response.raise_for_status()
        return response.json()['translations'][0]['text']
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def translate_to_russian(text):
    """
    Translate English text to Russian using Yandex Translate
    """
    try:
        response = requests.post(
            "https://translate.api.cloud.yandex.net/translate/v2/translate",
            json={
                "sourceLanguageCode": "en",
                "targetLanguageCode": "ru",
                "texts": [text]
            },
            headers={
                "Authorization": f"Api-Key {YANDEX_API_KEY}"
            }
        )
        response.raise_for_status()
        return response.json()['translations'][0]['text']
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

def translate_recipe(recipe):
    """
    Translate recipe details to Russian
    """
    try:
        # Translate title
        recipe['title'] = translate_to_russian(recipe['title'])
        
        # Translate ingredients
        if 'extendedIngredients' in recipe:
            for ingredient in recipe['extendedIngredients']:
                ingredient['name'] = translate_to_russian(ingredient['name'])
                if 'original' in ingredient:
                    ingredient['original'] = translate_to_russian(ingredient['original'])
        
        # Translate instructions
        if 'analyzedInstructions' in recipe and recipe['analyzedInstructions']:
            for instruction_group in recipe['analyzedInstructions']:
                if 'steps' in instruction_group:
                    for step in instruction_group['steps']:
                        step['step'] = translate_to_russian(step['step'])
        
        return recipe
    except Exception as e:
        print(f"Recipe translation error: {e}")
        return recipe

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('index.html', error="Please enter a search query")
    
    try:
        # Translate query if it's in Russian
        if any(ord(char) >= 1040 and ord(char) <= 1103 for char in query):
            translated_query = translate_to_english(query)
            if not translated_query:
                return render_template('index.html', error="Failed to translate search query")
            query = translated_query
        
        results = search_recipes(query)
        if results is None:
            return render_template('index.html', error="Failed to fetch recipes. Please try again later.")
        
        if not results.get('results'):
            return render_template('index.html', error="No recipes found. Please try a different search term.")
        
        # Translate each recipe to Russian
        translated_results = []
        for recipe in results['results']:
            translated_recipe = translate_recipe(recipe)
            translated_results.append(translated_recipe)
        
        return render_template('results.html', recipes=translated_results)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return render_template('index.html', error="An unexpected error occurred. Please try again later.")

if __name__ == '__main__':
    app.run(debug=True) 