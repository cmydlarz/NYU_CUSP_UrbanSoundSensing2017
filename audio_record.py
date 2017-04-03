"""Audio capture and real-time root mean squared (RMS) calculation script
using a non-blocking implementation of PyAudio

- Don't forget to turn off active/auto noise cancellation on your recording device
- If you have an external microphone make use of that
- Please bring headphones to the lecture

Script will prompt for entry of the device number for audio input you'd like to use.
If entry is invalid, script will default to device '-1', which uses the system default device.

Usage:
>python audio_record.py

Requirements:
PyAudio: https://people.csail.mit.edu/hubert/pyaudio/

How to install:

Windows
>python -m pip install pyaudio

OSX
>brew install portaudio
>pip install pyaudio

If you have issues, try this solution:
pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio

Linux
>sudo apt-get install python-pyaudio python3-pyaudio

"""

__author__ = "Charlie Mydlarz"
__version__ = "0.1"
__status__ = "Development"

import pyaudio
import time
import numpy as np
import wave

# Declare variable global so other threads can make use of it
global wavefile, recording

sample_rate = 44100                 # Sample rate of audio device
frames_per_buffer = 2048            # Number of audio frames delivered per hardware buffer return
channels = 1                        # Number of audio channels (1 = mono)
fname = str(time.time()) + '.wav'   # Output wave filename using current UTC time
total_duration = 60 * 5             # Total length of wave file
device_id = -1                      # Default audio input device ID
recording = True                    # Boolean check to hold while wait loop

# Initialize PyAudio
pa = pyaudio.PyAudio()


def select_audio_device():
    """ This method will list all the devices connected to host machine along with its index value"""
    print('Index\tValue\n===============')

    for i in range(pa.get_device_count()):
        devinfo = pa.get_device_info_by_index(i)

        # Convert dictionary key:value pair to a tuple
        for k in list(devinfo.items()):
            name, value = k

            if 'name' in name:
                print i, '\t', value

    try:
        return int(raw_input('\nEnter input device index: '))
    except ValueError:
        print "Not a valid device, falling back to default device"
        return -1

# List and select audio input device
device_id = select_audio_device()


def recorder_callback(in_data, frame_count, time_info, status_flags):
    """ This method is called whenever the audio device has acquired the number of audio samples
    defined in 'frames_per_buffer'. This method is called by a different thread to the main thread so some variables
    need to be declared global when altered within it. Avoid any heavy number crunching within this method as it
    can disrupt audio I/O if it blocks for too long.

    Args:
        in_data (str): Byte array of audio data from the audio input device.
        frame_count (int): Number of audio samples/frames received, will be equal to 'frames_per_nuffer'.
        time_info (dict): Dictionary of time information for audio sample data
        status_flags (long): Flag indicating any errors in audio capture
    """
    global wavefile, recording

    # Convert byte array data into numpy array with a range -1.0 to +1.0
    audio_data = np.fromstring(in_data, dtype=np.int16) / 32767.0

    # Calculate root mean squared of audio buffer
    rms = np.sqrt(np.mean(np.square(audio_data)))

    # Print RMS to console
    if rms > 0.2:
    	print rms
	print "Level exceeded!!!"

    # Write audio byte array values to wave file
    wavefile.writeframes(in_data)

    # If wavefile length is equal to the duration given then change recording flag
    if wavefile.getnframes() > total_duration * sample_rate:
        recording = False

    return None, pyaudio.paContinue

# Initialize recording stream object passing all predefined settings
recorder = pa.open(start=False,
                   input_device_index=device_id,
                   format=pyaudio.paInt16,
                   channels=channels,
                   rate=sample_rate,
                   input=True,
                   frames_per_buffer=frames_per_buffer,
                   stream_callback=recorder_callback)

# Open wave file ready for I/O
wavefile = wave.open(fname, 'wb')

# Set number of input channels
wavefile.setnchannels(channels)

# Set sample width = 2, as each 16bit sample value consists of 2 bytes: http://wavefilegem.com/how_wave_files_work.html
wavefile.setsampwidth(pa.get_sample_size(pyaudio.paInt16))

# Set sample rate at 44,100 sample values per second
wavefile.setframerate(sample_rate)

# Start recording stream, triggering hardware buffer fill and callback
recorder.start_stream()

# Hold script in loop waiting for wave file to meet desired file length in seconds
while recording:
    time.sleep(0.1)

# Close all open streams and files
recorder.close()
pa.terminate()
wavefile.close()
