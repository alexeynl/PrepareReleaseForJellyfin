import logging
import argparse

from utils.release import Release

def main():
    logger = logging.getLogger(__name__)
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel("DEBUG")

    default_media_extensions = [".mkv"]
    default_audio_track_extensions = [".mka"]
    default_subtitle_track_extensions = [".ass", "srt"]

    media_extensions = default_media_extensions
    audio_track_extensions = default_audio_track_extensions
    subtitle_track_extensions = default_subtitle_track_extensions

    parser = argparse.ArgumentParser(description="Prepare you downloaded media release for Jellyfin processing")
    parser.add_argument("-p", "--path", help="Path to release")
    parser.add_argument("-c", "--config", help="Path to config file")
    parser.add_argument("-e", "--media-extensions" , nargs='+', help="Extenstions of media files to search for. Deafults to .mkv")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug level events")
    args = parser.parse_args()

    if args.media_extensions:
        media_extensions = args.media_extensions
    
    if args.verbose:    
        logging.getLogger("utils.release").setLevel(logging.DEBUG)

    if args.path:
        logger.debug("Release path will be processed: {}".format(args.path))
        release = Release(args.path, media_extensions, audio_track_extensions, subtitle_track_extensions)
        release._create_sym_links()

if __name__ == "__main__":
    main()