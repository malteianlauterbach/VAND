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
              if not is_similar_title(title, unique_headlines) and not has_blind_characters(title):
                  unique_headlines.add(title)
                  current_entry = line.strip() + "\n"  # Start a new entry with the title
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