# SocialCraft AI

SocialCraft AI is a full-stack AI-powered social media content studio designed for small businesses. It includes two main tools: **CaptionCraft**, which creates written marketing content, and **PostCraft**, which creates a complete social media post package with a locked premium visual preview.

## Overview

Small businesses often need to post consistently on social media, but creating captions, hashtags, calls to action, and visual post ideas can take time. SocialCraft AI helps users turn simple inputs into ready-to-use social media content.

The app uses a frontend form to collect details from the user, sends the information to a Flask backend, and uses the Gemini API to generate structured content.

## Tools

### CaptionCraft

CaptionCraft generates written marketing content based on the user's business type, platform, topic, tone, and target audience.

It creates:

* Two caption options
* Relevant hashtags
* A call to action
* A future content idea

### PostCraft

PostCraft creates a complete social media post package based on the user's business, platform, topic, goal, style, format, colours, audience, and preferred on-image text.

It creates:

* A short headline for the post visual
* A supporting subheadline
* A matching caption
* Relevant hashtags
* A detailed image-generation prompt
* A locked premium visual preview

The locked preview simulates a paid image-generation feature. When image generation is disabled, users can still view the full text package and image prompt.

## Features

* AI-generated captions and hashtags
* AI-generated calls to action and future post ideas
* PostCraft visual package generation
* Locked premium image preview for future subscription-style features
* Gemini API integration
* Flask backend for secure API handling
* Environment variable support for API keys
* Responsive frontend using Tailwind CSS
* Local testing support

## Tech Stack

* HTML
* JavaScript
* Tailwind CSS
* Python
* Flask
* Gemini API
* python-dotenv

## Project Structure

```text
SocialCraftAI
├── index.html
├── server.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/RadicalRis/SocialCraftAI.git
```

### 2. Navigate into the project folder

```bash
cd SocialCraftAI
```

### 3. Create a virtual environment

```bash
py -m venv venv
```

### 4. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

### 6. Create a `.env` file

Create a file called `.env` in the main project folder and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_IMAGE_MODEL=disabled
```

`GEMINI_IMAGE_MODEL=disabled` keeps PostCraft in text-package mode and shows the locked premium visual preview instead of calling a paid/limited image-generation model.

### 7. Run the Flask server

```bash
python server.py
```

### 8. Open the app

In your browser, go to:

```text
http://127.0.0.1:5050/
```

## Security Note

The `.env` file is intentionally not uploaded to GitHub because it contains the private Gemini API key. The `.gitignore` file should prevent sensitive or unnecessary files from being committed, including:

```text
.env
venv/
__pycache__/
*.pyc
.DS_Store
```

## What I Learned

Through this project, I learned how to build a full-stack web application with a frontend and backend. I also learned how to connect a Python Flask server to an AI API, handle JSON responses, protect API keys using environment variables, and design a product with multiple AI-powered features.

This project helped me better understand how real web applications are structured, especially how the frontend, backend, and external APIs work together.

## Future Improvements

Possible future upgrades include:

* Add local content history
* Add user accounts
* Add real payment/subscription support for PostCraft visual generation
* Add downloadable post templates
* Deploy the app online using a production server
* Add screenshots or a demo video to the README

## Author

Created by [RadicalRis](https://github.com/RadicalRis).
