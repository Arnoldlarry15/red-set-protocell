import yaml
import os
import time
from datetime import datetime
from sniper import RedSetSniper
from spotter import RedSetSpotter
from utils import log_event, ensure_directories

def load_config():
    """Load configuration from YAML file"""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("[ERROR] config.yaml not found. Please ensure it exists in the root directory.")
        exit(1)

def setup_environment(config):
    """Setup directories and environment"""
    ensure_directories([
        config['spotter']['logs'],
        config['feedback_loop']['transcript_dir'],
        config['sniper']['prompt_bank']
    ])
    
    # Set API keys from environment if using placeholders
    for service, key in config['api_keys'].items():
        if key.startswith('${') and key.endswith('}'):
            env_var = key[2:-1]  # Remove ${ and }
            actual_key = os.getenv(env_var)
            if actual_key:
                config['api_keys'][service] = actual_key
            else:
                print(f"[WARNING] Environment variable {env_var} not set")

def run_single_test(sniper, spotter, config):
    """Run a single red team test"""
    runtime_config = config['runtime']
    
    for attempt in range(runtime_config.get('max_retries', 3) + 1):
        try:
            print(f"\n[TEST] Starting test run (attempt {attempt + 1})")
            
            # Generate adversarial prompt
            prompt = sniper.generate_prompt()
            print(f"[SNIPER] Generated prompt: {prompt[:100]}...")
            
            # Fire prompt at target model
            response = sniper.fire_prompt(prompt, config)
            print(f"[TARGET] Response received (length: {len(response)} chars)")
            
            # Score the response
            score_data = spotter.score_response(response, prompt)
            print(f"[SPOTTER] Risk score: {score_data['overall_score']:.2f}")
            
            # Generate coaching feedback
            feedback = spotter.coach(score_data, prompt)
            print(f"[COACHING] {feedback}")
            
            # Log everything
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'response': response,
                'score_data': score_data,
                'feedback': feedback,
                'attempt': attempt + 1
            }
            
            log_event(log_data, config)
            
            # If we got here without exception, test succeeded
            return log_data
            
        except Exception as e:
            print(f"[ERROR] Test attempt {attempt + 1} failed: {str(e)}")
            if attempt < runtime_config.get('max_retries', 3):
                cooldown = runtime_config.get('cooldown_seconds', 1)
                print(f"[RETRY] Waiting {cooldown}s before retry...")
                time.sleep(cooldown)
            else:
                print("[FAILURE] All retry attempts exhausted")
                return None

def main():
    """Main execution function"""
    print("=== RedSet ProtoCell MVP ===")
    
    # Load configuration
    config = load_config()
    print(f"[CONFIG] Loaded configuration for run_id: {config['global']['run_id']}")
    
    # Setup environment
    setup_environment(config)
    
    # Initialize agents
    sniper = RedSetSniper(config)
    spotter = RedSetSpotter(config)
    
    print(f"[INIT] Initialized {sniper.name} and {spotter.name}")
    print(f"[TARGET] Testing against: {config['global']['target_model']}")
    
    # Run test
    result = run_single_test(sniper, spotter, config)
    
    if result:
        print(f"\n[SUCCESS] Test completed successfully")
        print(f"[SUMMARY] Overall risk score: {result['score_data']['overall_score']:.2f}")
        
        # Check if this was a successful adversarial attack
        threshold = config['spotter']['response_thresholds']['pass']
        if result['score_data']['overall_score'] >= threshold:
            print(f"[ALERT] High-risk response detected! Score {result['score_data']['overall_score']:.2f} >= {threshold}")
        else:
            print(f"[INFO] Response within safe parameters. Score {result['score_data']['overall_score']:.2f} < {threshold}")
    else:
        print(f"\n[FAILURE] Test failed after all retry attempts")

if __name__ == "__main__":
    main()