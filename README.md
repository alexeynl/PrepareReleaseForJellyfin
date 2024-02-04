# Intro
## Why you need this?
Jellyfin is perfect media server for my needs except one thing. Server can add and stream external audio and subtitles additionaly to the main video. But Jellyfin requires that [external audio or subtitle file must be placed in the same directory and has the same name as video](https://jellyfin.org/docs/general/server/media/external-files/).
Most of torrent releasers on the other hand places external audio and subtitle tracks to subdirectories. In this case i need copy these external files to the video directory and sometimes rename those. 
The first problem: it's pain if you do this manually.
The second problem: if you move files you will broke your torrent download and you could not seeding. If you copy files instead you need extra storage to store duplicates that actiualy do not need.
## How this script works and solves these problems?
The main idea that scipt implements is to create symlink to the external file and place it next to the video. So you do not need extra storage and you stay all original files untouched on those places. So you are able to continue seeding downloads.
After applying this script the file structure will look like this:
<pre><code>
--Torrent name
----Torrent name.Ep01.mkv
----Torrent name.Ep01.mka <-- symlink to subdir .\Rus Sound\Torren release.Ep01.mka
----Torrent name.Ep01.ass <-- symlink to subdir .\Rus Subs\Torren release.Ep01.ssa
----Torrent name.Ep02.mkv
----Torrent name.Ep02.mka <-- symlink to subdir .\Rus Sound\Torren release.Ep02.mka
----Torrent name.Ep02.ass <-- symlink to subdir .\Rus Subs\Torren release.Ep02.ssa
                                   ...
------Rus Sound
--------Torrent name.Ep01.mka
--------Torrent name.Ep01.mka
                                   ...
------Rus Subs
--------Torrent name.Ep01.ass
--------Torrent name.Ep01.ass
                                   ...
</code></pre>
During the library scan Jellyfin server correctly detect this symlink as if those are original files and add aditional audio or subtitle streams.
