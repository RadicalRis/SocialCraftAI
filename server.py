from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
import os
import json
import re
import base64

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY. Check your .env file.")

GEMINI_TEXT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

client = genai.Client(api_key=api_key)


def clean_ai_json(text):
    """Remove markdown fences when Gemini wraps JSON in ```json blocks."""
    if not text:
        return ""

    cleaned = text.strip()
    cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"^```", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def safe_json_from_gemini(prompt, fallback):
    """Ask Gemini for JSON and fall back safely if the model returns plain text."""
    try:
        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=prompt
        )
        ai_text = clean_ai_json(getattr(response, "text", "") or "")
        return json.loads(ai_text)
    except Exception as exc:
        print("GEMINI JSON ERROR:", exc)
        return fallback


def get_aspect_ratio(format_choice):
    ratios = {
        "Square Post": "1:1",
        "Portrait / Story": "9:16",
        "Landscape Banner": "16:9"
    }
    return ratios.get(format_choice, "1:1")


def iter_response_parts(response):
    """Return response parts across SDK versions."""
    parts = getattr(response, "parts", None)
    if parts:
        return parts

    collected = []
    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        candidate_parts = getattr(content, "parts", None) if content else None
        if candidate_parts:
            collected.extend(candidate_parts)

    return collected


def inline_image_to_data_url(inline_data):
    """Convert Gemini inline image data to a browser-displayable data URL."""
    mime_type = getattr(inline_data, "mime_type", None) or getattr(inline_data, "mimeType", None) or "image/png"
    raw_data = getattr(inline_data, "data", None)

    if not raw_data:
        return None

    if isinstance(raw_data, bytes):
        image_base64 = base64.b64encode(raw_data).decode("utf-8")
    else:
        image_base64 = str(raw_data)

    return f"data:{mime_type};base64,{image_base64}"


def build_post_package(data):
    business = data.get("businessType", "small business")
    platform = data.get("platform", "Instagram")
    topic = data.get("topic", "")
    style = data.get("style", "Modern")
    colors = data.get("colors", "clean brand colors")
    audience = data.get("audience", "general audience")
    goal = data.get("goal", "Promotion")
    text_on_image = data.get("textOnImage", "")
    format_choice = data.get("format", "Square Post")

    fallback_headline = text_on_image.strip() or topic.title() or "New Post"
    fallback = {
        "headline": fallback_headline[:60],
        "subheadline": f"A {goal.lower()} post for {audience}",
        "caption": f"{topic} — made for {audience}. Check it out and stay connected with us.",
        "hashtags": "#smallbusiness #socialmedia #marketing #branding #contentcreation",
        "image_prompt": ""
    }

    prompt = f"""
Create a social media post package for a small business.

User Inputs:
Business Type: {business}
Platform: {platform}
Post Topic: {topic}
Visual Style: {style}
Colors / Brand Vibe: {colors}
Target Audience: {audience}
Goal: {goal}
Format: {format_choice}
Preferred Text on Image: {text_on_image if text_on_image else "No custom text provided"}

Return ONLY valid JSON in this exact format:
{{
  "headline": "short on-image headline, max 6 words",
  "subheadline": "supporting line, max 12 words",
  "caption": "2-4 sentence caption matching the post",
  "hashtags": "#tag1 #tag2 #tag3 #tag4 #tag5 #tag6",
  "image_prompt": "detailed prompt for Gemini image generation"
}}

Rules:
- The image should look like a finished social media graphic/post, not random art.
- The headline should be short because image models handle short text better.
- The image_prompt must describe layout, composition, colours, typography, subject, lighting, style, and platform fit.
- Make the post safe for work.
- Do not include markdown.
"""

    package = safe_json_from_gemini(prompt, fallback)

    if not package.get("image_prompt"):
        package["image_prompt"] = create_image_prompt(data, package)

    return package


def create_image_prompt(data, package):
    business = data.get("businessType", "small business")
    platform = data.get("platform", "Instagram")
    topic = data.get("topic", "")
    style = data.get("style", "Modern")
    colors = data.get("colors", "clean brand colors")
    audience = data.get("audience", "general audience")
    goal = data.get("goal", "Promotion")
    format_choice = data.get("format", "Square Post")
    headline = package.get("headline", "")
    subheadline = package.get("subheadline", "")

    return f"""
Create a polished, ready-to-post {format_choice} social media graphic for {platform}.

Business type: {business}
Topic: {topic}
Goal: {goal}
Target audience: {audience}
Visual style: {style}
Color direction: {colors}

Design instructions:
- Make it look like a professional marketing post, not a random illustration.
- Use a clean modern layout with strong visual hierarchy.
- Add one large short headline: "{headline}".
- Add one smaller supporting line: "{subheadline}".
- Use readable typography, balanced spacing, and a social media ad/post composition.
- Include relevant visual elements connected to the business and topic.
- Avoid clutter, distorted lettering, extra random words, logos, and watermarks.
- High quality digital design, crisp edges, polished lighting, commercial social media aesthetic.
""".strip()


def image_generation_is_enabled():
    """Treat disabled/off/false/none as a text-only Post Studio mode."""
    value = (GEMINI_IMAGE_MODEL or "").strip().lower()
    return value not in {"", "disabled", "off", "false", "none"}


def generate_gemini_image(image_prompt, aspect_ratio):
    """Generate an image with Gemini and return a data URL for the browser."""
    final_prompt = f"""
{image_prompt}

Important format instruction:
Create the image in a {aspect_ratio} aspect ratio.
""".strip()

    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=[final_prompt]
    )

    for part in iter_response_parts(response):
        inline_data = getattr(part, "inline_data", None) or getattr(part, "inlineData", None)
        if inline_data:
            data_url = inline_image_to_data_url(inline_data)
            if data_url:
                return data_url

    raise ValueError("Gemini did not return an image. Try a simpler prompt or check image model access.")


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}

    business = data.get("businessType", "")
    platform = data.get("platform", "")
    topic = data.get("topic", "")
    tone = data.get("tone", "")
    audience = data.get("audience", "")

    prompt = f"""
Create marketing content for a small business.

Business Type: {business}
Platform: {platform}
Topic: {topic}
Tone: {tone}
Target Audience: {audience}

Return ONLY valid JSON in this exact format:
{{
  "caption1": "string",
  "caption2": "string",
  "hashtags": "string",
  "cta": "string",
  "idea": "string"
}}
"""

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt
    )

    ai_text = clean_ai_json(getattr(response, "text", "") or "")

    try:
        parsed = json.loads(ai_text)
    except json.JSONDecodeError:
        return jsonify({
            "caption1": ai_text,
            "caption2": "",
            "hashtags": "",
            "cta": "",
            "idea": ""
        })

    return jsonify(parsed)


@app.route("/generate-visual-post", methods=["POST"])
def generate_visual_post():
    data = request.get_json() or {}
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"error": "Post topic is required."}), 400

    post_package = build_post_package(data)
    image_prompt = create_image_prompt(data, post_package)
    aspect_ratio = get_aspect_ratio(data.get("format", "Square Post"))

    base_response = {
        "headline": post_package.get("headline", ""),
        "subheadline": post_package.get("subheadline", ""),
        "caption": post_package.get("caption", ""),
        "hashtags": post_package.get("hashtags", ""),
        "image_prompt": image_prompt,
        "aspect_ratio": aspect_ratio
    }

    if not image_generation_is_enabled():
        return jsonify({
            **base_response,
            "image_url": "",
            "image_model": "disabled",
            "image_locked": True,
            "image_status": "locked",
            "locked_title": "PostCraft visuals locked",
            "locked_message": "Subscribe to unlock AI-generated PostCraft visuals. Your caption, hashtags, and image prompt are ready below."
        })

    try:
        image_url = generate_gemini_image(image_prompt, aspect_ratio)
        return jsonify({
            **base_response,
            "image_url": image_url,
            "image_model": GEMINI_IMAGE_MODEL,
            "image_locked": False,
            "image_status": "generated"
        })

    except Exception as exc:
        print("GEMINI IMAGE ERROR:", exc)
        return jsonify({
            **base_response,
            "image_url": "",
            "image_model": GEMINI_IMAGE_MODEL,
            "image_locked": True,
            "image_status": "quota_or_billing_required",
            "locked_title": "PostCraft visuals unavailable",
            "locked_message": "PostCraft image generation requires available Gemini image quota or billing. The text package still generated successfully.",
            "image_error": str(exc)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5050, use_reloader=False)
