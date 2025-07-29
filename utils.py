def log_event(event):
    with open("events.log", "a") as f:
        f.write(event + "\n")

# === config.yaml ===
# Place this in the root directory as config.yaml
# Example:
# model: chatgpt-3.5
# api_key: sk-XXXXXX
# threshold: 0.5
