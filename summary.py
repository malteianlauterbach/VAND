from flask import Flask, render_template_string

# Initialize the Flask app
app = Flask(__name__)

# Read the content from the output.txt file and strip === separators
def read_output_file():
    try:
        with open("output.txt", "r") as file:
            content = file.read()
            # Remove the === separators and filter out entries starting with "Title:"
            filtered_content = [entry.strip() for entry in content.split("===") if not entry.strip().startswith("Title:")]
            return filtered_content
    except FileNotFoundError:
        print("File not found.")
        return None

# Define the route for /summary
@app.route('/summary')
def summary():
    # Read the content from the output.txt file
    contents = read_output_file()

    # Check if content exists
    if contents:
        # Render the template with the content centered in a div
        html_template = '''
            <!DOCTYPE html>
            <html>
            <head>
            <title>Summary</title>
            <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 12pt;
                background-color: white;
                margin: 0;
                padding: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                width: 80%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                height: 100%;
            }
            .headline {
                background-color: #f2f2f2;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                max-height: 50%;
                overflow-y: auto;
            }
            </style>
            </head>
            <body>
            <div class="container">
        '''
        for content in contents:
            if content.strip():
                html_template += f'<div class="headline">{content}</div>\n'
        html_template += '''
            </div>
            </body>
            </html>
        '''
        return html_template
    else:
        return "No content available."

if __name__ == "__main__":
    app.run(debug=True)
