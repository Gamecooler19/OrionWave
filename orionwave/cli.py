import argparse
import logging
import sys
from .config import AudioConfig
from .processor import VoiceProcessor

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Real-time voice changer')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--effect', type=str, default='pitch_shift',
                       choices=['pitch_shift', 'robot_effect'],
                       help='Voice effect to apply')
    parser.add_argument('--shift', type=int, default=200,
                       help='Pitch shift amount (for pitch_shift effect)')
    
    args = parser.parse_args()

    try:
        config = AudioConfig.from_yaml(args.config) if args.config else AudioConfig()
        processor = VoiceProcessor(config)
        processor.initialize_streams()

        logger.info(f"Starting voice changer with {args.effect} effect...")
        while True:
            effect_args = {'shift': args.shift} if args.effect == 'pitch_shift' else {}
            processor.process_audio(effect=args.effect, **effect_args)

    except KeyboardInterrupt:
        logger.info("Stopping voice changer...")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        processor.cleanup()

if __name__ == '__main__':
    main()
