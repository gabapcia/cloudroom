import os, pyaudio
from vosk import Model, KaldiRecognizer
from typing import Callable, AnyStr, NoReturn


class Chris:
    keep_listening = True


    def __init__(
            self, 
            model_path:AnyStr, 
            callback:Callable[[AnyStr], NoReturn]
        ):
        self.callback = callback
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)


    def listen(self) -> NoReturn:
        stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16, 
            channels=1, 
            rate=16000, 
            input=True, 
            frames_per_buffer=8000   
        )

        stream.start_stream()

        while self.keep_listening:
            data = stream.read(5000, False)
            if self.recognizer.AcceptWaveform(data):
                self.callback(self.recognizer.Result())

        stream.stop_stream()
