from openai import OpenAI
import os

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Define the main function
def main():
  # Read the contents of the file
  def read_file(file_path):
    try:
      with open(file_path, 'r') as file:
        return file.read()
    except FileNotFoundError:
      print("File not found.")
      return None

  # Define the file path
  file_path = "unique_headlines.txt"
  file_contents = read_file(file_path)

  if file_contents:
    # Split the file contents by '===' to get individual entries
    entries = file_contents.split("===")

    # Open the output file in write mode
    with open("output.txt", "w") as output_file:
      # Send only the first 10 entries to OpenAI API
      for entry in entries[:10]:
        # Prepare the message for OpenAI API
        message = 'You are JournoGPT, a pre-trained Neuronal Networking Journalist intended to aid whoever. The following data is a list of articles we have gotten from our colleagues. Please summarize the events of the last 48 hours. There will be no need to explain the context of these events at all and also no need to elaborate on how this is a summary.\n\n'
        message += entry  # Add entry to the message

        # Send request to OpenAI API
        response = client.chat.completions.create(model='gpt-3.5-turbo-0125',
                                                  messages=[{
                                                      'role': 'user',
                                                      'content': message
                                                  }],
                                                  max_tokens=500,
                                                  temperature=0)

        # Extract the response content
        response_content = response.choices[0].message.content

        # Print the summary to console
        print(response_content)

        # Write the summary to the output file
        output_file.write(response_content + "\n")
        output_file.write("=========================================\n")

    print("Summaries saved to output.txt")


# Execute the main function
if __name__ == "__main__":
  main()
