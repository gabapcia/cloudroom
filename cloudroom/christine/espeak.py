import subprocess, re, os
from typing import List, Dict, NoReturn, AnyStr


class Espeak:
    def __init__(
            self, 
            amplitude:int=100, 
            device:AnyStr=None, 
            voice:str='en', 
            speed:int=175, 
            pitch:int=50
        ):
        
        if not os.path.exists(os.path.join('/', 'usr', 'bin', 'espeak-ng')):
            raise RuntimeError('espeak-ng not found')
        
        assert amplitude >= 0 and amplitude <= 200, \
            'Amplitude must be between 0 and 200'
        
        assert pitch >= 0 and pitch <= 99, 'Pitch must be between 0 and 99'
        
        self.amplitude = amplitude
        self.device = device
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
    
    
    def get_command(self, phrase:AnyStr) -> List[AnyStr]:
        return [
            'espeak-ng',
            '-a',
            str(self.amplitude),
            '-d',
            self.device or '',
            '-p',
            str(self.pitch),
            '-s',
            str(self.speed),
            '-v',
            self.voice,
            phrase
        ]

    
    def say(self, phrase:AnyStr, sync:bool=False) -> NoReturn:
        if sync:
            subprocess.run(args=self.get_command(phrase=phrase))
        else:
            subprocess.Popen(args=self.get_command(phrase=phrase))

    
    def voices(self) -> List[Dict[AnyStr, AnyStr]]:
        output = subprocess.run(
            args=['espeak-ng', '--voices'],
            capture_output=True
        ).stdout.decode().split('\n')
        
        del output[0]
        header = [
            'Pty',
            'Language',
            'Age/Gender',
            'VoiceName',
            'File',
            'Other Languages',
        ]

        _voices = []
        for line in output:
            line_dict = {
                header[i]: v.strip() \
                    for i, v in enumerate(
                        re.split(
                            r'\s{1,}', line.strip(), maxsplit=len(header) - 1
                        )
                    ) if v.strip()
            }
            if line_dict:
                _voices.append(line_dict)
        
        return _voices
    
    
    def read_file(self, text_file:AnyStr, sync:bool=False) -> NoReturn:
        if not os.path.exists(text_file):
            raise FileNotFoundError

        arguments = [
            'espeak-ng',
            '-f',
            text_file
        ]
        if sync:
            subprocess.run(args=arguments)
        else:
            subprocess.Popen(args=arguments)


if __name__ == '__main__':
    Espeak().say('Hello, and, again, welcome to the Aperture Science Computer-aided Enrichment Center')