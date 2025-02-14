from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime
from pydub import AudioSegment
from image_processing import apply_grayscale, apply_blur, apply_glitch, apply_invert, apply_sepia, apply_pixelate
app = Flask(__name__)
from style_transfer import apply_style_transfer

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PROCESSED_FOLDER = 'static/processed'

app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER


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

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(url_for('image_processing'))  

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('image_processing'))

    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return redirect(url_for('image_processing', image=filename))

@app.route('/image_processing')
def image_processing():
    image_filename = request.args.get('image', '')  
    result_image_filename = request.args.get('result_image', '')
    return render_template('image_processing.html', image=image_filename, result_image=result_image_filename)
    
@app.route("/apply_filter/<filter_name>/<filename>")
def apply_filter(filter_name, filename):
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = f"{filter_name}_{filename}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Apply the corresponding filter
    if filter_name == "grayscale":
        apply_grayscale(input_path, output_path)
    elif filter_name == "blur":
        apply_blur(input_path, output_path)
    elif filter_name == "glitch":
        apply_glitch(input_path, output_path)
    elif filter_name == "invert":
        apply_invert(input_path, output_path)
    elif filter_name == "sepia":
        apply_sepia(input_path, output_path)
    elif filter_name == "pixelate":
        apply_pixelate(input_path, output_path)
    return redirect(url_for('image_processing', image=filename, result_image=output_filename))



# Route for uploading, processing, and displaying audio on the same page
@app.route('/audio_processing', methods=['GET', 'POST'])
def audio_processing():
    filename = None
    processed_filename = None

    if request.method == 'POST':
        # Check if the user uploaded a file
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

        # Check if the user applied an effect
        if 'effect' in request.form and 'filename' in request.form:
            effect = request.form['effect']
            filename = request.form['filename']
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if os.path.exists(input_path):
                audio = load_audio(filename)
                processed_audio = apply_effect(audio, effect)

                processed_filename = f"{effect}_{filename}"
                output_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
                processed_audio.export(output_path, format="mp3")

    return render_template('audio_processing.html', filename=filename, processed_filename=processed_filename)

# Route to serve audio files
@app.route('/static/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/generate_audio_soundscape', methods=['GET', 'POST'])
def generate_audio_soundscape():
    soundscape = generate_soundscape()  # Call function to create soundscape

    if soundscape:
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], "soundscape.mp3")
        soundscape.export(output_path, format="mp3")
        return redirect(url_for('audio_processing', soundscape_created=True))
    else:
        return "Soundscape generation failed. Make sure required files exist.", 400


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