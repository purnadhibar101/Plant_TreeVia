from flask import Flask, render_template, request, jsonify, url_for
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

app = Flask(__name__, static_url_path='/static', template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'static/photos'

# --- LOAD MODEL ---
try:
    model_path = "model.h5"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- CLASS LABELS (Ensure this matches training and JS) ---
CLASS_LABELS = {
    0: 'Anthracnose', 1: 'Bacterial Canker', 2: 'Cutting Weevil',
    3: 'Die Back', 4: 'Gall Midge', 5: 'Healthy',
    6: 'Powdery Mildew', 7: 'Sooty Mould'
}

# --- CONFIDENCE THRESHOLD ---

CONFIDENCE_THRESHOLD = 0.5 


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/predict", methods=['POST'])
def predict():
    if not model:
        print("Prediction failed: Model not loaded.")

        return jsonify({'error': 'Model not available. Please contact support.', 'is_likely_mango': False}), 500

    if 'image' not in request.files:
        print("Prediction failed: No image file part.")
        return jsonify({'error': 'No image file received by server.', 'is_likely_mango': False}), 400

    file = request.files['image']
    if file.filename == '':
        print("Prediction failed: No image selected.")
        return jsonify({'error': 'No image file selected in the request.', 'is_likely_mango': False}), 400

    if file:
        try:
            print(f"Received file: {file.filename}")
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            img = img.resize((128, 128))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            print(f"Image preprocessed, shape: {img_array.shape}")

            # Make prediction
            prediction = model.predict(img_array)
            prediction_list = prediction.tolist()
            print(f"Raw prediction probabilities: {prediction_list[0]}")

            # --- CONFIDENCE CHECK ---
            max_probability = np.max(prediction[0])
            print(f"Highest probability: {max_probability:.4f}")

            if max_probability < CONFIDENCE_THRESHOLD:
                print(f"Confidence below threshold ({CONFIDENCE_THRESHOLD}). Likely not a recognized mango leaf.")

                return jsonify({
                    'error': f'Input image does not appear to be a mango leaf recognized by the model (Max Confidence: {max_probability*100:.1f}%). Please upload a clear image of a mango leaf.',
                    'is_likely_mango': False
                }), 400

            predicted_index = np.argmax(prediction[0])
            predicted_class_name = CLASS_LABELS.get(predicted_index, "Unknown Class")
            print(f"Predicted class index: {predicted_index}, name: {predicted_class_name}, confidence: {max_probability:.4f}")

            return jsonify({
                "predicted_class": predicted_class_name,
                "probabilities": prediction_list[0],
                "is_likely_mango": True 
            })

        except Image.UnidentifiedImageError:
             print(f"Error: Cannot identify image file. It might be corrupted or not an image.")
             return jsonify({'error': 'Uploaded file is not a valid image or is corrupted.', 'is_likely_mango': False}), 400
        except Exception as e:
            print(f"Error processing image or predicting: {e}")
            return jsonify({'error': f'Server error during image processing or prediction. Please try again.', 'is_likely_mango': False}), 500

    print("Prediction failed: Invalid file state.") 
    return jsonify({'error': 'Invalid file provided.', 'is_likely_mango': False}), 400

if __name__ == "__main__":
    app.run(debug=True)