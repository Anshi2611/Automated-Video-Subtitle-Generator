import moviepy.editor as mp
from pydub import AudioSegment
import speech_recognition as sr
import subprocess
from pydub.silence import split_on_silence
import os
import datetime

# Load video
video = mp.VideoFileClip("Eng_speech.mp4")

# Extract audio
audio = video.audio
audio.write_audiofile("Audio.mp3")

# Convert MP3 to WAV using ffmpeg
subprocess.call(['ffmpeg', '-i', 'Audio.mp3', 'Audio.wav'])

# Load the audio file for processing
audio_file = sr.AudioFile('Audio.wav')

# Initialize the recognizer
r = sr.Recognizer()

r.energy_threshold = 500
r.pause_threshold = 0.5
r.dynamic_energy_threshold = True
r.dynamic_energy_adjustment_damping = 0.15
r.dynamic_energy_ratio = 1.5
r.operation_timeout = None
r.phrase_threshold = 0.3
r.non_speaking_duration = 0.2
r.pause_threshold = 0.8
r.phrase_threshold = 0.1
r.buffer_size = 1
r.dynamic_energy_adjustment_ratio = 1.5

# Create a subtitle file
subtitle_file = open('output.srt', 'w')

# Get the duration of the audio clip
with mp.AudioFileClip('Audio.wav') as audio_clip:
    duration = audio_clip.duration

# Initialize subtitle counter and timestamps
subtitle_num = 1
start_time = 0
end_time = 0

# Process audio segments and generate subtitles
with audio_file as source:
    sound = AudioSegment.from_wav("Audio.wav")
    chunks = split_on_silence(sound,
        min_silence_len=500,
        silence_thresh=sound.dBFS-14,
        keep_silence=500
    )

    recognizer = sr.Recognizer()
    subtitles = []

    for i, chunk in enumerate(chunks):
        chunk_path = f"chunk{i}.wav"
        chunk.export(chunk_path, format="wav")

        with sr.AudioFile(chunk_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = r.recognize_sphinx(audio_data)
            except sr.UnknownValueError:
                text = ""

        # Calculate timestamps
        start_time = (i * 500) / 100.0
        end_time = ((i + 1) * 500) / 100.0

        print(end_time)

        # Write the subtitle to file
        subtitle_file.write(str(subtitle_num) + '\n')
        start_time_str = '{:0>8}'.format(str(datetime.timedelta(seconds=start_time)))[:8]
        end_time_str = '{:0>8}'.format(str(datetime.timedelta(seconds=end_time)))[:8]
        subtitle_file.write(start_time_str + ' --> ' + end_time_str + '\n')
        subtitle_file.write(text + '\n\n')

        subtitle_num += 1

# Close the subtitle file
subtitle_file.close()

# Delete chunk files
for filename in os.listdir("."):
    if filename.startswith("chunk") and filename.endswith(".wav"):
        os.remove(filename)
