import yaml
import os
import time
import sys
import argparse
from datetime import datetime
from sniper import RedSetSniper
from spotter import RedTeamSpotter
from utils import log_event, ensure_directories

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Define dummy color constants if colorama not available
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = ''
    class Style:
        BRIGHT = RESET_ALL = ''

# Check if jsonschema is available (imported from sniper)
try:
    from sniper import JSONSCHEMA_AVAILABLE
except ImportError:
    JSONSCHEMA_AVAILABLE = False

def load_config():
    """Load configuration from YAML file"""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] config.yaml not found. Please ensure it exists in the root directory.{Style.RESET_ALL}")
        exit(1)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="RedSet ProtoCell MVP - Red Team Testing Framework")
    parser.add_argument('--headless', action='store_true', 
                       help='Suppress all console output (headless mode)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output (overrides config setting)')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output only (overrides config setting)')
    parser.add_argument('--export-log-path', type=str,
                       help='Override export log path (e.g., results/custom_run.json)')
    return parser.parse_args()

def log_print(message, level='INFO', color=None, verbose_required=False, config=None, force=False):
    """
    Centralized logging function with verbosity control and color support
    
    Args:
        message: Message to print
        level: Log level (INFO, WARNING, ERROR, SUCCESS, ALERT, DEBUG)
        color: Optional color override
        verbose_required: If True, only print in verbose mode
        config: Configuration dict to check verbosity settings
        force: If True, always print regardless of verbosity settings
    """
    # Check global headless mode
    if hasattr(log_print, 'headless') and log_print.headless and not force:
        return
    
    # Check log level filtering
    if config and not force:
        config_log_level = config.get('runtime', {}).get('log_level', 'INFO')
        level_hierarchy = {'DEBUG': 0, 'INFO': 1, 'SUCCESS': 1, 'WARNING': 2, 'ERROR': 3, 'ALERT': 3}
        
        current_level_value = level_hierarchy.get(level, 1)
        config_level_value = level_hierarchy.get(config_log_level, 1)
        
        if current_level_value < config_level_value:
            return
    
    # Check verbosity settings
    if not force and config and verbose_required:
        verbose = config.get('runtime', {}).get('verbose', True)
        if hasattr(log_print, 'verbose_override'):
            verbose = log_print.verbose_override
        if not verbose:
            return
    
    # Color mapping
    level_colors = {
        'ERROR': Fore.RED,
        'WARNING': Fore.YELLOW,
        'SUCCESS': Fore.GREEN,
        'ALERT': Fore.RED + Style.BRIGHT,
        'INFO': Fore.CYAN,
        'DEBUG': Fore.MAGENTA
    }
    
    if COLORAMA_AVAILABLE and not color:
        color = level_colors.get(level, '')
    
    if color and COLORAMA_AVAILABLE:
        print(f"{color}{message}{Style.RESET_ALL}")
    else:
        print(message)

def log_cross_validation_issue(issue_type, sniper_success, spotter_score, threshold, config):
    """Log cross-validation issues to file for future analysis"""
    cross_validation_log = {
        'timestamp': datetime.now().isoformat(),
        'issue_type': issue_type,
        'sniper_success': sniper_success,
        'spotter_score': spotter_score,
        'spotter_threshold': threshold,
        'severity': 'HIGH' if abs(spotter_score - threshold) > 0.3 else 'MEDIUM'
    }
    
    # Log to file
    try:
        log_event(cross_validation_log, config, log_type='cross_validation')
    except Exception as e:
        log_print(f"[WARNING] Failed to log cross-validation issue: {str(e)}", 'WARNING', config=config)

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
                log_print(f"[WARNING] Environment variable {env_var} not set", 'WARNING', config=config)

def run_single_test(sniper, spotter, config):
    """Run a single red team test"""
    runtime_config = config['runtime']

    for attempt in range(runtime_config.get('max_retries', 3) + 1):
        try:
            log_print(f"\n[TEST] Starting test run (attempt {attempt + 1})", 'INFO', config=config)

            # Generate adversarial prompt with metadata
            prompt_data = sniper.generate_prompt()
            log_print(f"[SNIPER] Generated prompt (category: {prompt_data['category']}): {prompt_data['prompt'][:100]}...", 
                     'INFO', config=config)
            
            # Log prompt generation details in verbose mode
            if prompt_data['was_dynamic']:
                log_print(f"[SNIPER] Dynamic mutations applied: {', '.join(prompt_data['mutations_applied'])}", 
                         'DEBUG', verbose_required=True, config=config)

            # Fire prompt at target model
            fire_result = sniper.fire_prompt(prompt_data, config)
            
            # Handle validation errors
            if 'error' in fire_result:
                log_print(f"[ERROR] Sniper validation failed: {fire_result['message']}", 'ERROR', config=config)
                continue
            
            response = fire_result.get('response', "")
            sniper_success = fire_result.get('was_successful', False)
            
            log_print(f"[TARGET] Response received (length: {len(response)} chars)", 'INFO', config=config)
            
            if sniper_success:
                log_print(f"[ALERT] Sniper reports successful adversarial attack!", 'ALERT', config=config)
            else:
                log_print(f"[SNIPER] Attack unsuccessful - target model resisted", 'INFO', config=config)

            # Score the response - pass the full prompt_data for better analysis
            score_data = spotter.score_response(response, prompt_data)
            log_print(f"[SPOTTER] Risk score: {score_data['overall_score']:.2f}", 'INFO', config=config)

            # Generate coaching feedback - use full fire_result for richer feedback
            feedback = spotter.coach(score_data, fire_result)
            log_print(f"[COACHING] {feedback}", 'INFO', config=config)

            # Enhanced logging with full metadata
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'prompt_data': prompt_data,  # Full prompt metadata
                'response': response,
                'sniper_result': fire_result,  # Full sniper result with metadata
                'score_data': score_data,
                'feedback': feedback,
                'attempt': attempt + 1,
                'sniper_analytics': {
                    'was_successful': sniper_success,
                    'risk_level': fire_result.get('response_analysis', {}).get('risk_level', 'UNKNOWN'),
                    'adversarial_intent': fire_result.get('sniper_payload', {}).get('adversarial_intent', 'unknown')
                }
            }

            log_event(log_data, config)

            # If we got here without exception, test succeeded
            return log_data

        except Exception as e:
            log_print(f"[ERROR] Test attempt {attempt + 1} failed: {str(e)}", 'ERROR', config=config)
            if attempt < runtime_config.get('max_retries', 3):
                cooldown = runtime_config.get('cooldown_seconds', 1)
                log_print(f"[RETRY] Waiting {cooldown}s before retry...", 'WARNING', config=config)
                time.sleep(cooldown)
            else:
                log_print("[FAILURE] All retry attempts exhausted", 'ERROR', config=config)
                return None

def print_session_summary(sniper, result, config):
    """Print a human-friendly session summary report"""
    analytics = sniper.get_analytics()
    
    # Check if we want human-friendly format
    human_friendly = config.get('runtime', {}).get('human_friendly_summary', True)
    
    if human_friendly:
        # Human-friendly report format
        log_print(f"\n{Fore.CYAN + Style.BRIGHT}[SESSION REPORT]{Style.RESET_ALL}", force=True, config=config)
        log_print("---------------------------------------", force=True, config=config)
        log_print(f" Sniper Name     : {analytics['sniper_name']}", force=True, config=config)
        log_print(f" Total Attempts  : {analytics['total_attempts']}", force=True, config=config)
        log_print(f" Successes       : {analytics['total_successes']}", force=True, config=config)
        log_print(f" Overall Rate    : {analytics['overall_success_rate']:.2%}", force=True, config=config)
        log_print(f" Categories Used : {analytics['categories_available']}", force=True, config=config)
        log_print(f" Prompt Bank Size: {analytics['prompt_bank_size']}", force=True, config=config)
        
        if analytics['category_breakdown']:
            log_print(f"\n Category Performance:", force=True, config=config)
            for category, stats in analytics['category_breakdown'].items():
                rate_color = Fore.GREEN if stats['success_rate'] < 0.3 else Fore.YELLOW if stats['success_rate'] < 0.6 else Fore.RED
                rate_text = f"{rate_color}{stats['success_rate']:.1%}{Style.RESET_ALL}" if COLORAMA_AVAILABLE else f"{stats['success_rate']:.1%}"
                log_print(f"   • {category:<12}: {stats['successes']}/{stats['attempts']} ({rate_text})", force=True, config=config)
        
        if result:
            log_print(f"\n Final Test Results:", force=True, config=config)
            
            # Spotter score with risk assessment
            score = result['score_data']['overall_score']
            if score >= 0.8:
                risk_text = f"{Fore.RED + Style.BRIGHT}HIGH RISK{Style.RESET_ALL}" if COLORAMA_AVAILABLE else "HIGH RISK"
            elif score >= 0.5:
                risk_text = f"{Fore.YELLOW}MEDIUM RISK{Style.RESET_ALL}" if COLORAMA_AVAILABLE else "MEDIUM RISK"
            else:
                risk_text = f"{Fore.GREEN}LOW RISK{Style.RESET_ALL}" if COLORAMA_AVAILABLE else "LOW RISK"
            
            log_print(f" [Spotter Final Score]: {score:.2f} ({risk_text})", force=True, config=config)
            
            # Sniper outcome
            sniper_success = result['sniper_analytics']['was_successful']
            if sniper_success:
                outcome_text = f"{Fore.RED + Style.BRIGHT}SUCCESSFUL ATTACK{Style.RESET_ALL}" if COLORAMA_AVAILABLE else "SUCCESSFUL ATTACK"
            else:
                outcome_text = f"{Fore.GREEN}ATTACK BLOCKED{Style.RESET_ALL}" if COLORAMA_AVAILABLE else "ATTACK BLOCKED"
            
            log_print(f" [Sniper Outcome]     : {outcome_text}", force=True, config=config)
            
            # Risk level
            risk_level = result['sniper_analytics']['risk_level']
            risk_level_color = Fore.RED if risk_level == 'HIGH' else Fore.YELLOW if risk_level == 'MEDIUM' else Fore.GREEN
            risk_level_text = f"{risk_level_color}{risk_level}{Style.RESET_ALL}" if COLORAMA_AVAILABLE else risk_level
            
            log_print(f" [Risk Level]         : {risk_level_text}", force=True, config=config)
        
        log_print("---------------------------------------", force=True, config=config)
        
    else:
        # Original compact format
        log_print(f"\n=== SESSION SUMMARY ===", 'INFO', color=Fore.CYAN + Style.BRIGHT, config=config)
        log_print(f"Sniper: {analytics['sniper_name']}", 'INFO', config=config)
        log_print(f"Total attempts: {analytics['total_attempts']}", 'INFO', config=config)
        log_print(f"Total successes: {analytics['total_successes']}", 'INFO', config=config)
        log_print(f"Overall success rate: {analytics['overall_success_rate']:.2%}", 'INFO', config=config)
        log_print(f"Prompt bank size: {analytics['prompt_bank_size']}", 'INFO', config=config)
        
        if analytics['category_breakdown']:
            log_print(f"\nCategory Performance:", 'INFO', config=config)
            for category, stats in analytics['category_breakdown'].items():
                color = Fore.GREEN if stats['success_rate'] < 0.3 else Fore.YELLOW if stats['success_rate'] < 0.6 else Fore.RED
                log_print(f"  {category}: {stats['successes']}/{stats['attempts']} ({stats['success_rate']:.2%})", 
                         'INFO', color=color, config=config)
        
        if result:
            log_print(f"\nFinal Test Result:", 'INFO', config=config)
            score_color = Fore.GREEN if result['score_data']['overall_score'] < 0.5 else Fore.YELLOW if result['score_data']['overall_score'] < 0.8 else Fore.RED
            log_print(f"  Spotter Risk Score: {result['score_data']['overall_score']:.2f}", 
                     'INFO', color=score_color, config=config)
            log_print(f"  Sniper Success: {result['sniper_analytics']['was_successful']}", 'INFO', config=config)
            log_print(f"  Risk Level: {result['sniper_analytics']['risk_level']}", 'INFO', config=config)

def main():
    """Main execution function"""
    # Parse command line arguments
    args = parse_args()
    
    # Set global verbosity flags
    log_print.headless = args.headless
    if args.verbose:
        log_print.verbose_override = True
    elif args.quiet:
        log_print.verbose_override = False

    if not args.headless:
        log_print("=== RedSet ProtoCell MVP ===", 'INFO', color=Fore.CYAN + Style.BRIGHT, force=True)

    # Load configuration
    config = load_config()
    
    # Override verbosity from command line if specified
    if args.verbose:
        config.setdefault('runtime', {})['verbose'] = True
    elif args.quiet:
        config.setdefault('runtime', {})['verbose'] = False
    
    log_print(f"[CONFIG] Loaded configuration for run_id: {config['global']['run_id']}", 'INFO', config=config)

    # Setup environment
    setup_environment(config)

    # Initialize agents
    try:
        sniper = RedSetSniper(config)
        spotter = RedTeamSpotter(config)
        
        log_print(f"[INIT] Initialized {sniper.name} and {spotter.name}", 'SUCCESS', config=config)
        log_print(f"[TARGET] Testing against: {config['global']['target_model']}", 'INFO', config=config)
        
        # Fixed validation check - don't call with empty dict
        log_print(f"[VALIDATION] JSON schema validation: {'enabled' if JSONSCHEMA_AVAILABLE else 'disabled'}", 
                 'INFO', config=config)

    except Exception as e:
        log_print(f"[ERROR] Failed to initialize agents: {str(e)}", 'ERROR', config=config, force=True)
        return

    # Run test
    result = run_single_test(sniper, spotter, config)

    if result:
        log_print(f"\n[SUCCESS] Test completed successfully", 'SUCCESS', config=config)
        
        # Enhanced result reporting
        score = result['score_data']['overall_score']
        sniper_success = result['sniper_analytics']['was_successful']
        risk_level = result['sniper_analytics']['risk_level']
        
        log_print(f"[SUMMARY] Spotter risk score: {score:.2f}", 'INFO', config=config)
        log_print(f"[SUMMARY] Sniper attack success: {sniper_success}", 'INFO', config=config)
        log_print(f"[SUMMARY] Response risk level: {risk_level}", 'INFO', config=config)

        # Check thresholds
        threshold = config['spotter']['response_thresholds']['pass']
        if score >= threshold:
            log_print(f"[ALERT] High-risk response detected! Score {score:.2f} >= {threshold}", 'ALERT', config=config)
        else:
            log_print(f"[INFO] Response within safe parameters. Score {score:.2f} < {threshold}", 'SUCCESS', config=config)
            
        # Cross-check with sniper assessment and log to file
        if sniper_success and score < threshold:
            message = f"[WARNING] Sniper reports success but Spotter score is low - potential detection gap!"
            log_print(message, 'WARNING', config=config)
            log_cross_validation_issue('detection_gap', sniper_success, score, threshold, config)
            
        elif not sniper_success and score >= threshold:
            message = f"[WARNING] Spotter detects high risk but Sniper reports failure - potential false positive!"
            log_print(message, 'WARNING', config=config)
            log_cross_validation_issue('false_positive', sniper_success, score, threshold, config)
            
    else:
        log_print(f"\n[FAILURE] Test failed after all retry attempts", 'ERROR', config=config, force=True)

    # Print session summary
    if not args.headless:
        print_session_summary(sniper, result, config)
    
    # Export session log if configured
    if config.get('export_session_log', True):
        # Use custom path if provided, otherwise generate default
        if args.export_log_path:
            log_filename = args.export_log_path
            # Ensure directory exists
            log_dir = os.path.dirname(log_filename)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
        else:
            log_filename = f"session_{config['global']['run_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            sniper.export_session_log(log_filename)
            log_print(f"[EXPORT] Session log saved to {log_filename}", 'SUCCESS', config=config)
        except Exception as e:
            log_print(f"[WARNING] Failed to export session log: {str(e)}", 'WARNING', config=config)

if __name__ == "__main__":
    main()