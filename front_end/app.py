import pandas as pd
from flask import Flask, render_template, request
import os
import ast

app = Flask(__name__)

# --- Configuration ---
DATA_DIR = 'data'
SUMMARIZED_ARTICLES_FILE = os.path.join(DATA_DIR, 'summarized_articles_t5.csv') # Used by Summarizer
RECOMMENDATIONS_FILE = os.path.join(DATA_DIR, 'bert_faiss_recommendations.csv')
CLEANED_ARTICLES_FILE = os.path.join(DATA_DIR, 'cleaned_articles.csv') # Used by Recommender for titles/categories

# --- Load Data ---
# For Summarizer page
summarized_article_data = {}
available_article_ids_for_summarizer = []

# For Recommender page
base_article_details = {} # From cleaned_articles.csv for titles, categories
user_recommendations = {}
available_user_ids = []

def load_data():
    global summarized_article_data, available_article_ids_for_summarizer
    global base_article_details, user_recommendations, available_user_ids
    print("--- Loading Data ---")

    # 1. Load CLEANED_ARTICLES_FILE for base recommender details (title, category)
    try:
        cleaned_df = pd.read_csv(CLEANED_ARTICLES_FILE)
        cleaned_df['id'] = cleaned_df['id'].astype(str)
        cleaned_df.fillna({
            'title': 'Title Unavailable',
            'category': 'N/A',
            'subcategory': 'N/A',
            'abstract_clean': '' # Keep for summarizer if it falls back
        }, inplace=True)
        
        for _, row in cleaned_df.iterrows():
            base_article_details[row['id']] = {
                'id': row['id'],
                'title': row['title'],
                'category': row['category'],
                'subcategory': row['subcategory'],
                'abstract_clean': row['abstract_clean'] # For summarizer page use
            }
        print(f"Loaded {len(base_article_details)} base article details for Recommender & Summarizer fallback from '{CLEANED_ARTICLES_FILE}'.")
    except FileNotFoundError:
        print(f"ERROR: Critical file '{CLEANED_ARTICLES_FILE}' not found. Recommender and Summarizer will have limited functionality.")
        # Allow app to run but with clear indication of missing data
    except Exception as e:
        print(f"Error loading '{CLEANED_ARTICLES_FILE}': {e}")

    # 2. Load SUMMARIZED_ARTICLES_FILE for the Summarizer page
    try:
        summarized_df = pd.read_csv(SUMMARIZED_ARTICLES_FILE)
        summarized_df['id'] = summarized_df['id'].astype(str)
        summarized_df.fillna({
            'title': 'Title Unavailable', # Should ideally come from cleaned_articles
            'abstract_clean': '',    # Should ideally come from cleaned_articles
            'summary': 'Summary Not Available',
            'category': 'N/A',
            'subcategory': 'N/A'
        }, inplace=True)
        
        available_article_ids_for_summarizer = summarized_df['id'].unique().tolist()
        for _, row in summarized_df.iterrows():
            # Prioritize details from base_article_details if available
            article_id = row['id']
            summarized_article_data[article_id] = {
                'id': article_id,
                'title': base_article_details.get(article_id, {}).get('title', row['title']),
                'abstract_clean': base_article_details.get(article_id, {}).get('abstract_clean', row['abstract_clean']),
                'category': base_article_details.get(article_id, {}).get('category', row['category']),
                'subcategory': base_article_details.get(article_id, {}).get('subcategory', row['subcategory']),
                'summary': row['summary']
            }
        print(f"Loaded {len(summarized_article_data)} summarized articles for Summarizer page from '{SUMMARIZED_ARTICLES_FILE}'.")
    except FileNotFoundError:
        print(f"Warning: '{SUMMARIZED_ARTICLES_FILE}' not found. Summarizer page will rely on fallback or show 'Summary Not Available'.")
    except Exception as e:
        print(f"Error loading or merging '{SUMMARIZED_ARTICLES_FILE}': {e}")

    # 3. Load RECOMMENDATIONS_FILE
    try:
        recs_df = pd.read_csv(RECOMMENDATIONS_FILE)
        recs_df['user_id'] = recs_df['user_id'].astype(str)
        available_user_ids = recs_df['user_id'].unique().tolist()

        def safe_literal_eval(val):
            try:
                evaluated = ast.literal_eval(val)
                return [str(item) for item in evaluated]
            except (ValueError, SyntaxError): return []

        recs_df['recommended_news_ids'] = recs_df['recommended_news_ids'].apply(safe_literal_eval)
        user_recommendations = recs_df.set_index('user_id')['recommended_news_ids'].to_dict()
        print(f"Loaded recommendations for {len(user_recommendations)} users from '{RECOMMENDATIONS_FILE}'.")
    except FileNotFoundError:
        print(f"Warning: '{RECOMMENDATIONS_FILE}' not found. Recommender will not work.")
        user_recommendations = {} # Ensure it's an empty dict
    except Exception as e:
        print(f"Error loading '{RECOMMENDATIONS_FILE}': {e}")
        user_recommendations = {}

    print("--- Data Loading Complete ---")

load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    article_id_input = None
    article_info_display = None
    error_message = None

    if request.method == 'POST':
        article_id_input = request.form.get('article_id', '').strip()
    elif request.method == 'GET': # Handle GET requests for direct linking
        article_id_input = request.args.get('article_id', '').strip() # Get from URL query param

    if article_id_input: # Process if we have an article_id_input from POST or GET
        article_id_input_str = str(article_id_input)
        article_info_display = summarized_article_data.get(article_id_input_str)
        
        if not article_info_display:
            fallback_info = base_article_details.get(article_id_input_str)
            if fallback_info:
                article_info_display = fallback_info.copy()
                article_info_display['summary'] = "Summary not generated for this article."
            else:
                # Only set error if it wasn't a direct link that found nothing initially
                if request.method == 'POST' or (request.method == 'GET' and request.args.get('article_id')):
                    error_message = f"Article ID '{article_id_input_str}' not found."
        elif not article_info_display.get('summary') or article_info_display.get('summary') == 'Summary Not Available':
             article_info_display['summary'] = "Summary not generated for this article."
    
    # If it's a GET request without an article_id, just show the form
    # If it's a POST and article_id_input was empty, error_message would be set
    elif request.method == 'POST' and not article_id_input:
         error_message = "Please enter an Article ID."


    return render_template(
        'summarize.html',
        article_id_input=article_id_input,
        article_data=article_info_display,
        error=error_message,
        available_article_ids=available_article_ids_for_summarizer[:200]
    )


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    user_id_input = None
    recommendations_display_list = None # List of dicts for the template
    error_message = None

    if request.method == 'POST':
        user_id_input = request.form.get('user_id', '').strip()
        if not user_id_input:
            error_message = "Please enter a User ID."
        else:
            user_id_input = str(user_id_input)
            recommended_ids = user_recommendations.get(user_id_input)

            if recommended_ids is None:
                error_message = f"User ID '{user_id_input}' not found or no recommendations available."
            elif not recommended_ids:
                error_message = f"No recommendations available for User ID '{user_id_input}'."
                recommendations_display_list = []
            else:
                recommendations_display_list = []
                for article_id in recommended_ids:
                    article_id_str = str(article_id)
                    # Get base details (title, category) from base_article_details
                    details = base_article_details.get(article_id_str)
                    
                    if details:
                        recommendations_display_list.append({
                            'id': details['id'],
                            'title': details['title'],
                            'category': details['category'],
                            'subcategory': details['subcategory']
                            # NO 'summary' or 'abstract_clean' here for the recommender view
                        })
                    else:
                        # This case should be rare if bert_faiss_recommendations.csv is correctly filtered
                        recommendations_display_list.append({
                            'id': article_id_str,
                            'title': f'Article {article_id_str} (Details Missing)',
                            'category': 'N/A',
                            'subcategory': 'N/A'
                        })
                if not recommendations_display_list and recommended_ids:
                     error_message = "Found recommendations, but could not retrieve details for any recommended articles."


    return render_template(
        'recommend.html',
        user_id_input=user_id_input,
        recommendations=recommendations_display_list,
        error=error_message,
        available_user_ids=available_user_ids[:200]
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)