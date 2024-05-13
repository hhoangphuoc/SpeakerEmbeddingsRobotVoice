# -*- coding: utf-8 -*-
# Modifications
# 
# Original copyright:
# The copyright is under MIT license from VQMIVC.
# VQMIVC (https://github.com/Wendison/VQMIVC) / author: Wendison


import warnings
warnings.filterwarnings(action='ignore')

import os
from os.path import join as opj
import json
import random
import numpy as np
import librosa
import soundfile as sf
from joblib import Parallel, delayed
from glob import glob
from tqdm import tqdm
import resampy
import pyworld as pw


# # import spectrogram from TRIAAN-VC models instead of copy it to new file
# from models.triaanvc.preprocess.spectrogram import logmelspectrogram
from processing.spectrogram import logmelspectrogram

def ProcessingTrainData(path, cfg):
    """
        Processing both loading, resampling and normalising the wav file
        and calculating log-mel spectrogram of the wav file
        Output: processed file using for training data 
    """
    # Load and process wav file

    # skip pre-emphasis
    wav_name = os.path.basename(path).split('.')[0] # e.g: r1_1111anger
    speaker  = wav_name.split('_')[0] #eg. r1, r2,...
    sr       = cfg.sampling_rate # ensure sampling rate 16kHz
    wav, fs  = sf.read(path)
    wav, _   = librosa.effects.trim(y=wav, top_db=cfg.top_db) # trim slience

    # Normalise and resample
    # pitch shift
    wav = librosa.effects.pitch_shift(wav, sr, n_steps=cfg.pitch_shift) #shift pitch by 2 tones
    # resample
    if fs != sr:
        wav = resampy.resample(x=wav, sr_orig=fs, sr_new=sr, axis=0)
        fs  = sr
        
    assert fs == 16000, 'Downsampling needs to be done.'
    
    # normalise amplitude (loudness) ~ peak
    peak = np.abs(wav).max()
    if peak > cfg.peak_max:
        wav /= peak # divided to normalise
    elif peak < cfg.peak_min:
        wav *= cfg.peak_min / peak

    # Calculate log mel spectrogram -------------------------    
    mel = logmelspectrogram(
                            x=wav,
                            fs=cfg.sampling_rate,
                            n_mels=cfg.n_mels,
                            n_fft=cfg.n_fft,
                            n_shift=cfg.n_shift,
                            win_length=cfg.win_length,
                            window=cfg.window,
                            fmin=cfg.fmin,
                            fmax=cfg.fmax
                            )
    tlen         = mel.shape[0]
    frame_period = cfg.n_shift/cfg.sampling_rate*1000
    
    f0, timeaxis = pw.dio(wav.astype('float64'), cfg.sampling_rate, frame_period=frame_period)
    f0           = pw.stonemask(wav.astype('float64'), f0, timeaxis, cfg.sampling_rate)
    f0           = f0[:tlen].reshape(-1).astype('float32')
    
    nonzeros_indices      = np.nonzero(f0)
    lf0                   = f0.copy()
    lf0[nonzeros_indices] = np.log(f0[nonzeros_indices]) # for f0(Hz), lf0 > 0 when f0 != 0
    
    return wav_name, mel, lf0, mel.shape[0], speaker

# TODO: CHECK AND REMOVE IF NOT NEEDED
def SaveFeatures(wav_name, info, mode, cfg):
    
    mel, lf0, mel_len, speaker = info
    wav_path      = f'{cfg.data_path}/{speaker}/{wav_name}.wav' # can change to special char *
    mel_save_path = f'{cfg.output_path}/{mode}/mels/{speaker}/{wav_name}.npy'
    lf0_save_path = f'{cfg.output_path}/{mode}/lf0/{speaker}/{wav_name}.npy'
    
    os.makedirs(os.path.dirname(mel_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(lf0_save_path), exist_ok=True)
    np.save(mel_save_path, mel)
    np.save(lf0_save_path, lf0)
    
    # wav_name = wav_name.split('_')[0] # p231_001
    wav_name = wav_name.split('_')[1] # p231_001 #r1_1111anger -> 1111anger

    return {'mel_len':mel_len, 'speaker':speaker, 'wav_name':wav_name, 'wav_path':wav_path, 'mel_path':mel_save_path, 'lf0_path':lf0_save_path}
    

def NormalizeLogMel(wav_name, mel, mean, std):
    mel = (mel - mean) / (std + 1e-8)
    return wav_name, mel

##-------------------------------------------------------Train test split-------------------------------------------------------##
def GetSpeakerInfo(cfg):
    """
    Get all the speaker names and speaker ids from the data path
    - all_audios_name: list of all the names of audios files in every folder, e.g. r1_1111anger, r1_1112anger,...
    - all_spks_name: list of all the speaker name (folder names). e.g. r1, r2, r3
    """
    # spk_info = open(cfg.spk_info_path, 'r') #FIXME: Should we make the same file only for the speaker info?
    folders = os.listdir(cfg.data_path)
    all_audios_name = []
    all_spks_name  = []    
    for folder in folders:
        all_spks_name.append(folder) # adding speaker_id 
        all_audios_name += glob(f'{cfg.data_path}/{folder}/*wav') #FIXME: Do we need to go through every files in the folder instead? A list of all the audio files names
    all_audios_name = list(set([os.path.basename(name).split('.')[0] for name in all_audios_name])) #get the name including speaker_id and speaker_name, exclude .wav, eg. r1_1111anger

    return all_spks_name, all_audios_name

def SplitDataset(all_spks, cfg):
    """
    Split the dataset into train, valid and test set based on the seen/unseen speakers and corresponding audios
    - train_spks: list of train speaker names -> e.g. r1, r22, r13
    - valid_spks: list of speaker names for validation -> e.g. r12, r25
    - test_spks: list of speaker names for test -> e.g. r6, r7, r23,..
    - train_wavs_names: list of audio names for training
    - valid_wavs_names: list of audio names for validation
    - test_wavs_names: list of audio names for testing
    """
    
    all_spks_name = sorted(all_spks)
    random.shuffle(all_spks_name)
    # TODO: DO WE NEED SEPERATE TRAIN, TEST, VALID SPEAKERS? IS THIS WILL RETURN WHAT WE WANT?
    train_spks = all_spks_name[:-cfg.eval_spks * 2] # except valid and test unseen speakers
    valid_spks = all_spks_name[-cfg.eval_spks * 2:-cfg.eval_spks]
    test_spks  = all_spks_name[-cfg.eval_spks:]

    train_wavs_names = []
    valid_wavs_names = []
    test_wavs_names  = []
    
    for spk in train_spks:
        # spk = r1, r22, r13, ...
        spk_wavs         = glob(f'{cfg.data_path}/{spk}/*.wav') # list of files for each speaker: r1_1111anger.wav, r1_1112anger.wav, ... (audios of r1)
        spk_wavs_names = [os.path.basename(path).split('.')[0] for path in spk_wavs] # list of audio names for each speaker: r1_1111anger, r1_1112anger, ...

        valid_names    = random.sample(spk_wavs_names, int(len(spk_wavs_names) * cfg.s2s_portion)) #valid set portion: 0.1
        train_names    = [n for n in spk_wavs_names if n not in valid_names] # train set portion: 0.9
        test_names     = random.sample(train_names, int(len(spk_wavs_names) * cfg.s2s_portion))
        train_names    = [n for n in train_names if n not in test_names] # test set portion: 0.1

        train_wavs_names += train_names
        valid_wavs_names += valid_names
        test_wavs_names  += test_names

    for spk in valid_spks:
        spk_wavs         = glob(f'{cfg.data_path}/{spk}/*.wav') # list of files
        spk_wavs_names   = [os.path.basename(path).split('.')[0] for path in spk_wavs]
        # spk_wavs_names   = spk # only spk name -> r1_1111anger
        valid_wavs_names += spk_wavs_names

    for spk in test_spks:
        spk_wavs        = glob(f'{cfg.data_path}/{spk}/*.wav')
        spk_wavs_names  = [os.path.basename(path).split('.')[0] for path in spk_wavs]
        # # test_wavs_names += spk_wavs_names
        # spk_wavs         = glob(f'{spk}.wav') # spk fullname -> r1_1111anger.wav
        # spk_wavs_names   = spk 
        test_wavs_names += spk_wavs_names
    
    all_wavs         = glob(f'{cfg.data_path}/*/*.wav')
    
    print(f'Total files: {len(all_wavs)}, Train: {len(train_wavs_names)}, Valid: {len(valid_wavs_names)}, Test: {len(test_wavs_names)}, Del Files: {len(all_wavs)-len(train_wavs_names)-len(valid_wavs_names)-len(test_wavs_names)}')
    
    return all_wavs, train_wavs_names, valid_wavs_names, test_wavs_names


#-------------------------------------------------------UNUSED FUNCTIONS-------------------------------------------------------#

# ONLY LOAD AND PROCESS WAV FILE
def LoadWav(path, cfg):
    
    """
        load raw wav from the path -> processed wav 
        (resampled, normalised, trimmed, pitch shifted)
    """
    # skip pre-emphasis
    wav_name = os.path.basename(path).split('.')[0] #this will produce the file name (without .wav)
    sr       = cfg.sampling_rate # ensure sampling rate 16kHz
    wav, fs  = sf.read(path)
    wav, _   = librosa.effects.trim(y=wav, top_db=cfg.top_db) # trim slience

    # normalise and resample

    # pitch shift
    wav = librosa.effects.pitch_shift(wav, sr, n_steps=cfg.pitch_shift) #shift pitch by 2 tones

    # resample
    if fs != sr:
        wav = resampy.resample(x=wav, sr_orig=fs, sr_new=sr, axis=0)
        fs  = sr
        
    assert fs == 16000, 'Downsampling needs to be done.'
    
    # normalise amplitude (loudness) ~ peak
    peak = np.abs(wav).max()
    if peak > cfg.peak_max:
        wav /= peak # divided to normalise
    elif peak < cfg.peak_min:
        wav *= cfg.peak_min / peak

    return wav, wav_name

# ONLY CALCULATE LOG-MEL SPECTROGRAM OF THE WAV FILE
def GetLogMel(wav, cfg):

    """
        load log mel from the wav -> mel, f0, mel length
    """
    mel = logmelspectrogram(
                            x=wav,
                            fs=cfg.sampling_rate,
                            n_mels=cfg.n_mels,
                            n_fft=cfg.n_fft,
                            n_shift=cfg.n_shift,
                            win_length=cfg.win_length,
                            window=cfg.window,
                            fmin=cfg.fmin,
                            fmax=cfg.fmax
                            )
    
    tlen         = mel.shape[0]
    frame_period = cfg.n_shift/cfg.sampling_rate*1000
    
    f0, timeaxis = pw.dio(wav.astype('float64'), cfg.sampling_rate, frame_period=frame_period)
    f0           = pw.stonemask(wav.astype('float64'), f0, timeaxis, cfg.sampling_rate)
    f0           = f0[:tlen].reshape(-1).astype('float32')
    
    nonzeros_indices      = np.nonzero(f0)
    lf0                   = f0.copy()
    lf0[nonzeros_indices] = np.log(f0[nonzeros_indices]) # for f0(Hz), lf0 > 0 when f0 != 0
    
    return mel, lf0, mel.shape[0]

# TODO: CHECK AND REMOVE IF NOT NEEDED
def GetMetaResults(train_results, valid_results, test_results, cfg):
    """
    This is for making additional metadata [txt, text_path, test_type] -1:train, 0:s2s_st, 1:s2s_ut, 2:u2u_st, 3:u2u_ut
    """

    for i in range(len(train_results)):
        
        spk      = train_results[i]['speaker']  # p225
        wav_name = train_results[i]['wav_name'] # p225_001
        txt_path = f'{cfg.txt_path}/{spk}/{wav_name}.txt' 
        
        file    = open(txt_path)
        scripts = file.readline()
        file.close()
       
        train_results[i]['text']      = scripts
        train_results[i]['text_path'] = txt_path
        train_results[i]['test_type'] = 'train'
        
    for i in range(len(valid_results)):
        
        spk      = valid_results[i]['speaker']  # p225
        wav_name = valid_results[i]['wav_name'] # p225_001
        txt_path = f'{cfg.txt_path}/{spk}/{wav_name}.txt' 
        
        file    = open(txt_path)
        scripts = file.readline()
        file.close()
       
        valid_results[i]['text']      = scripts
        valid_results[i]['text_path'] = txt_path
        
    for i in range(len(test_results)):
        
        spk      = test_results[i]['speaker']  # p225
        wav_name = test_results[i]['wav_name'] # p225_001
        txt_path = f'{cfg.txt_path}/{spk}/{wav_name}.txt' 
        
        file    = open(txt_path)
        scripts = file.readline()
        file.close()
       
        test_results[i]['text']      = scripts
        test_results[i]['text_path'] = txt_path

        
    train_spk = set([i['speaker'] for i in train_results])
    valid_spk = set([i['speaker'] for i in valid_results])
    test_spk  = set([i['speaker'] for i in test_results])

    train_txt = set([i['text'] for i in train_results])
    valid_txt = set([i['text'] for i in valid_results])
    test_txt  = set([i['text'] for i in test_results])

    valid_s2s_spk = train_spk.intersection(valid_spk) 
    valid_u2u_spk = valid_spk.difference(train_spk).difference(test_spk)

    test_s2s_spk  = train_spk.intersection(test_spk)
    test_u2u_spk  = test_spk.difference(train_spk).difference(valid_spk)

    valid_s2s_txt = train_txt.intersection(valid_txt) 
    valid_u2u_txt = valid_txt.difference(train_txt).difference(test_txt)

    test_s2s_txt  = train_txt.intersection(test_txt)
    test_u2u_txt  = test_txt.difference(train_txt).difference(valid_txt)
    
    for i in range(len(valid_results)):
        
        spk, txt = valid_results[i]['speaker'], valid_results[i]['text']
        if spk in valid_s2s_spk:
            if txt in valid_s2s_txt:
                valid_results[i]['test_type'] = 's2s_st'
            else:
                valid_results[i]['test_type'] = 's2s_ut'
        else:
            if txt in valid_s2s_txt:
                valid_results[i]['test_type'] = 'u2u_st'
            else:
                valid_results[i]['test_type'] = 'u2u_ut'

    for i in range(len(test_results)):
        
        spk, txt = test_results[i]['speaker'], test_results[i]['text']
        if spk in test_s2s_spk:
            if txt in test_s2s_txt:
                test_results[i]['test_type'] = 's2s_st'
            else:
                test_results[i]['test_type'] = 's2s_ut'
        else:
            if txt in test_s2s_txt:
                test_results[i]['test_type'] = 'u2u_st'
            else:
                test_results[i]['test_type'] = 'u2u_ut'
                
    return train_results, valid_results, test_results

# TODO: CHECK AND REMOVE IF NOT NEEDED
def ExtractMelstats(wn2info, train_wavs_names, cfg):
    
    mels = []
    for wav_name in train_wavs_names:
        mel, *_ = wn2info[wav_name]
        mels.append(mel)   
        
    mels      = np.concatenate(mels, 0)
    mean      = np.mean(mels, 0)
    std       = np.std(mels, 0)
    mel_stats = np.concatenate([mean.reshape(1,-1), std.reshape(1,-1)], 0)    
    print('---Extract Mel statistics and save---')
    np.save(opj(cfg.output_path, 'mel_stats.npy'), mel_stats)
    
    return mean, std

