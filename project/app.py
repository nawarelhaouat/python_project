from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime
from pydub import AudioSegment
from image_processing import apply_grayscale, apply_blur, apply_glitch, apply_invert, apply_sepia, apply_pixelate
app = Flask(__name__)
from style_transfer import apply_style_transfer


app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'


# Ensure folders exist



# Load audio file
def load_audio(filename):
    return AudioSegment.from_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# Apply effects
def apply_effect(audio, effect):
    if effect == "speed_up":
        return audio.speedup(playback_speed=1.5, chunk_size=150, crossfade=25)
    elif effect == "fade":
        return audio.fade_in(2000).fade_out(2000)
    elif effect == "reverse":
        return audio.reverse()
    elif effect == "louder":
        return audio + 10  # Increase volume by 10dB
    return audio

# Generate soundscape
def generate_soundscape():
    rain_file = os.path.join(app.config['UPLOAD_FOLDER'], "rain.wav")
    thunder_file = os.path.join(app.config['UPLOAD_FOLDER'], "thunder.wav")
    piano_file = os.path.join(app.config['UPLOAD_FOLDER'], "piano.mp3")

    # Check if soundscape files exist
    for file in [rain_file, thunder_file, piano_file]:
        if not os.path.exists(file):
            return None

    try:
        rain = AudioSegment.from_file(rain_file)
        thunder = AudioSegment.from_file(thunder_file)
        piano = AudioSegment.from_file(piano_file)

        soundscape = rain.overlay(thunder, position=5000)  # Thunder starts at 5 seconds
        soundscape = soundscape.overlay(piano, position=10000)  # Piano starts at 10 seconds
        return soundscape
    except Exception as e:
        print(f"Error generating soundscape: {e}")
        return None
    
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_image", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return render_template("gallery.html", image=file.filename)

@app.route("/apply_filter/<filter_name>/<filename>")
def apply_filter(filter_name, filename):
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filter_name}_{filename}")
    if filter_name == "grayscale":
        apply_grayscale(input_path, output_path)
    elif filter_name == "blur":
        apply_blur(input_path, output_path)
    elif filter_name == "glitch":
        apply_glitch(input_path, output_path)
    ############################################################
    elif filter_name == "invert":
        apply_invert(input_path, output_path)
    elif filter_name == "sepia":
        apply_sepia(input_path, output_path)
    elif filter_name == "pixelate":
        apply_pixelate(input_path, output_path)
    ############################################################
    return render_template("view_art.html", image=f"{filter_name}_{filename}")

@app.route('/', methods=["POST"])
def upload_audio():
    file = request.files.get('file')
    if not file or file.filename == '':
        return "No file selected", 400

    if file.filename == '':
        return "File format not allowed", 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    return redirect(url_for('audio_processing', filename=file.filename))

@app.route('/audio_processing/<filename>')
def audio_processing(filename):
    return render_template('audio_processing.html', filename=filename)

@app.route('/apply_effect/<effect>/<filename>')
def apply_audio_effect(effect, filename):
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{effect}_{filename}")

    # Load and apply effect
    audio = load_audio(filename)
    processed_audio = apply_effect(audio, effect)
    processed_audio.export(output_path, format="mp3")

    return send_from_directory(app.config['PROCESSED_FOLDER'], f"{effect}_{filename}")

@app.route('/generate_soundscape')
def generate_audio_soundscape():
    soundscape = generate_soundscape()
    if soundscape:
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], "soundscape.mp3")
        soundscape.export(output_path, format="mp3")
        return send_from_directory(app.config['PROCESSED_FOLDER'], "soundscape.mp3")
    return "Error generating soundscape", 500


@app.route('/view_images')
def view_images():
    # Get a list of all files in the uploads folder
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    # Filter only image files (you can add more extensions if needed)
    images = [img for img in images if img.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('view_images.html', images=images)

# Route to serve individual images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

############################################################################
@app.route('/draw')
def draw():
    os.system("python interactive_art.py")  # Exécute interactive_art.py
    return "<script>window.history.back();</script>"

@app.route('/view_images')
def gallery():
    # Liste des images sauvegardées dans le dossier static/
    images = sorted(
        [img for img in os.listdir("static") if img.lower().endswith((".png", ".jpg", ".jpeg"))],
        reverse=True
    )
    return render_template('view_images.html', images=images, now=datetime.now().timestamp())

@app.route('/visualization')
def visualization():
    os.system("python visualization.py")  # Exécute visualization.py
    return "<script>window.history.back();</script>"

@app.route('/style_transfer', methods=['GET', 'POST'])
def style_transfer():
    if request.method == 'GET':
        return render_template("style_transfer.html")

    if 'content' not in request.files or 'style' not in request.files:
        return redirect(url_for('style_transfer'))
    
    content_file = request.files['content']
    style_file = request.files['style']
    
    if content_file.filename == '' or style_file.filename == '':
        return redirect(url_for('style_transfer'))
    
    content_path = os.path.join(app.config['UPLOAD_FOLDER'], content_file.filename)
    style_path = os.path.join(app.config['UPLOAD_FOLDER'], style_file.filename)
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"styled_{content_file.filename}")
    
    content_file.save(content_path)
    style_file.save(style_path)
    
    apply_style_transfer(content_path, style_path, output_path)
    
    return render_template("style_transfer.html", output_image=output_path)



if __name__ == "__main__":
    app.run(debug=True)