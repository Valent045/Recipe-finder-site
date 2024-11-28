from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from googletrans import Translator

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get API key from environment variable
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
        'addRecipeInformation': True,  # Include detailed recipe information
        'fillIngredients': True        # Include ingredient information
    }
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipes: {e}")
        return None

def translate_to_english(text):
    """
    Translate Russian text to English
    """
    try:
        translator = Translator()
        translation = translator.translate(text, src='ru', dest='en')
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def translate_to_russian(text):
    """
    Translate English text to Russian
    """
    try:
        translator = Translator()
        translation = translator.translate(text, src='en', dest='ru')
        return translation.text
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
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    # Translate query if it's in Russian
    if any(ord(char) >= 1040 and ord(char) <= 1103 for char in query):
        translated_query = translate_to_english(query)
        if translated_query:
            query = translated_query
        else:
            return jsonify({'error': 'Translation failed'}), 500
    
    results = search_recipes(query)
    if results is None:
        return jsonify({'error': 'Failed to fetch recipes'}), 500
    
    # Translate each recipe to Russian
    translated_results = []
    for recipe in results['results']:
        translated_recipe = translate_recipe(recipe)
        translated_results.append(translated_recipe)
    
    results['results'] = translated_results
    return render_template('results.html', recipes=results['results'])

if __name__ == '__main__':
    app.run(debug=True) 