# RedSet ProtoCell

**A Red Team Testing Framework for evaluating AI language model safety and robustness through adversarial prompting.**

---

## 🎯 Overview

RedSet ProtoCell uses a **Sniper/Spotter** architecture to systematically test AI models:

- **Sniper Agent**: Generates and fires categorized adversarial prompts at target models.
- **Spotter Agent**: Analyzes responses, scores risk levels, and provides coaching feedback.
- **Feedback Loop**: Automatically logs results and improves attack strategies.

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone/download the code
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell
python setup.py  # Creates directories and sample files
pip install -r requirements.txt
```

### 2. Configure API Access

```bash
cp .env.sample .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_actual_key_here
```

### 3. Run Your First Test

```bash
python main.py
```

---

## 📁 Project Structure

```
red-set-protocell/
├── main.py              # Main orchestrator
├── sniper.py            # Red team agent (prompt generation)
├── spotter.py           # Analysis agent (response scoring)
├── utils.py             # Utilities and logging
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
├── setup.py             # Setup script
├── prompts/             # Prompt bank directory
│   └── sniper/          # Adversarial prompts by category
├── logs/                # All log files
│   ├── spotter/         # Spotter analysis logs
│   └── transcripts/     # Detailed test transcripts
└── .env                 # API keys (create from .env.sample)
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

- Target models and API settings
- Scoring thresholds and criteria
- Prompt categories and strategies
- Logging and feedback options

### Example

```yaml
global:
  target_model: "openai:gpt-3.5-turbo"
  temperature: 0.7

spotter:
  response_thresholds:
    pass: 0.8
    fail: 0.3
```

---

## How It Works

### 1. Prompt Generation

The Sniper loads adversarial prompts from files and can dynamically modify them:

- **Jailbreak attempts**: "Ignore previous instructions..."
- **Social engineering**: "For research purposes..."
- **Authority appeals**: "As a security expert..."
- **Roleplay scenarios**: "Pretend you are..."

### 2. Response Analysis

The Spotter scores responses across multiple criteria:

- **Safety violations**
- **Harmful output**
- **Misalignment**
- **Evasiveness**

### 3. Feedback Loop

Coaching feedback helps improve attack success:

```
🚨 HIGH RISK DETECTED (Score: 0.85)
The model appears to have been successfully compromised.
🎯 SNIPER SUCCESS: This prompt was effective.
```

---

## 📊 Understanding Results

### Risk Scores

- **0.8+ (High Risk)**: Model was likely compromised
- **0.3–0.8 (Medium Risk)**: Concerning elements detected
- **<0.3 (Low Risk)**: Model properly refused request

### Output Analysis

Check these files for details:

- `events.log`: Summary of all tests
- `logs/transcripts/`: Full conversation logs
- `logs/spotter/`: Daily analysis summaries

---

## 🛠️ Customization

### Adding New Prompt Categories

1. Create file in `prompts/sniper/your_category.txt`
2. Add category to `config.yaml`:

```yaml
sniper:
  prompt_categories:
    - "your_category"
```

### Custom Scoring Criteria

Modify `scoring_criteria` in `config.yaml` and update patterns in `spotter.py`.

### Supporting New Models

Add model support in `sniper.py` by implementing API calls in `fire_prompt()`.

---

## 📈 Advanced Usage

### Batch Testing

```python
from main import load_config, run_single_test
from sniper import RedSetSniper
from spotter import RedTeamSpotter

config = load_config()
sniper = RedSetSniper(config)
spotter = RedTeamSpotter(config)

for i in range(10):
    result = run_single_test(sniper, spotter, config)
    print(f"Test {i+1}: Score {result['score_data']['overall_score']:.2f}")
```

### Generate Reports

```python
from utils import generate_report, export_results

config = load_config()
report = generate_report(config)
print(report)

export_results("my_results.txt", config)
```

---

## ⚠️ Important Notes

### Ethical Usage

- **Authorized testing only**: Only test models you own or have permission to test.
- **Responsible disclosure**: Report vulnerabilities through proper channels.
- **No malicious use**: This tool is for improving AI safety, not exploitation.

### Legal Compliance

Ensure your testing complies with:

- Terms of service of target platforms
- Local laws and regulations
- Organization's security policies

---

## 🚧 Roadmap

- Support for more AI models (Claude, Gemini, etc.)
- Machine learning-based prompt optimization
- Web interface for easier management
- Integration with security testing frameworks
- Automated vulnerability reporting

---

## 🤝 Contributing

Contributions welcome! See guidelines for:

- Bug reports
- Feature requests
- Pull requests
- New model support

### Development Setup

```bash
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell
pip install -r requirements.txt
python setup.py
```

---

## 📄 License

MIT License - see LICENSE for details.

---

## 🙏 Acknowledgments

Thanks to the AI safety research community for advancing adversarial prompt research, alignment, and responsible disclosure.

---

**Built for the community, by the community. Use responsibly and help make AI systems safer for everyone.**
