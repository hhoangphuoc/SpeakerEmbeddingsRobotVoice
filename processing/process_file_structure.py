## rename the files in the current directory with the given format: <speaker_id>_<description>.wav

# NOTE: THIS FILE WILL ONLY USED 1 TIME ONLY - TO REFORMAT THE FILE STRUCTURE OF THE DATASET TO MATCH THE MODEL INPUT

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

# mapping sound id to speaker id
def get_spk_from_range(from_spk, to_spk):
    spk_list = []
    for i in range(from_spk, to_spk + 1):
        spk_list.append(str(i))
    return spk_list

def generate_speakers_mapping():
    # generate the mapping from sound id to speaker id
    sid_to_spk = {
        'r1': get_spk_from_range(1111, 1139),
        'r2': get_spk_from_range(1140, 1146),
        'r3': get_spk_from_range(1147, 1174),
        'r4': get_spk_from_range(1175, 1204),
        'r5': get_spk_from_range(1205, 1232),
        'r6': get_spk_from_range(1233, 1262),
        'r11': get_spk_from_range(1263, 1290),
        'r12': get_spk_from_range(1321, 1350),
        'r13': get_spk_from_range(1351, 1363),
        'r14': 'A',
        'r15': 'B',
        'r16': 'C',
        'r17': 'D',
        'r18': 'E',
        'r19': 'F',
        'r20': 'G',
        'r21': 'H',
        'r22': 'I',
        'r23': 'J',
        'r24': 'K',
        'r25': 'L',
        'r26': 'M',
        'r27': 'R2D2',
        'r28': 'WALL-E',
    }
    return sid_to_spk

def seperate_speakers(path):
    # function that seperate the speakers in current directory into different folder
    # by the speaker id, the speaker id is the first part of the filename
    speakers_mapping = generate_speakers_mapping()
    files = os.listdir(path)
    temp_folder_name = ''
    for file in files:
        if file.endswith('.wav'):
            filename, ext = file.split('.')
            spk_id = filename.split('_')[0] # eg: 1111, A, B, R2D2

            for key, value in speakers_mapping.items():
                if spk_id in value:
                    if not os.path.exists(opj(path, key)):
                        os.makedirs(opj(path, key))
                        temp_folder_name = key
            # move the file to the corresponding folder
            if not os.path.exists(opj(path, temp_folder_name, file)):
                os.rename(opj(path, file), opj(path, temp_folder_name, file))

def rename_files_by_spk(path):
    folders = os.listdir(path)
    for folder_name in folders:
        if os.path.isdir(opj(path, folder_name)):
            files = os.listdir(opj(path, folder_name))
            # rename the files prefix corresponding to speaker id
            for file in files:
                if file.endswith('.wav'):
                    filename, ext = file.split('.')
                    wav_name = filename.split('_')[1]
                    new_filename = f'{folder_name}_{wav_name}' + '.' + ext
                    os.rename(opj(path, folder_name, file), opj(path, folder_name, new_filename))


if __name__ == '__main__':
    path = opj(os.getcwd(), 'data', 'Phuoc', 'input')
    # rename_files(path)
    # seperate_speakers(path)
    # rename_files_by_spk(path)
