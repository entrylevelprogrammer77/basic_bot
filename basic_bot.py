import pymongo
import spacy
import random
import requests
from flask import Flask, request, jsonify, render_template

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chatbot_db"]
collection = db["memory"]

def load_memory():
    """Load previous conversations from the database."""
    memory = {}
    for record in collection.find():
        memory[record["user_input"]] = record["bot_responses"]
    return memory

def save_memory(user_input, bot_response):
    """Save multiple responses for a user input."""
    existing_record = collection.find_one({"user_input": user_input})
    if existing_record:
        if bot_response not in existing_record["bot_responses"]:
            collection.update_one(
                {"user_input": user_input},
                {"$push": {"bot_responses": bot_response}}
            )
    else:
        collection.insert_one({"user_input": user_input, "bot_responses": [bot_response]})

def google_search(query):
    """Fetch a search result using Google's Search API."""
    search_url = f"https://www.google.com/search?q={query}"
    return f"I don't know the answer. You can check this link: {search_url}"

def get_response(user_input, memory):
    """Generate a response using NLP and update memory dynamically."""
    responses = {
        "hello": [
            "Hi there! How can I assist you today?",
            "Hello! What’s on your mind?",
            "Hey! How’s your day going?",
            "Hi! How can I help you?",
            "Greetings! What would you like to chat about?",
            "Hello there! Need assistance with something?",
            "Hi! Hope you're having a great day!",
            "Hey there! What’s up?",
            "Hello! Anything I can do for you?",
            "Hi! Let’s chat!"
        ],
        "how are you": ["I'm just a bot, but I'm doing great! How about you?"],
        "bye": ["Goodbye! Have a great day!"]
    }
    
    # Process user input with NLP
    doc = nlp(user_input.lower())
    
    # Check for keyword matches
    for key in responses:
        if key in user_input.lower():
            return random.choice(responses[key])
    
    # Use NLP similarity matching for smarter responses
    best_match = None
    best_score = 0.0
    for key in responses:
        similarity = nlp(key).similarity(doc)
        if similarity > best_score:
            best_score = similarity
            best_match = key
    
    if best_match and best_score > 0.6:
        return random.choice(responses[best_match])
    
    # If no match, check if user input exists in memory
    if user_input in memory:
        return random.choice(memory[user_input])
    
    # If no match, perform a Google search
    return google_search(user_input)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if user_input:
        memory = load_memory()
        response = get_response(user_input, memory)
        return jsonify({"response": response})
    return jsonify({"response": "I didn't get that. Can you try again?"})

@app.route("/update_response", methods=["POST"])
def update_response():
    """Allow manual updates to bot responses."""
    data = request.json
    user_input = data.get("user_input")
    new_response = data.get("new_response")
    
    if user_input and new_response:
        save_memory(user_input, new_response)
        return jsonify({"message": "Response updated successfully!"})
    
    return jsonify({"error": "Invalid input."}), 400

if __name__ == "__main__":
    app.run(debug=True)
