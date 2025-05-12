import pandas as pd
import ast

print("Analyzing data consistency...")

try:
    recs_df = pd.read_csv('data/bert_faiss_recommendations.csv')
    summarized_df = pd.read_csv('data/summarized_articles_t5.csv')
    cleaned_df = pd.read_csv('data/cleaned_articles.csv') # Your base article list

    # Ensure IDs are strings for consistent comparison
    recs_df['user_id'] = recs_df['user_id'].astype(str)
    summarized_df['id'] = summarized_df['id'].astype(str)
    cleaned_df['id'] = cleaned_df['id'].astype(str)

    all_recd_article_ids = set()
    def safe_eval_ids(val):
        try:
            return {str(item) for item in ast.literal_eval(val)}
        except:
            return set()

    for id_list_str in recs_df['recommended_news_ids']:
        all_recd_article_ids.update(safe_eval_ids(id_list_str))

    summarized_article_ids = set(summarized_df['id'])
    cleaned_article_ids = set(cleaned_df['id'])

    print(f"Total unique articles in recommendations: {len(all_recd_article_ids)}")
    print(f"Total unique articles in summarized_articles_t5.csv: {len(summarized_article_ids)}")
    print(f"Total unique articles in cleaned_articles.csv: {len(cleaned_article_ids)}")

    missing_in_cleaned = all_recd_article_ids - cleaned_article_ids
    if missing_in_cleaned:
        print(f"\nWARNING: {len(missing_in_cleaned)} recommended article IDs are MISSING from cleaned_articles.csv (base details):")
        print(list(missing_in_cleaned)[:20]) # Print a sample
    else:
        print("\nGOOD: All recommended article IDs are present in cleaned_articles.csv.")

    missing_in_summarized = all_recd_article_ids - summarized_article_ids
    if missing_in_summarized:
        print(f"\nINFO: {len(missing_in_summarized)} recommended article IDs are MISSING summaries (not in summarized_articles_t5.csv):")
        # Check if these are at least in cleaned_articles
        still_missing_details = missing_in_summarized - cleaned_article_ids
        if still_missing_details:
             print(f"  Out of these, {len(still_missing_details)} are ALSO missing from cleaned_articles.csv! These will show 'details not found'.")
        else:
            print("  However, all of these should still have basic details from cleaned_articles.csv.")
        # print(list(missing_in_summarized)[:20]) # Print a sample
    else:
        print("\nGOOD: All recommended article IDs have corresponding entries in summarized_articles_t5.csv (summaries should be available).")

except FileNotFoundError as e:
    print(f"File not found: {e}. Please ensure all CSVs are in the 'data' directory.")
except Exception as e:
    print(f"An error occurred: {e}")