# Using TRIAAN-VC

## Installation

- python version: 3.8.10
- pip version: 21.1.1

- install the required packages
  `pip install -r requirements.txt`

- **Note:** It is recommended to create a virtual environment (namely `vcrs-venv`) for the project, since the pip version and compatible version of every package is not the latest, so it might cause some issues during the installation.

## Steps

- Clone the repository from TRIAAN-VC original source: https://github.com/winddori2002/TriAAN-VC, stored in models folder.
  The expected path is `./models/TriAAN-VC`

- Running the `convert.py` file, with some specified arguments, the output is expected to be a converted file

- Specify the source and target directories in the `base_data` file.
- Changing the configuration in `config\base.yaml` for targetting source and target input

### Input - for `convert.py`

- `--config` : direct of configuration file (default: `./ORIGINAL_TRIAAN_PATH/config/base.yaml`)
- `--device` : device to run the conversion on (default: `cuda:0`)
- `--sample_path`: path to the sample data (default: `./ORIGINAL_TRIAAN_PATH/samples`)
- `--src_name`: name of the source data (default: `src.flac`)
- `--checkpoints`: path to the checkpoints (default: `./ORIGINAL_TRIAAN_PATH/checkpoints`)
- `--model_name`: name of the model, injecting with the custom path (default: `model-cpc-split.pth`)

---

### Running the original conversion model

```python
# Running test conversion example
!python convert.py --device cpu --sample_path ../../data --src_name [source_file_name] --trg_name [target_file_name] --checkpoint ./checkpoints
```

### Output

- Test with sample voice - src: `conversion_test_source.wav`, trg: `conversion_test_target.wav`
- Test with non-verbal (laughing) voice - src: `montreal6happy.wav`, trg: `ken8happy.wav`
- Test with robot voice (surprise) - src: `emogib28surprise.wav`, trg: `best1137surpise.wav` -> Didn't work that well
- Test from non-verbal robot voice to non-verbal human voice with - src: `best1214fear.wav`, trg: `montreal6fear.wav` -> Didn't work that well but the reverse worked quite well

> We can customise the robot voice by converting from human voice, but currently, it only work with non-verbal voice, and emotional expression.

### Observations
