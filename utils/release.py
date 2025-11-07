import glob, os
from pathlib import Path
from itertools import chain
import logging

logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel("INFO")

class ExternalTrack:
    def __init__(self, media):
        self.parent_media = Media(media.ParentRelease, media.FilePath)
        self.parent_media = media
        self._file_path = None
        self.Type = None #audio, subs
        self.related_depth = None
        #self.parent_media = None
        self.FileName = None
    @property
    def FilePath(self):
        return self._file_path
    @FilePath.setter
    def FilePath(self, value):
        self._file_path = value
        self.FileName = os.path.basename(self._file_path)
    def _get_label(self):
        media_path = Path(self.parent_media.FilePath)
        track_path = Path(self.FilePath)
        if track_path.parents[0].is_relative_to(media_path.parents[0]):
            track_relative_path = track_path.parents[0].relative_to(media_path.parents[0])
            if len(track_relative_path.parts) == 2:
                if track_relative_path.parts[0].endswith("Subs"):
                    track_label = track_relative_path.parts[1]
                if track_relative_path.parts[0].endswith("Sound"):
                    track_label =  track_relative_path.parts[1]
        return track_label
    def _extract_labels(self, extract_existing = False):
        media_path = Path(self.parent_media.FilePath)
        track_path = Path(self.FilePath)
        track_labels_list = []
        # default straight way to extract: result label is concatenation of track subfolders names and add sequence number
        if track_path.parents[0].is_relative_to(media_path.parents[0]):
            track_relative_path = track_path.parents[0].relative_to(media_path.parents[0])
            logger.debug("track_relative_path = {}".format(track_relative_path))
            if len(track_relative_path.parts) > 0:
                subfolder_names_delimeter = " - "
                track_labels_list.append(subfolder_names_delimeter.join(track_relative_path.parts))
        return track_labels_list

    def _get_language(self):
        media_path = Path(self.parent_media.FilePath)
        track_path = Path(self.FilePath)
        if track_path.parents[0].is_relative_to(media_path.parents[0]):
            track_relative_path = track_path.parents[0].relative_to(media_path.parents[0])
            if len(track_relative_path.parts) == 2:
                if track_relative_path.parts[0].endswith("Subs"):
                    track_language = track_relative_path.parts[0].rstrip("Subs")
                if track_relative_path.parts[0].endswith("Sound"):
                    track_language =  track_relative_path.parts[0].rstrip("Sound")
        return str(track_language).strip().lower()

class ExternalTracks:
    def __init__(self, media):
        self.ParentMedia = media
        self._items = []
        self.Count = 0
    def Items(self) -> list[ExternalTrack]:
        return self._items
    def Add(self, track: ExternalTrack):
        self._items.append(track)
    def _getlabel(self):
        self.ParentMedia

class Media:
  def __init__(self, release, file_path):
    self.FilePath = file_path
    self.AudioTracks = ExternalTracks(self)
    self.SubtitleTracks = ExternalTracks(self)
    self.ParentRelease = release
    self.Name = Path(self.FilePath).stem
    self.FileName = os.path.basename(self.FilePath)
    self.DirPath = os.path.dirname(self.FilePath)

class Medias:
  def __init__(self):
    self.Count = 0
    self._items = []
  def Items(self) -> list[Media]:
    return self._items
  def Add(self, media: Media):
    self._items.append(media)

class Release:
    def __init__(self, path, media_extensions, audio_track_extensions, subtitle_track_extensions):
        self._medias = Medias()
        self._media_paths = []
        self.MediaExtensions = media_extensions
        self.AudioTrackExtenstions = audio_track_extensions
        self.SubtitleTrackExtensions = subtitle_track_extensions
        self.Path = path
        self._file_paths = None
        self._scan_for_files()
        self._scan_for_media()

    def _scan_for_files(self):
        logger.debug("Start to scan release path {} for files".format(self.Path))
        self._file_paths = glob.glob(glob.escape(self.Path) + '/**/*', recursive=True)
        logger.debug("Scan finished. Found {} files. List: {}".format(len(self._file_paths), ";".join(self._file_paths)))

    def _scan_for_media(self):

        logger.debug("Start to scan path {} for media with extensions {}".format(self.Path, ",".join(self.MediaExtensions)))
        for extenstion in self.MediaExtensions:
            self._media_paths = self._media_paths + list (filter(lambda x:x.endswith(extenstion), self._file_paths))

        logger.debug("List of medias found: {}".format(";".join(self._media_paths)))

        for media_path in self._media_paths:
           media = Media(self, media_path)
           self._medias.Add(media)
           self._scan_for_tracks(media)
        pass

    def _scan_for_tracks(self, media: Media):

        logger.debug("Start to search fo related files. Media name: {}".format(media.Name))
        related_files = list(filter(lambda x:Path(x).stem.startswith(media.Name), self._file_paths))
        logger.debug("Found files related to media: {}".format(";".join(related_files)))

        audio_track_paths = list(filter(lambda x:Path(x).suffix in self.AudioTrackExtenstions, related_files))

        for audio_track_path in audio_track_paths:
            logger.debug("Creating new audio track object: {}".format(audio_track_path))
            audio_track = ExternalTrack(media)
            audio_track.FilePath = audio_track_path
            media.AudioTracks.Add(audio_track)

        subtitle_track_paths = list (filter(lambda x:Path(x).suffix in self.SubtitleTrackExtensions, related_files))
        for subtitle_track_path in subtitle_track_paths:
            logger.debug("Creating new subtitle tracks object for path: {}".format(subtitle_track_path))
            subtitle_track = ExternalTrack(media)
            subtitle_track.FilePath = subtitle_track_path
            media.SubtitleTracks.Add(subtitle_track)
        pass

    #create sym links for each media to external audio and subtitles track in the media directory
    def _create_sym_links(self):
        for media in self.Medias.Items():
            for index, track in chain(enumerate(media.AudioTracks.Items()), enumerate(media.SubtitleTracks.Items())):
                relpath = os.path.relpath(track.FilePath, media.DirPath)
                track_labels = track._extract_labels()
                if track_labels != None:
                    symlink_file_name = '.'.join([media.Name, str(index + 1) + " - " + ".".join(track_labels), Path(track.FilePath).suffix.lstrip('.')])
                symlink_file = os.path.join(media.DirPath, symlink_file_name)
                os.symlink(relpath, symlink_file)

    @property
    def Medias(self):
        return self._medias

    @property
    def MediaPaths(self):
        return self.__media_paths
    @property
    def FilePaths(self):
        return self.__file_paths