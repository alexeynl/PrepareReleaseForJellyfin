import glob, os
from pathlib import Path
from typing import List
import re
import Settings
from itertools import chain

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
        self._file_paths = glob.glob(self.Path + '/**/*', recursive=True)

    def _scan_for_media(self):
        for extenstion in self.MediaExtensions:
            self._media_paths = self._media_paths + list (filter(lambda x:x.endswith(extenstion), self._file_paths))

        for media_path in self._media_paths:
           media = Media(self, media_path)
           self._medias.Add(media)
           self._scan_for_tracks(media)
        pass

    def _scan_for_tracks(self, media: Media):
        related_files = list(filter(lambda x:Path(x).stem == media.Name, self._file_paths))

        audio_track_paths = list(filter(lambda x:Path(x).suffix in self.AudioTrackExtenstions, related_files))
        for audio_track_path in audio_track_paths:
            audio_track = ExternalTrack(media)
            audio_track.FilePath = audio_track_path
            media.AudioTracks.Add(audio_track)

        subtitle_track_paths = list (filter(lambda x:Path(x).suffix in self.SubtitleTrackExtensions, related_files))
        for subtitle_track_path in subtitle_track_paths:
            subtitle_track = ExternalTrack(media)
            subtitle_track.FilePath = subtitle_track_path
            media.SubtitleTracks.Add(subtitle_track)
        pass
    
    #create sym links for each media to external audio and subtitles track in the media directory
    def _create_sym_links(self):
        for media in self.Medias.Items():
            for track in chain(media.AudioTracks.Items(), media.SubtitleTracks.Items()):
                relpath = os.path.relpath(track.FilePath, media.DirPath)
                track_label = track._get_label()
                if track_label != None:
                    symlink_file_name = '.'.join([media.Name, track_label, Path(track.FilePath).suffix.lstrip('.')])
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

#release_path = "/srv/torrents/qbittorrent/downloads/anime/Vinland.Saga.Season2.WEBRip.1080p/"
release_path = r'C:\Users\homeadmin\Downloads\Anime\Vinland.Saga.Season2.WEBRip.1080p'
release = Release(release_path,[".mkv"], [".mka"], [".ass"])
release._create_sym_links()