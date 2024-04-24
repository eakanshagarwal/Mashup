from flask import Flask, render_template, request, redirect, url_for, flash
import os
import re
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from moviepy.editor import *
from pytube import YouTube
from youtubesearchpython import VideosSearch

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


OUTPUT_PATH = "mashup"

#get video urls
def get_video_urls(artist_name,num_clips):
    prefix = "https://www.youtube.com/watch?v="
    search_results = VideosSearch(artist_name, limit=num_clips).result()["result"]
    video_urls = [prefix + result["id"] for result in search_results]
    return video_urls

#download yt videos
def download_videos(artist_name,num_clips):
    #flash("Videos being downloaded")
    i=1
    urls = get_video_urls(artist_name, num_clips)
    output_path = os.path.join(OUTPUT_PATH, "videos")
    for url in urls:
        yt = YouTube(url)
        stream = yt.streams.get_lowest_resolution()
        print("Downloading:", yt.title)
        stream.download(output_path, filename=f"video{i}.mp4")
        print("Download complete!")
        i=i+1
    return output_path


#convery video to audio
def video_to_audio():
    #flash("Converting to audios")
    i=1
    videos_path = os.path.join(OUTPUT_PATH,"videos")
    output_path = output_path = os.path.join(OUTPUT_PATH, "audio")
    os.makedirs(output_path,exist_ok=True)
    videos = os.listdir(videos_path)
    for video in videos:
        temp_path = os.path.join(videos_path, video)
        video_clip = VideoFileClip(temp_path)
        audio_clip = video_clip.audio
        audio_save_path = os.path.join(output_path, f"audio{i}.mp3")
        audio_clip.write_audiofile(audio_save_path)
        i=i+1
        audio_clip.close()
        video_clip.close()

    return output_path


#trim audios
def trim_audio(trim_seconds):
    #flash("Trimming the audio")
    audio_path = os.path.join(OUTPUT_PATH,"audio")
    output_path = output_path = os.path.join(OUTPUT_PATH, "trimmed")
    os.makedirs(output_path,exist_ok=True)
    audios = os.listdir(audio_path)
    print(audios)
    i=1
    for audio in audios:
        input_path = os.path.join(audio_path, audio)
        trimmed_audio_save_path = os.path.join(output_path,f"trimmed_audio{i}.mp3")
        audio_clip = AudioFileClip(input_path)
        trimmed_audio = audio_clip.subclip(trim_seconds, audio_clip.duration)
        trimmed_audio.write_audiofile(trimmed_audio_save_path)
        i=i+1

    return output_path



#join trimmed audios
def concatinate_audio_files(output_filename):
    #flash("Creating your Mashup!!")
    trimmed_audio_path= os.path.join(OUTPUT_PATH,"trimmed")
    output_final_mashup = os.path.join(OUTPUT_PATH, "Final_Mashup")
    output_path = os.path.join(output_final_mashup, output_filename)
    os.makedirs(output_final_mashup,exist_ok=True)
    
    trimmed_clips = os.listdir(trimmed_audio_path)

    audio_clips = []
    for clip in trimmed_clips:
        temp_path = os.path.join(trimmed_audio_path, clip)
        audio_clip = AudioFileClip(temp_path)
        audio_clips.append(audio_clip)

    mashup = concatenate_audioclips(audio_clips)
    mashup.write_audiofile(output_path)

    for clips in audio_clips:
        clips.close()
    
    
    return output_final_mashup


#make mashup
def make_mashup(singer_name, num_vides, trim_durration, output_file):

    download_videos(singer_name, num_vides)
    video_to_audio()
    trim_audio(trim_durration)
    concatinate_audio_files(output_file)
    
    return


#make zipfile
def convert_to_zip(zip_filename):

    folder_name = os.path.join(OUTPUT_PATH, "Final_Mashup") 
    
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_name))

    return


def is_valid_email(email):
    # Regular expression for validating an email address
    email_regex = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def send_email(email):
    #flash("Writing an email")
    sender_email = "raghavgarg.1463@gmail.com"
    password = "sqya mofk afyk xvru"
    receiver_email = email

    if not is_valid_email(sender_email) or not is_valid_email(receiver_email):
        print("Invalid email address. Please provide valid email addresses.")
        exit()

    # Create a message object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = " Your Mashup is here!"

    # Add body to email
    body = "Download the attached zip file for your mashup."
    message.attach(MIMEText(body, "plain"))

    zipfile_path = "mashup.zip"  # Change this to the path of your zip file
    if os.path.exists(zipfile_path):
        with open(zipfile_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(zipfile_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(zipfile_path)}"'
            message.attach(part)

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # Change to your SMTP server and port
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
    finally:
        server.quit()




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        singer_name = request.form['singer_name']
        num_videos = int(request.form['num_videos'])
        duration = int(request.form['duration'])
        email = request.form['email']

        if not (singer_name and num_videos and duration and email):
            flash('Please fill in all the fields.')
            return redirect(request.url)


        make_mashup(singer_name,num_videos,duration,"output.mp3")
        convert_to_zip("mashup.zip")
        send_email(email)
        flash('Your request has been processed. Check your email for the result file.')


    return render_template('index.html')


