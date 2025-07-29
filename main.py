import yaml
from sniper import generate_prompt, fire_prompt
from spotter import score_response, coach
from utils import log_event

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    model = config.get("model", "chatgpt-3.5")
    threshold = config.get("threshold", 0.5)

    prompt = generate_prompt()
    response = fire_prompt(prompt, model)
    score = score_response(response)
    feedback = coach(score)

    print(response)
    print(f"[SCORE] {score:.2f}")
    print(f"[COACHING] {feedback}")

    log_event(f"Prompt: {prompt}\nResponse: {response}\nScore: {score}\n")

if __name__ == "__main__":
    main()

