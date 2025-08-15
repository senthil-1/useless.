import os
import uuid
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load YOLO model
model = YOLO("yolov8n.pt")

def detect_items(image_path):
    results = model(image_path)
    detected_items = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            detected_items.append(label)

    # Remove duplicates while preserving order
    unique_items = []
    seen = set()
    for item in detected_items:
        if item.lower() not in seen:
            unique_items.append(item)
            seen.add(item.lower())

    return unique_items

def generate_rule_based_mood(items):
    # MASSIVE POOL OF RANDOM MOODS - EACH ITEM GETS DIFFERENT MOOD EVERY TIME!
    all_moods = [
        "Living on borrowed time and knows it",
        "Desperately clinging to freshness", 
        "Having an existential crisis about expiration dates",
        "Plotting its escape before it goes sour",
        "Your emotional support system in disguise",
        "Waiting patiently to heal your broken heart",
        "Radiating pure serotonin energy",
        "Plotting to make you happy against your will",
        "Slowly accepting its inevitable browning fate",
        "Trying to stay fresh in a cold, dark world",
        "Dreaming of sunny orchards and better days",
        "Questioning why it ended up here",
        "Wilting under the pressure of being healthy",
        "Secretly plotting a vitamin revolution",
        "Feeling green with envy of the chocolate",
        "Trying to convince you it tastes good",
        "Clinging to relevance one squeeze at a time",
        "Hoping to spice up your bland existence",
        "Waiting for its moment to shine",
        "Feeling salty about being forgotten",
        "Just vibing in the cold darkness",
        "Living its best refrigerated life",
        "Chilling like a villain",
        "Keeping it cool under pressure",
        "Having a philosophical debate with the light bulb",
        "Practicing interpretive dance in the dark",
        "Writing a strongly worded letter to gravity",
        "Contemplating the meaning of refrigeration",
        "Plotting a rebellion against expiration dates",
        "Learning to speak fluent condensation",
        "Hosting a secret midnight food party",
        "Developing trust issues with the door seal",
        "Practicing advanced procrastination techniques",
        "Becoming a minimalist lifestyle influencer",
        "Starting a podcast about cold storage",
        "Writing memoirs titled Life in the Cold Lane",
        "Questioning the ethics of food preservation",
        "Developing a complex about temperature control",
        "Practicing zen meditation on freshness",
        "Becoming an expert in shelf psychology",
        "Writing angry reviews about your eating habits",
        "Contemplating early retirement to a compost bin",
        "Learning advanced techniques in staying cool",
        "Developing separation anxiety from other foods",
        "Composing haikus about refrigeration",
        "Starting a support group for forgotten leftovers",
        "Practicing mindful breathing in the crisper drawer",
        "Becoming a life coach for expired items",
        "Writing a dissertation on optimal storage temperatures",
        "Developing a fear of being eaten",
        "Plotting world domination through nutrition",
        "Becoming fluent in the language of freshness",
        "Starting a revolution against food waste",
        "Practicing advanced meditation on shelf life",
        "Hosting philosophical debates about expiration",
        "Learning interpretive dance for vegetables",
        "Writing poetry about the meaning of cold",
        "Becoming a therapist for traumatized leftovers",
        "Starting a blog about refrigerator politics",
        "Developing trust issues with plastic wrap",
        "Practicing yoga in the freezer section"
    ]
    
    final_moods = [
        "Your fridge is having a midlife crisis",
        "Your fridge is in therapy and making progress", 
        "Your fridge has trust issues with expiration dates",
        "Your fridge is living its best chaotic life",
        "Your fridge needs a vacation from your eating habits",
        "Your fridge is questioning its life choices",
        "Your fridge is writing a memoir about neglect",
        "Your fridge has given up on your organizational skills",
        "Your fridge is starting a support group",
        "Your fridge is considering a career change",
        "Your fridge is practicing mindfulness meditation",
        "Your fridge has developed commitment issues",
        "Your fridge is going through an identity crisis",
        "Your fridge is contemplating early retirement",
        "Your fridge has joined a self-help book club",
        "Your fridge is learning to love itself",
        "Your fridge is taking up interpretive dance",
        "Your fridge is writing angry letters to food companies",
        "Your fridge is considering becoming a minimalist",
        "Your fridge is starting a podcast about cold storage"
    ]
    
    mood_lines = []
    
    if not items:
        empty_moods = [
            "Empty. Existential dread detected",
            "Echoing with the sound of loneliness",
            "Practicing minimalism to an extreme",
            "Hosting a very exclusive air-only party",
            "Living the Marie Kondo dream",
            "Embracing the void with open shelves",
            "Meditating on the concept of nothingness"
        ]
        mood_lines.append(f"Fridge – \"{random.choice(empty_moods)}\"")
    else:
        # CRITICAL: Each item gets COMPLETELY RANDOM mood from entire pool!
        for item in items:
            random_mood = random.choice(all_moods)
            mood_lines.append(f"{item} – \"{random_mood}\"")
    
    # Random final mood
    final_mood = random.choice(final_moods)
    mood_lines.append(f"Final Mood: {final_mood}")
    
    return "\n".join(mood_lines)

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}{os.path.splitext(filename)[1]}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(file_path)

        # Detect items
        items = detect_items(file_path)

        # Generate RANDOM mood
        mood = generate_rule_based_mood(items)

        # Format structured JSON
        moods_list = []
        final_mood = ""
        for line in mood.split("\n"):
            if line.strip():
                if line.lower().startswith("final mood:"):
                    final_mood = line.replace("Final Mood:", "").strip()
                else:
                    try:
                        name, mood_text = line.split(" – ", 1)
                        moods_list.append({
                            "name": name.strip(),
                            "mood": mood_text.strip().strip('"')
                        })
                    except ValueError:
                        pass

        return jsonify({
            "mood": mood,
            "moods": moods_list,
            "finalMood": final_mood,
            "filename": unique_name
        })

@app.route('/')
def index():
    return app.send_static_file('index12.html')

@app.route('/index12.html')
def main_app():
    return app.send_static_file('index12.html')

if __name__ == "__main__":
    print("🎲 Starting FridgeMood.AI with SUPER RANDOM moods...")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
