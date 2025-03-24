#!/usr/bin/env python3
"""
ICEx Buddy - An intelligent assistant for ICEx

This is the main entry point for the application.
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Core components
from core.assistant import Assistant
from core.config import Config

# Interfaces
from interfaces.cli import CLIInterface
from interfaces.web_ui import WebInterface
from interfaces.api import APIInterface
from interfaces.whatsapp import WhatsAppInterface

# Utilities
from utils.logger import setup_logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ICEx Buddy - An intelligent assistant")
    parser.add_argument("--config", type=str, default="config.yaml", 
                        help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", 
                        help="Enable debug mode")
    parser.add_argument("--interface", type=str, choices=["cli", "web", "api", "whatsapp"],
                        default="cli", help="Interface to start")
    return parser.parse_args()

def main():
    """Main application entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logger("icex_buddy", debug=args.debug)
    logger.info("Starting ICEx Buddy...")
    
    try:
        # Load configuration
        config = Config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
        
        # Initialize assistant
        assistant = Assistant(config)
        logger.info("Assistant initialized")
        
        # Start the requested interface
        if args.interface == "cli":
            interface = CLIInterface(assistant, config)
        elif args.interface == "web":
            interface = WebInterface(assistant, config)
        elif args.interface == "api":
            interface = APIInterface(assistant, config)
        elif args.interface == "whatsapp":
            interface = WhatsAppInterface(assistant, config)
            
        logger.info(f"Starting {args.interface} interface")
        interface.start()
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()