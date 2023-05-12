# Call-and-Transcribe Application Documentation

This application is a robust solution that leverages the Telnyx API for call management and the OpenAI API for transcription services. It allows you to initiate multiple calls to a list of numbers, play a sound during each call, record the calls, and transcribe the recordings. The transcriptions along with other call details are written to a TSV (Tab-Separated Values) file.

You can find the backstory of this app in the tweet below: 

https://twitter.com/yigitkonur/status/1654827917845860353

## Application Setup

The application is developed in Python and uses the Flask framework for managing incoming webhooks. It also uses the Telnyx and OpenAI APIs, so you need to have valid API keys for these services.

## Key Functions

1. `call_and_play_sound(number)`: Initiates a call to a given number and stores the call information in a global dictionary. The actual sound playback starts after the call is answered.

2. `transcribe_call(call_control_id)`: Retrieves the recording of a completed call, transcribes it using the OpenAI API, and writes the result (along with the caller and recipient numbers and call duration) to a TSV file.

3. `load_numbers(filename)`: Loads a list of phone numbers from a text file, where each line contains one number.

4. `process_number(number)`: A wrapper for `call_and_play_sound(number)`. This function is designed to be used with multi-threading.

5. `multi_threaded_call(numbers)`: Uses a thread pool to manage multiple calls simultaneously.

6. `display_progress(numbers)`: Uses the Rich library to display a progress bar and a table summarizing the call results.

## Webhook Routes

1. `@app.route("/webhook", methods=["POST"])`: Handles various call events, such as call initiation, answer, and hangup. It starts audio playback and recording when a call is answered, and triggers transcription when a call is hung up.

2. `@app.route("/webhook/call-recording-saved", methods=["POST"])`: Handles the event when a call recording is saved on the Telnyx platform. It downloads the audio file and transcribes it.

## Usage

To use the application, follow these steps:

1. Place the list of phone numbers (one per line) in a text file.

2. Run the application. Make sure to set up an environment where the Telnyx and OpenAI APIs are accessible.

3. The application will start calling the numbers in the list, playing a sound file on each call, recording the call, and transcribing the call once it's completed.

4. The transcription results are stored in a TSV file named `results.tsv`, with the columns "From Number", "To Number", "Text", and "Total Call Duration".

## Important Notes

Please ensure to replace the placeholder `xxxxxxxxxxxxxxx` in the code with your actual API keys and other required values such as the connection_id for Telnyx, the 'from' number for making calls, and the sound file's URL.

Also, note that this application assumes the Flask server and your Telnyx account are properly configured to handle the webhook events.


# Audio Transcription Application Documentation

The second Python script (transcriber.py) is designed to transcribe a bulk of audio files using OpenAI's API. It searches for audio files in a specified directory, transcribes the content of each file, and then stores the transcriptions in a Tab-Separated Values (TSV) file. It supports different audio formats including mp3, mp4, mpeg, mpga, m4a, wav, and webm.

## Key Functions

1. `transcribe_audio(filename)`: This function transcribes a given audio file using OpenAI's API. It applies an exponential backoff strategy to handle possible exceptions during the transcription process.

## Workflow of the Script

1. The script begins by setting the OpenAI API key. Make sure to replace `'sk-xxxxxxxxxx'` with your actual OpenAI API key.

2. The directory where the audio files are stored is specified. Change this to the directory path on your local machine where your audio files are stored.

3. It then prepares a list of all audio files in the specified directory.

4. A TSV file named `transcriptions.tsv` is created to store the transcriptions. Each row in the file represents an audio file and contains two fields: the filename and the transcription of the text in the audio file.

5. A progress bar is created using the Rich library to track the transcription process.

6. The script uses a ThreadPoolExecutor to concurrently transcribe multiple audio files. For each completed transcription, the result is written to the TSV file and the progress bar is updated.

## Usage

To use this script, ensure that you have the OpenAI Python client set up correctly and that the OPENAI_API_KEY environment variable is set to your OpenAI API key. Also, make sure to replace the directory path with the path of the directory that contains the audio files you want to transcribe.

Then, simply run the script. It will transcribe all the audio files in the specified directory and write the transcriptions to a TSV file named `transcriptions.tsv`.

## Important Note

This script uses a max_workers value of 3 for the ThreadPoolExecutor. This means that it will transcribe up to three audio files concurrently. You can adjust this value as needed based on the capabilities of your machine and the rate limits of your OpenAI API key.

Also, the script assumes that your OpenAI API key has sufficient privileges to use the Audio API for transcribing audio files.
