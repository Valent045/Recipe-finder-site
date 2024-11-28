from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    results = search_recipes(query)
    if results is None:
        return jsonify({'error': 'Failed to fetch recipes'}), 500
    
    return render_template('results.html', recipes=results['results'])

if __name__ == '__main__':
    app.run(debug=True) 