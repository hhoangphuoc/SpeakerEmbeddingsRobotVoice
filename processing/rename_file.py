## rename the files in the current directory with the given format: <speaker_id>_<description>.wav


import os
import sys
from os.path import join as opj


def rename_files(path):
    files = os.listdir(path)
    for file in files:
        if file.endswith('.wav'):
            filename, ext = file.split('.')

            spk_id = ""
            description = ""

            if len(filename.split('_')) == 0 and filename[0].isupper():
                # handling the case where the filename is written in camel case
                # e.g. ABeepProcessing.wav
                spk_id = filename[0]
                description = filename[1:]
            else:
                splitter = filename.split('_')
                if splitter[0] == "BEST":
                    spk_id = splitter[1]
                else:
                    spk_id = splitter[0]
                description = "_".join(splitter[1:])
            new_filename = f'{spk_id}_{description}' + '.' + ext

            os.rename(opj(path, file), opj(path, new_filename))
