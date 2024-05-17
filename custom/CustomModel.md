## Input

### Data directory structure

Restructure the folder directory and file structure, by running the file `processing/process_file_structure.py` to restructure the input to several folders: _r1, r2,..._

**Original data**

```python
    data_path /
        ├── input /
        │   ├── r1 /
        │   │   ├── audio1.wav
        │   │   ├── audio2.wav
        │   │   └── ...
        │   ├── r2 /
        │   │   ├── audio1.wav
        │   │   ├── audio2.wav
        │   │   └── ...
        │   └── ...
```

**Splitted data for training**

```python
    data_path /
        ├── train /
        │   ├── r1 /
        │   │   ├── audio1.wav
        │   │   ├── audio2.wav
        │   │   └── ...
        │   ├── r2 /
        │   │   ├── audio1.wav
        │   │   ├── audio2.wav
        │   │   └── ...
        │   └── ...
        ├── val /
        │   ├── r1 /
        │   │   ├── audio1.wav
        │   │   ├── audio2.wav
        │   │   └── ...
        │   ├── r2 /
        │   │   ├── audio1.wav
        │   │   ├── audio2.wav
        │   │   └── ...
        │   └── ...
        └── test /
            ├── audio1.wav
            ├── audio2.wav
            └── ...
```

### Preprocessing - Audio Configuration

- Sample rate: 16kHz
- Normalise audio: pitch, volume, tempo (optional?)
- ***

### Preprocessing - Train test split

- Modified the configuration in file: `modified_audio_process.py`
- All audios are split into 3 sets: train, val, test based on the 24 speakers and audios
- Train: 80%, Val: 10% and Test: 10%

## Models

### Configuration The model parameters and architecture:

-Configuration file: `modelconfiguration.yaml`

### Custom Preprocessing

- File used: `custom_preprocessing.py`

### Custom Train, Test

- File used: `custom_main.py`

### Custom Convert model

- File used: `custom_convert.py`
