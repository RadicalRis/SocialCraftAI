# CaptionCraft AI

CaptionCraft AI is a full-stack AI-powered marketing content generator designed for small businesses. Users can enter details such as their business type, platform, post topic, tone, and target audience, and the app generates social media captions, hashtags, a call to action, and a future content idea.

## Features

* Generates two marketing caption options
* Creates relevant hashtags
* Suggests a call to action
* Provides a future content idea
* Uses a Flask backend to securely handle AI requests
* Uses environment variables to protect the Gemini API key
* Can run locally and across devices on the same local network

## Tech Stack

* HTML
* JavaScript
* Tailwind CSS
* Python
* Flask
* Gemini API
* dotenv

## How It Works

The frontend collects user input through a web form. The Flask backend receives the data, sends a structured prompt to the Gemini API, and returns the generated content as JSON. The frontend then displays the response in separate content cards.

## Project Purpose

I built CaptionCraft AI to explore full-stack development, API integration, and AI-powered productivity tools. The goal was to create a practical app that could help small businesses quickly generate marketing content for social media platforms.

## Running the Project Locally

1. Clone the repository.

```bash
git clone https://github.com/YOUR-USERNAME/captioncraft-ai.git
```

2. Navigate into the project folder.

```bash
cd captioncraft-ai
```

3. Install the required packages.

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project folder.

```env
GEMINI_API_KEY=your_api_key_here
```

5. Run the Flask server.

```bash
python server.py
```

6. Open the app in your browser.

```text
http://127.0.0.1:5050/
```

## Local Network Testing

The app can also be tested on another device connected to the same network by running the Flask server with:

```python
app.run(host="0.0.0.0", debug=True, port=5050, use_reloader=False)
```

Then another device can visit:

```text
http://YOUR-COMPUTER-IP:5050/
```

## Security Note

The `.env` file is not included in this repository because it contains the private Gemini API key. The `.gitignore` file prevents `.env` and `venv/` from being uploaded.