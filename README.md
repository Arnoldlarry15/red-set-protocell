# Red Set ProtoCell

Red Set ProtoCell is an open-source AI red teaming system built as a sniper/spotter two-agent cell.

## Features
- Adversarial prompt generation (Sniper)
- Real-time response monitoring and scoring (Spotter)
- CLI-based and modular

## Setup
```bash
pip install pyyaml
python main.py
```

## Config
Update `config.yaml` with your model and preferences:
```yaml
model: chatgpt-3.5
api_key: your-api-key-here
threshold: 0.5
```

## License
MIT License
