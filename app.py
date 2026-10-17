from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "promptmall-secret-key-change-in-production"

# ====================== DATA ======================
PROMPTS = [
    {
        "id": "rain",
        "title": "Cinematic Rain Portrait",
        "type": "Image",
        "category": "Cinematic",
        "description": "A moody neon-lit urban portrait with filmic texture.",
        "tags": ["Cinematic", "Portrait", "Neon"],
        "author": "Arjun Mehta",
        "likes": "2.4k",
        "copies": "8.9k",
        "img": "https://images.pexels.com/photos/14440801/pexels-photo-14440801.jpeg?auto=compress&cs=tinysrgb&w=800",
        "prompt_text": "Create an ultra-realistic cinematic portrait of a young man standing on a rainy city street at night, dramatic neon lighting, shallow depth of field, realistic skin texture, professional photography, 85mm lens, cinematic color grading."
    },
    {
        "id": "luxury",
        "title": "Luxury Product Photography",
        "type": "Image",
        "category": "Business",
        "description": "Luxury campaign lighting for high-end product imagery.",
        "tags": ["Product", "Studio", "Gold"],
        "author": "Maya Shah",
        "likes": "1.8k",
        "copies": "6.1k",
        "img": "https://images.pexels.com/photos/37127787/pexels-photo-37127787.jpeg?auto=compress&cs=tinysrgb&w=800",
        "prompt_text": "Create a luxury product photograph of a premium gold watch on black marble, dramatic studio lighting, reflections, high-end commercial style, 100mm macro lens, cinematic color grading."
    },
    {
        "id": "city",
        "title": "Futuristic Cyberpunk City",
        "type": "Video",
        "category": "Cinematic",
        "description": "Electric skyline vistas for futuristic worldbuilding.",
        "tags": ["Cyberpunk", "City", "Video"],
        "author": "Leo Martin",
        "likes": "3.1k",
        "copies": "11.2k",
        "img": "https://images.pexels.com/photos/32660203/pexels-photo-32660203.jpeg?auto=compress&cs=tinysrgb&w=800",
        "prompt_text": "Cinematic drone shot flying through a futuristic cyberpunk city at night, neon lights, flying cars, rain, volumetric fog, ultra detailed, 8k, cinematic camera movement."
    },
    {
        "id": "wedding",
        "title": "Indian Wedding Portrait",
        "type": "Image",
        "category": "Photography",
        "description": "Regal bridal portraiture with rich tradition and light.",
        "tags": ["Wedding", "India", "Portrait"],
        "author": "Naina Kapoor",
        "likes": "2.7k",
        "copies": "7.4k",
        "img": "https://images.pexels.com/photos/32170148/pexels-photo-32170148.jpeg?auto=compress&cs=tinysrgb&w=800",
        "prompt_text": "Elegant Indian bridal portrait, traditional red and gold lehenga, soft natural light, intricate jewelry, cinematic shallow depth of field, editorial photography style."
    },
    {
        "id": "anime",
        "title": "Anime Character Design",
        "type": "Image",
        "category": "Anime",
        "description": "Vivid character direction with expressive colour and mood.",
        "tags": ["Anime", "Character", "Art"],
        "author": "Kai Mori",
        "likes": "4.2k",
        "copies": "15.7k",
        "img": "https://images.pexels.com/photos/4208443/pexels-photo-4208443.jpeg?auto=compress&cs=tinysrgb&w=800",
        "prompt_text": "Anime style character design of a young warrior girl with silver hair, glowing blue eyes, detailed armor, dynamic pose, vibrant colors, high quality illustration."
    },
    {
        "id": "minimal",
        "title": "Minimal Product Ad",
        "type": "Image",
        "category": "Business",
        "description": "Clean commercial compositions made for modern brands.",
        "tags": ["Minimal", "Ad", "Product"],
        "author": "Zara Khan",
        "likes": "1.5k",
        "copies": "5.6k",
        "img": "https://images.pexels.com/photos/8015461/pexels-photo-8015461.jpeg?auto=compress&cs=tinysrgb&w=800",
        "prompt_text": "Minimal product advertisement of a modern skincare bottle on clean white background, soft shadows, elegant composition, commercial photography style."
    }
]

CATEGORIES = [
    {"emoji": "🎨", "name": "Image Prompts", "count": "12,400"},
    {"emoji": "🎬", "name": "Video Prompts", "count": "3,280"},
    {"emoji": "📸", "name": "Photography", "count": "6,890"},
    {"emoji": "🎥", "name": "Cinematic", "count": "4,120"},
    {"emoji": "👗", "name": "Fashion", "count": "2,450"},
    {"emoji": "🏠", "name": "Architecture", "count": "1,980"},
    {"emoji": "🎭", "name": "Anime", "count": "3,720"},
    {"emoji": "🚗", "name": "Cars", "count": "1,240"},
    {"emoji": "🍔", "name": "Food", "count": "2,010"},
    {"emoji": "🌄", "name": "Travel", "count": "2,890"},
    {"emoji": "💼", "name": "Business", "count": "1,670"},
    {"emoji": "📱", "name": "Social Media", "count": "4,560"},
]

# In-memory submitted prompts (for demo)
SUBMITTED_PROMPTS = []

def get_favorites():
    return session.get("favorites", [])

def get_prompt_by_id(prompt_id):
    for p in PROMPTS:
        if p["id"] == prompt_id:
            return p
    return None

# ====================== ROUTES ======================

@app.route("/")
def home():
    quick_cat = request.args.get("cat", "All")
    if quick_cat == "All":
        featured = PROMPTS
    else:
        featured = [p for p in PROMPTS if matches_category(p, quick_cat)]
    
    return render_template(
        "home.html",
        prompts=featured,
        all_prompts=PROMPTS,
        categories=CATEGORIES,
        quick_category=quick_cat,
        favorites=get_favorites(),
        active_page="home"
    )

@app.route("/explore")
def explore():
    q = request.args.get("q", "").lower()
    category = request.args.get("category", "All Categories")
    filter_type = request.args.get("filter", "All")
    
    items = PROMPTS.copy()
    
    # Filter by type
    if filter_type in ["Image", "Video"]:
        items = [p for p in items if p["type"] == filter_type]
    
    # Filter by category
    if category and category != "All Categories":
        items = [p for p in items if matches_category(p, category)]
    
    # Search
    if q:
        items = [p for p in items if q in (p["title"] + " " + p["description"] + " " + " ".join(p["tags"])).lower()]
    
    return render_template(
        "explore.html",
        prompts=items,
        categories=CATEGORIES,
        current_q=q,
        current_category=category,
        current_filter=filter_type,
        favorites=get_favorites(),
        active_page="explore"
    )

@app.route("/categories")
def categories():
    return render_template(
        "categories.html",
        categories=CATEGORIES,
        active_page="categories"
    )

@app.route("/prompt/<prompt_id>")
def detail(prompt_id):
    prompt = get_prompt_by_id(prompt_id)
    if not prompt:
        flash("Prompt not found", "error")
        return redirect(url_for("explore"))
    
    return render_template(
        "detail.html",
        prompt=prompt,
        favorites=get_favorites(),
        active_page="detail"
    )

@app.route("/favorites")
def favorites():
    fav_ids = get_favorites()
    fav_prompts = [p for p in PROMPTS if p["id"] in fav_ids]
    return render_template(
        "favorites.html",
        prompts=fav_prompts,
        favorites=fav_ids,
        active_page="favorites"
    )

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        new_prompt = {
            "id": f"user-{len(SUBMITTED_PROMPTS) + 1}",
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "prompt_text": request.form.get("prompt"),
            "category": request.form.get("category"),
            "type": request.form.get("type"),
            "tags": [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()],
            "author": "You",
            "likes": "0",
            "copies": "0",
            "img": "https://images.pexels.com/photos/11032525/pexels-photo-11032525.jpeg?auto=compress&cs=tinysrgb&w=800",
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        SUBMITTED_PROMPTS.append(new_prompt)
        flash("Prompt submitted successfully for review!", "success")
        return redirect(url_for("submit_success"))
    
    return render_template(
        "submit.html",
        categories=CATEGORIES,
        active_page="submit"
    )

@app.route("/submit/success")
def submit_success():
    return render_template("submit.html", success=True, categories=CATEGORIES, active_page="submit")

@app.route("/profile")
def profile():
    fav_ids = get_favorites()
    fav_prompts = [p for p in PROMPTS if p["id"] in fav_ids][:2]
    my_prompts = SUBMITTED_PROMPTS[-2:] if SUBMITTED_PROMPTS else PROMPTS[1:3]
    viewed = PROMPTS[3:5]
    
    return render_template(
        "profile.html",
        fav_prompts=fav_prompts,
        my_prompts=my_prompts,
        viewed_prompts=viewed,
        stats={
            "saved": len(fav_ids),
            "created": len(SUBMITTED_PROMPTS),
            "copies": "12.8k",
            "likes": "1.4k"
        },
        active_page="profile"
    )

# ====================== API ROUTES ======================

@app.route("/api/toggle-favorite/<prompt_id>", methods=["POST"])
def toggle_favorite(prompt_id):
    favorites = get_favorites()
    if prompt_id in favorites:
        favorites.remove(prompt_id)
        action = "removed"
    else:
        favorites.append(prompt_id)
        action = "added"
    session["favorites"] = favorites
    return jsonify({"status": "ok", "action": action, "favorites": favorites})

@app.route("/api/copy/<prompt_id>")
def copy_prompt(prompt_id):
    prompt = get_prompt_by_id(prompt_id)
    if prompt:
        return jsonify({"prompt": prompt["prompt_text"]})
    return jsonify({"error": "Not found"}), 404

# ====================== HELPERS ======================

def matches_category(p, name):
    if name in ["All", "All Categories"]:
        return True
    if name == "Image Prompts":
        return p["type"] == "Image"
    if name == "Video Prompts":
        return p["type"] == "Video"
    return p["category"] == name

# Make helper available in templates
app.jinja_env.globals.update(matches_category=matches_category)

if __name__ == "__main__":
    app.run(debug=True, port=5000)