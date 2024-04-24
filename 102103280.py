import os
import sys
import zipfile
from moviepy.editor import *
from pytube import YouTube
from youtubesearchpython import VideosSearch

OUTPUT_PATH = "mashup"


#get video urls
def get_video_urls(artist_name,num_clips):
    prefix = "https://www.youtube.com/watch?v="
    search_results = VideosSearch(artist_name, limit=num_clips).result()["result"]
    video_urls = [prefix + result["id"] for result in search_results]
    return video_urls


#download yt videos
def download_videos(artist_name,num_clips):
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

#main funtion
def main():
    if len(sys.argv) != 5:
        print("Usage: python program.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer_name = sys.argv[1]
    num_videos = int(sys.argv[2])
    audio_duration = int(sys.argv[3])
    output_file = sys.argv[4]

    if num_videos < 10:
        print("Number of videos should be greater than 10")
        sys.exit(1)

    if audio_duration < 20:
        print("Audio duration should be greater than 20 seconds")
        sys.exit(1)

    try:
        make_mashup(singer_name, num_videos, audio_duration, output_file)
        print("Mashup generated successfully!")
        convert_to_zip("mashup.zip")
    except Exception as e:
        print(f"An error occurred: {e}")




if __name__ == "__main__":
    main()