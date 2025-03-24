"""
Entry point for the ICEx Buddy personal assistant.
"""
import os
import logging
from dotenv import load_dotenv
from core.assistant import PersonalAssistant
from utils.logger import setup_logger

def main():
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting ICEx Buddy")
    
    # Initialize assistant
    assistant = PersonalAssistant()
    if 'assistant' in globals() and assistant:
        assistant.close()
    
    print("Goodbye!")
    sys.exit(0)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='ICEx Buddy Personal Assistant')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--data-dir', type=str, help='Path to data directory')
    parser.add_argument('--log-level', type=str, default='INFO', 
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Logging level')
    parser.add_argument('--backup', action='store_true', help='Create a backup before starting')
    parser.add_argument('--restore', type=str, help='Restore from backup file')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()
    
    # Override environment variables with command line arguments if provided
    if args.data_dir:
        os.environ['DATA_DIR'] = args.data_dir
    
    # Set default data directory if not specified
    if not os.getenv('DATA_DIR'):
        os.environ['DATA_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Load configuration
    config = load_config(args.config)
    
    # Ensure all required directories exist
    ensure_directories(config)
    
    # Setup logging
    setup_logger(args.log_level)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting ICEx Buddy v{config['system']['version']}")
    logger.info(f"Data directory: {os.getenv('DATA_DIR')}")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize assistant
        assistant = PersonalAssistant(config_path=args.config)
        
        # Create backup if requested
        if args.backup:
            backup_path = assistant.create_backup()
            logger.info(f"Backup created at: {backup_path}")
        
        # Restore from backup if requested
        if args.restore:
            assistant.restore_from_backup(args.restore)
            logger.info(f"Restored from backup: {args.restore}")
        
        # Start web interface if requested
        if args.web:
            from ui.web.app import start_web_server
            start_web_server(assistant)
        else:
            # Run interactive mode
            assistant.run_interactive()
    except KeyboardInterrupt:
        logger.info("Shutting down due to user interrupt")
    except Exception as e:
        logger.error(f"Error in main application: {e}", exc_info=True)
    finally:
        # Clean up resources
        try:
            assistant.close()
        except:
            pass
        logger.info("ICEx Buddy shutdown complete")

if __name__ == "__main__":
    main()