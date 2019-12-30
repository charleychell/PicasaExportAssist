Organizes photos gathered and exported from Picasa for import to another application

Picasa uses non destructive editing. The original is never modified, instead, a set of editing instructions
are kept for each edited file in a hidden file called .picasa.ini.  Files that have been edited will be listed, and
files that have not been edited won't be listed.

The editing instructions are apparently proprietary to Picasa so the only way to migrate the edits is to export
each picture.  Pacasa has no known batch commandline interface but it's pretty easy to select an album, select all
pictures in the album and export them to a subdirectory under a main directory that I'll call "Export".
Unfortunately, for unedited pictures, Picasa still re-renders them on export so it degrades the original pictures
clarity.

This program accepts a two sets of pictures, (the originals and exported versions), structured as two directories
with subdirectories for each album.  The subdirectory (album) names are assumed to be the same in the originals
and export directories.  Thus we have two parallel structures of the same pictures.

The program reproduces the album subdirectories in a target output directory and selectively moves one picture
to the them to a target directory.   It keeps the best version, either the edited picture if edits were made,
or the original picture if not.  Where the picture was edited, the original is moved to a separate target directory
in case it should ever be needed.  To save space, for unedited pictures the original is not duplicated.
You can choose to import these into your new photo app, or simply keep a backup of the entire original photo library.

Inputs, which ar3 defined as static variables for convenience since it is easy to just run the script in the IDE.
  - A directory of pictures, with the .picasa file
  - A directory of exports, likely with the same set of file names. These are the Picasa exported picture
  - A destination root directory, which cannot be the source directory
  - A second destination root directory for the original versions of the modified pictures

Outputs
  - A directory of the modified pictures, and originals for everything else
  - A subdirectory, named originals, of the originals for the modified pictures only   TODO Capitalize or not?

Operation
This program works by moving pictures rather than copying them.  Faster, and easier to see what's been done
Should be able to be run multiple times, picking up where it left off, for development and issues.
Should only move jpeg files, or whatever the cameras did
Discards the .picasa.ini files, which are of no value

Approach
The program enumerates each input directory and examines the .picasa.ini files.  It captures the results in a
dictionary.  The key is the relative path to the picture and the data are three flags.
  - the picture is in the .picasa.ini file
  - the picture is in the originals directory
  - the picture is in the exports directory
 
 There are eight cases. The first and fifth are the common cases.
 
| In .picasa   | in originals | in exports | Meaning | Action |
| :---: | :---: | :---: | :--- | :--- |
|       Y      |       Y      |      Y     | Normal, picture edited | Save both the exported and original versions |
|       Y      |       Y      |      N     | Warning, the picture should have been in exports | Save the  original |
|       Y      |       N      |      Y     | Warning, all pictures should be in originals | Save the exported version |
|       Y      |       N      |      N     | Warning, the picture doesn't exist anywhere | None |
|       N      |       Y      |      Y     | Normal, picture unretouched | Save the original, ignore exported version |
|       N      |       Y      |      N     | Warning, all pictures should be in the exports | Save the original |
|       N      |       N      |      Y     | Warning, picture should be in the originals | Save the exported version. |
|       N      |       N      |      N     | Case shouldn't exist | None |
