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

            splitter = filename.split('_')
            if len(splitter) == 3:
                # final case after 2 times processes - merge name of splitter[1] and splitter[2]
                new_filename = f'{splitter[0]}_{splitter[1]}{splitter[2]}' + '.' + ext

            elif len(splitter) == 2 and splitter[2] == "":
                # handling the case where the filename is written in camel case
                # e.g. ABeepProcessing_.wav to A_BeepProcessing_.wav
                new_filename = filename[0] + '_' + filename[1:] + '.' + ext
                
            else:
                if splitter[0] == "BEST":
                    spk_id = splitter[1]
                else:
                    spk_id = splitter[0]
                description = "_".join(splitter[1:])
                new_filename = f'{spk_id}_{description}' + '.' + ext

            os.rename(opj(path, file), opj(path, new_filename))

if __name__ == '__main__':
    path = opj(os.getcwd(), 'data', 'Phuoc', 'input')
    rename_files(path)