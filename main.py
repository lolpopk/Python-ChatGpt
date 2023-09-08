def GetText():
    import speech_recognition as sr
    import os
    from pydub import AudioSegment
    from pydub.silence import split_on_silence

    r = sr.Recognizer()

    def transcribe_audio(path):
        with sr.AudioFile(path) as source:
            audio_listened = r.record(source)
            text = r.recognize_google(audio_listened, language="uk-UA")
        return text

    def get_large_audio_transcription_on_silence(path):
        """Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks"""
        sound = AudioSegment.from_file(path)
        chunks = split_on_silence(sound,
                                  # experiment with this value for your target audio file
        min_silence_len=500,
                                  # adjust this per requirement
        silence_thresh=sound.dBFS - 14,
                                  # keep the silence for 1 second, adjustable as well
        keep_silence=500,
                                  )
        folder_name = "audio-chunks"
        # create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            try:
                text = transcribe_audio(chunk_filename)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                #print(chunk_filename, ":", text)
                whole_text += text
        # return the text for all chunks detected
        return whole_text

    return get_large_audio_transcription_on_silence('output.wav')

def GetAbstract(text):
    import openai

    with open('apiKey.txt', 'r') as read:
        openai.api_key = read.readline()

    model_engine = "text-davinci-003"

    completion = openai.Completion.create(
        engine = model_engine,
        prompt = short + text,
        temperature = 0.5,
        max_tokens = 1000,
        top_p = 1.0,
        frequency_penalty = 0.5,
        presence_penalty = 0.0,
    )

    response = completion.choices[0].text
    return response

def GetVideo():
    from pytube import YouTube
    import os
    from moviepy.editor import VideoFileClip
    fileName = "link.txt"

    with open(fileName, 'r') as read:
        link = read.readlines()

    yt = YouTube(str(link))
    video = yt.streams.filter().first()
    outFile = video.download()

    os.rename(outFile, 'outVideo.mp4')

    videoClip = VideoFileClip('outVideo.mp4')
    audioClip = videoClip.audio
    audioClip.write_audiofile('output.wav')

    return audioClip

def CreatePrompt():
    global short
    value = input("на сколько хочешь сократить текст(1-3) 1-мало сократить: ")
    if (value == "1"):
        short = "зроби конспект з цього українською мовою: "
    elif (value == "2"):
        short = "зроби коротенький конспект з цього українською мовою: "
    elif (value == "3"):
        short = "зроби дуже коротенький конспект з цього українською мовою:"
    else:
        short = "зроби конспект з цього українською мовою: "

def finish():
    import os
    os.remove('output.wav')
    os.remove('outVideo.mp4')

def main():
    CreatePrompt()
    GetVideo()
    print(GetAbstract(GetText()))
    finish()
    #GetAbstract("меня зовут тимофей я программист учись в школе номер 3")
    #with open('apiKey.txt', 'r') as read:
    #    print(read.readlines())
    while True:
        if (input("введите 'выход': ")):
            break


if __name__ == "__main__":
    main()

