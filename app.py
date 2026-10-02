"""
Main Flask Backend
GSDCNet Plant Disease Detection + Chatbot Integration
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from tensorflow.keras.models import load_model
import numpy as np
import json
import os
import io
from PIL import Image

# Import from our own modules
from chatbot.advice import get_advice, handle_text_query, get_disease_info, get_statistics
from utils.preprocess import preprocess_image_from_pil, parse_class_name, is_healthy

app = Flask(__name__)
CORS(app)

# ============================================
# LOAD MODEL AND CLASS MAPPINGS
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'best_model.h5')
CLASS_INDICES_PATH = os.path.join(BASE_DIR, 'model', 'class_indices.json')

print("⏳ Loading GSDCNet model...")
model = load_model(MODEL_PATH, compile=False)
print("✅ Model loaded successfully!")

with open(CLASS_INDICES_PATH, 'r') as f:
    class_indices = json.load(f)

# class_indices.json format: {"0": "Apple___Apple_scab", ...}
class_names = {int(k): v for k, v in class_indices.items()}

print(f"🌿 Loaded {len(class_names)} disease classes")

CONFIDENCE_THRESHOLD = 0.70


# ============================================
# ROUTES
# ============================================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main endpoint: Upload leaf image -> Get disease prediction + chatbot advice
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Load and preprocess image
        img = Image.open(io.BytesIO(file.read()))
        img_array = preprocess_image_from_pil(img)

        # Predict
        predictions = model.predict(img_array, verbose=0)
        predicted_idx = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_idx])
        predicted_class = class_names[predicted_idx]

        # Parse crop/disease name
        crop, disease = parse_class_name(predicted_class)
        healthy = is_healthy(disease)

        # Top 3 predictions
        top_3_idx = np.argsort(predictions[0])[-3:][::-1]
        top_3_predictions = [
            {
                'class': class_names[int(idx)],
                'confidence': float(predictions[0][idx])
            }
            for idx in top_3_idx
        ]

        # Get chatbot advice message
        chatbot_message = get_advice(predicted_class, confidence)

        # Get structured disease details
        disease_details = get_disease_info(predicted_class)

        return jsonify({
            'success': True,
            'prediction': {
                'crop': crop,
                'disease': disease,
                'full_class': predicted_class,
                'confidence': round(confidence, 4),
                'is_healthy': healthy,
                'is_confident': confidence >= CONFIDENCE_THRESHOLD
            },
            'top_predictions': top_3_predictions,
            'chatbot_response': chatbot_message,
            'disease_details': disease_details
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """
    Text-only chatbot endpoint (for follow-up questions without image)
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        user_message = data['message']
        bot_response = handle_text_query(user_message)

        return jsonify({
            'success': True,
            'response': bot_response
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/classes', methods=['GET'])
def get_classes():
    """Return all available disease classes"""
    return jsonify({
        'classes': list(class_names.values()),
        'total': len(class_names)
    })


@app.route('/stats', methods=['GET'])
def stats():
    """Return chatbot database statistics"""
    try:
        return jsonify({'success': True, 'statistics': get_statistics()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("\n🚀 Starting Flask server on http://localhost:5000 ...")
    app.run(debug=True, host='0.0.0.0', port=5000)
