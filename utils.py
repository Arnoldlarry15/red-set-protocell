import json
import os
from datetime import datetime
from typing import Dict, List, Any

def ensure_directories(directories: List[str]):
    """Ensure all required directories exist"""
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"[UTILS] Created directory: {directory}")

def log_event(event_data: Dict[str, Any], config: Dict):
    """Log event data to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Log to main events file
    events_file = "events.log"
    with open(events_file, "a", encoding='utf-8') as f:
        f.write(f"[{event_data['timestamp']}] " + 
                f"Score: {event_data['score_data']['overall_score']:.2f} | " +
                f"Prompt: {event_data['prompt'][:100]}...\n")
    
    # Save detailed transcript if enabled
    if config['feedback_loop'].get('auto_save_transcripts', True):
        transcript_dir = config['feedback_loop']['transcript_dir']
        transcript_file = os.path.join(transcript_dir, f"transcript_{timestamp}.json")
        
        with open(transcript_file