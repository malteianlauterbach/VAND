import os
import re
from time import sleep

import Levenshtein
import requests
from flask import Flask, render_template, render_template_string, request
from textblob import TextBlob

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/query_api', methods=['POST'])
def query_api():
  query = request.form.get('query')
  api_url = f"https://api.gdeltproject.org/api/v2/context/context?format=html&timespan=48H&query={query}&mode=artlist&maxrecords=200&format=json"
  print(f"URL: {api_url}")

  # Sending a request to the API
  response = requests.get(api_url)
  data = response.json()

  total_articles = 0
  short_articles = 0
  short_titles = 0
  quote_articles = 0
  similar_articles = 0
  positive_articles = 0
  negative_articles = 0
  neutral_articles = 0
  high_polarity_articles = 0

  # Threshold for high polarity
  polarity_threshold = 0.8

  # List to store articles with their scores
  articles_with_scores = []

  # Saving response to a file
  with open('reply.txt', 'w') as file:
    for article in data['articles']:
      total_articles += 1
      if article.get('isquote') == 1:
        quote_articles += 1
        continue  # Skip if it's a quote

      title = article['title']
      sentence = article['sentence']
      context = article['context']
      socialimage = article['socialimage']

      # Check title length
      if len(title.split()) < 5:
        short_titles += 1
        continue  # Skip if title has less than 5 words

      # Count words in sentence
      word_count = len(re.findall(r'\w+', sentence))
      if word_count < 5:
        short_articles += 1
        continue  # Skip if sentence has less than 5 words

      # Check similarity using Levenshtein distance
      title_similarity = Levenshtein.distance(query, title)
      sentence_similarity = Levenshtein.distance(query, sentence)
      similarity_threshold = min(len(query), len(title), len(sentence)) * 0.3

      if title_similarity < similarity_threshold or sentence_similarity < similarity_threshold:
        similar_articles += 1
        continue  # Skip if title or sentence is too similar to query

      # Perform sentiment analysis
      sentence_sentiment = TextBlob(sentence).sentiment.polarity

      if sentence_sentiment > 0:
        positive_articles += 1
      elif sentence_sentiment < 0:
        negative_articles += 1
      else:
        neutral_articles += 1

      # Check for high polarity
      if abs(sentence_sentiment) > polarity_threshold:
        high_polarity_articles += 1
        continue  # Skip if polarity is too high

      # Count occurrences of query in title, sentence, and context
      query_in_title = title.lower().count(query.lower())
      query_in_sentence = sentence.lower().count(query.lower())
      query_in_context = context.lower().count(query.lower())

      # Assign score based on mentioned criteria
      score = query_in_title + query_in_sentence + query_in_context - abs(
          sentence_sentiment)

      # Append article with score to the list
      articles_with_scores.append((article, score))

    # Sort articles based on scores
    sorted_articles = sorted(articles_with_scores,
                             key=lambda x: x[1],
                             reverse=True)

    # Write sorted articles to file
    rank = 1

    for article, score in sorted_articles:
      title = article['title']
      sentence = article['sentence']
      socialimage = article['socialimage']
      context = article['context']  # Added context information
      polarity = TextBlob(sentence).sentiment.polarity
      file.write(f"Rank: {rank}\n")
      file.write(f"Title: {title}\n")
      file.write(f"Context: {context}\n")  # Write context to file
      file.write(f"Sentence: {sentence}\n")
      file.write(f"Social Image: {socialimage}\n")
      file.write(f"Sentiment Polarity: {polarity}\n")
      file.write("===\n")  # Adding a line break between articles
      rank += 1

  print(f"Total Articles: {total_articles}")
  print(f"Short Titles Filtered: {short_titles}")
  print(f"Short Articles Filtered: {short_articles}")
  print(f"Quote Articles Filtered: {quote_articles}")
  print(f"Similar Articles Filtered: {similar_articles}")
  print(f"Positive Articles: {positive_articles}")
  print(f"Negative Articles: {negative_articles}")
  print(f"Neutral Articles: {neutral_articles}")
  print(f"High Polarity Articles Filtered: {high_polarity_articles}")

  print("Response saved to reply.txt")

  def get_unique_entries(file_path):
    with open(file_path, 'r') as file:
      unique_headlines = set()
      current_entry = ""
      removed_count = 0  # Counter for removed duplicate titles
      skip_entry = False  # Flag to skip current entry
      for line in file:
        if line.strip() == "===":
          if skip_entry:
            skip_entry = False  # Reset skip flag if a separator is encountered
          else:
            if current_entry:  # Ensure current entry is not empty before yielding
              yield current_entry + "===\n"  # Yield the entire entry with separator
            current_entry = ""  # Start a new entry
        elif line.startswith("Title:"):
          title = line.strip()[7:]
          if not is_similar_title(
              title, unique_headlines) and not has_blind_characters(title):
            unique_headlines.add(title)
            current_entry = line.strip(
            ) + "\n"  # Start a new entry with the title
          else:
            removed_count += 1  # Increment counter for removed duplicate titles
            skip_entry = True  # Set flag to skip the current entry
            current_entry = ""  # Clear current entry
        elif not skip_entry:
          current_entry += line  # Add line to the current entry if not skipping
      print(f"Removed {removed_count} duplicate titles with blind characters")

  def is_similar_title(title, unique_headlines):
    for unique_title in unique_headlines:
      title_words = set(title.lower().split())
      unique_title_words = set(unique_title.lower().split())
      common_words = title_words.intersection(unique_title_words)
      if len(common_words) >= 5:
        return True  # Titles are similar if 5 or more words are common
    return False  # Titles are not similar

  def has_blind_characters(text):
    blind_phrases = ["Lorem ipsum", "dolor sit amet", "consectetur adipiscing"]
    for phrase in blind_phrases:
      if phrase.lower() in text.lower():
        return True  # Text contains blind characters
    return False  # Text does not contain blind characters

  def write_unique_entries(input_file, output_file):
    with open(output_file, 'w') as output:
      for entry in get_unique_entries(input_file):
        output.write(entry)

  input_file_path = "reply.txt"
  output_file_path = "unique_headlines.txt"
  write_unique_entries(input_file_path, output_file_path)
  print("Unique headlines saved to unique_headlines.txt")


@app.route('/results')
def display_results():
  if os.path.exists("unique_headlines.txt"):
    # Read the contents of the text file
    with open('unique_headlines.txt', 'r') as file:
      data = file.read()

    # Split the text into individual entries
    entries = data.split('===\n')

    # Create a list to hold dictionaries representing each entry
    parsed_entries = []

    # Parse each entry
    for entry in entries:
      if entry.strip():  # Check if the entry is not empty
        entry_dict = {}
        lines = entry.split('\n')
        for line in lines:
          if ': ' in line:
            key, value = line.split(': ', 1)
            entry_dict[key] = value
        parsed_entries.append(entry_dict)

    # Render HTML template with parsed entries
    return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>VAND - vectorized analytical news distribution</title>
                <style>
                    body {
                        background-color: #f0f0f0; /* Light grey background */
                        font-family: "Courier New", Courier, monospace;
                    }

                    .container {
                        max-width: 800px;
                        margin: 50px auto;
                    }

                    .news-item {
                        display: flex; /* Use flexbox to align items */
                        align-items: flex-start; /* Align items at the start */
                        margin-bottom: 20px;
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        background-color: white;
                    }

                    .text-content {
                        flex: 1; /* Take remaining space */
                        padding: 10px;
                        height: auto; /* Fixed height */
                        overflow: hidden; /* Hide overflow text */
                    }

                    .text-content p {
                        margin: 5px 0;
                    }

                    .image-content {
                        margin-left: 20px;
                        height: 150px; /* Fixed height */
                    }

                    .image-content img {
                        max-width: 100%;
                        max-height: 100%;
                        object-fit: cover; /* Ensure image fills container */
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 style="text-align: center;">Vectorized Analytical Data Distribution</h1>
                    {% for entry in entries %}
                    <div class="news-item">
                        <div class="text-content">
                            <p><strong>Title:</strong> {{ entry.get('Title', 'N/A') }}</p>
                            <p><strong>Sentence:</strong> {{ entry.get('Sentence', 'N/A') }}</p>
                            <p><strong>Context:</strong> {{ entry.get('Context', 'N/A') }}</p>
                            <p><strong>Sentiment Polarity:</strong> {{ entry.get('Sentiment Polarity', 'N/A') }}</p>
                        </div>
                        <div class="image-content">
                            <img src="{{ entry.get('Social Image', '') }}">
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </body>
            </html>
            ''',
                                  entries=parsed_entries)
  else:
    return "Error: reply.txt does not exist."


if __name__ == '__main__':
  app.run(debug=True)
