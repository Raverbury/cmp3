import pyaudio
import pydub

filename = "audio/th8_10.wav"
# filename = "Love-colored Master Spark.mp3"

LOOP_START_SEC = 5.0
LOOP_END_SEC = 10.0

audio_segment: pydub.audio_segment.AudioSegment = pydub.AudioSegment.from_file(filename)

# Set chunk size of 1024 samples per data frame

# Open the sound file 

framerate = audio_segment.frame_rate
print(framerate)

chunk = int(float(1024.0/framerate) * 1000)

LOOP_START_FRAME = int(LOOP_START_SEC * 1000)
LOOP_END_FRAME = int(LOOP_END_SEC * 1000)

# Create an interface to PortAudio
p = pyaudio.PyAudio()

# print(wf.getframerate(), wf.getsampwidth())

# Open a .Stream object to write the WAV file to
# "output = True" indicates that the sound will be played rather than recorded
stream = p.open(format = p.get_format_from_width(audio_segment.sample_width),
                channels = audio_segment.channels,
                rate = framerate,
                output = True)

# Read data in chunks
data = ""
current_frame = 0

# Play the sound by writing the audio data to the stream
while True:
    data = (audio_segment[current_frame:current_frame+chunk]).raw_data
    print(current_frame)
    if data == "":
        break
    stream.write(data)
    current_frame += chunk
    if current_frame >= LOOP_END_FRAME:
        # wf.setpos(LOOP_START_FRAME)
        current_frame = LOOP_START_FRAME

# Close and terminate the stream
stream.close()
p.terminate()

# wf: wave.Wave_read = wave.open(filename, "rb")

# framerate = wf.getframerate()

# LOOP_START_FRAME = int(LOOP_START_SEC * framerate)
# LOOP_END_FRAME = int(LOOP_END_SEC * framerate)

# # Create an interface to PortAudio
# p = pyaudio.PyAudio()

# # print(wf.getframerate(), wf.getsampwidth())

# # Open a .Stream object to write the WAV file to
# # "output = True" indicates that the sound will be played rather than recorded
# stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
#                 channels = wf.getnchannels(),
#                 rate = wf.getframerate(),
#                 output = True)

# # Read data in chunks
# data = ""
# current_frame = 0

# # Play the sound by writing the audio data to the stream
# while True:
#     data = wf.readframes(chunk)
#     # print(wf.tell())
#     if data == "":
#         break
#     stream.write(data)
#     current_frame += chunk
#     if current_frame >= LOOP_END_FRAME:
#         wf.setpos(LOOP_START_FRAME)
#         current_frame = LOOP_START_FRAME

# # Close and terminate the stream
# stream.close()
# p.terminate()