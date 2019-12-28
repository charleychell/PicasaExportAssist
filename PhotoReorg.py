#
# Picasa conversion
#
# Charley Chell
# December 27, 2019
#
# Picasa uses non destructive editing. The original is never modified, instead, a set of editing instructions
# are kept for each edited file in a hidden file called .picasa.ini.  Files that have been edited will be listed, and
# files that have not been edited won't be listed.
#
# The editing instructions are apparently proprietary to Picasa so the only way to migrate the edits is to export
# each picture.  Pacasa has no known batch commandline interface but it's pretty easy to select an album, select all
# pictures in the album and export them to a subdirectory under a main directory that I'll call "Export".
# Unfortunately, for unedited pictures, Picasa still re-renders them on export so it degrades the original pictures
# clarity.
#
# This program accepts a two sets of pictures, (the originals and exported versions), structured as two directories
# with subdirectories for each album.  The subdirectory (album) names are assumed to be the same in the originals
# and export directories.  Thus we have two parallel structures of the same pictures.
#
# The program reproduces the album subdirectories in a target output directory and selectively moves one picture
# to the them to a target directory.   It keeps the best version, either the edited picture if edits were made,
# or the original picture if not.  Where the picture was edited, the original is moved to a separate target directory
# in case it should ever be needed.  To save space, for unedited pictures the original is not duplicated.
# You can choose to import these into your new photo app, or simply keep a backup of the entire original photo library.
#
# Inputs, defined as static variables for convenience since it is easy to just run the script in the IDE.
#  - A directory of pictures, with the .picasa file
#  - A directory of exports, likely with the same set of file names. These are the Picasa exported picture
#  - A destination root directory, which cannot be the source directory
#  - A destination root directory for the original versions of the modified pictures
#
# Outputs
#  - A directory of the modified pictures, and originals for everything else
#  - A subdirectory, named originals, of the originals for the modified pictures only   TODO Capitalize or not?
#
# Operation
#   This program works by moving pictures rather than copying them.  Faster, and easier to see what's been done
#   Should be able to be run multiple times, picking up where it left off, for development and issues.
#   Should only move jpeg files, or whatever the cameras did
#   Discards the .picasa.ini files, which are of no value
#
# Approach
# The program enumerates each input directory and examines the .picasa.ini files.  It captures the results in a
# dictionary.  The key is the relative path to the picture and the data are three flags.
# - the picture is in the .picasa.ini file
# - the picture is in the originals directory
# - the picture is in the exports directory
# There are eight cases. The first and fifth are the common cases.
#   In .picasa  | in originals | in exports | Action
#        Y      |       Y      |      Y     | Normal: Picture edited - Copy exports to dest, copy original to the secondary location
#        Y      |       Y      |      N     | Warning, the picture should have been in exports.  Save the  original
#        Y      |       N      |      Y     | Warning, all pictures should be in originals.  Save the exported version
#        Y      |       N      |      N     | Warning, the picture doesn't exist anywhere
#        N      |       Y      |      Y     | Normal: Picture unretouched - Save the original, ignore exported version
#        N      |       Y      |      N     | Warning, all pictures should be in the exports. Save the original
#        N      |       N      |      Y     | Warning, picture should be in the originals.  Save the exported version.
#        N      |       N      |      N     | Case shouldn't exist


import os

fCheck = True                   # Flag to do consistency checks
fMove = True                    # Flag to disable file moves, good to turn this off on first tests

dirOriginals = './Originals'    # Input directories. Pictures are in subdirectories here. This points to the originals
dirModified = './Export'        # And this points to Picasa exports.  Exports are manually produced
dirOutput = './ImportThis'      # Destination directory.  Modified/originals pictures go here
dirOutputOriginals = './OriginalsForModifiedPictures'   # Destination for the originals of modified pictures
# Working directory is the parent of all of these

# Using a dictionary of 3-element arrays to store picture information.
fModified = 0       # The picture was noted in the picasa.ini file as modified
fOriginal = 1       # The picture was found in the originals directory
fExported = 2       # The picture was found in the export directory
dImages = {}        # Keys for this hash array are the subdirectory and filename of the picture


# STEP 1: Parse the directories to create dImages{[fModified, fOriginal, fExported]}

# Enumerate the originals
# Note, this must come first.  We assume that originals must exist for all pictures,
# otherwise, how could we have created an export version?
# Also, if the script fails or exits then some original files may already be moved.  In those cases
# the Export will be ignored (it's probably been moved anyway), and the .picasa.ini entry will be ignired
os.chdir(dirOriginals)
rootDir = './'
print('Parsing Originals Directory %s' % os.getcwd())
for dirName, subdirList, fileList in os.walk(rootDir):
#    print('Found directory: %s' % dirName)
    for fname in fileList:
        if fname.startswith('.'):               # TODO Really don't have to print this warning
            print('\tIgnoring %s' % fname)
        else:
            imgName = dirName + '/' + fname
#            print('%s' % imgName)
            dImages[imgName] = [False, True, False]

# Parse the .picasa.ini files while we're still in the Originals directory
print('Parsing the .picasa.ini files')
for dirName, subdirList, fileList in os.walk(rootDir):
#    print('Found directory: %s' % dirName)
    for fname in fileList:
        if fname == '.picasa.ini':
#            print('\tFound %s' % fname)
            picasaName = dirName + '/' + fname
            f = open(picasaName, 'r')
            for l in f:
                if l.startswith('['):
                    imgName = dirName + '/' + l[1:-2]
#                    print(imgName)
                    if imgName in dImages:
                        dImages[imgName][fModified] = True
                    else:
                        if not imgName.endswith('Picasa'):   # The first line of the line is [Picasa]
                            print('\tUnexpected file %s ' % imgName)        # TODO Not really an error.  Just means we didn't start from stratch
            f.close()

# Enumerate the exports
# Directory structure is assumed to be parallel
os.chdir('../.')
os.chdir(dirModified)
rootDir = './'
print('Parsing Export Directory %s' % os.getcwd())
for dirName, subdirList, fileList in os.walk(rootDir):
#   print('Found directory: %s' % dirName)
    for fname in fileList:
        imgName = dirName + '/' + fname
#        print('%s' % imgName)
        if imgName in dImages:
            dImages[imgName][fExported] = True
        else:
            if fname.startswith('.'):
                print('\tIgnoring %s' % fname)
            else:
                print('\tUnexpected file %s, not in originals ' % imgName)        # The picture wasn't in the originals dir

#print(dImages)

#
# STEP 2: Move the files around
#
# Pre-create the directory structures for the two target directories.  Do it from the Originals directory
# since that is what we're replicating
os.chdir('../.')
os.chdir(dirOriginals)
rootDir = './'
print('Creating target directories')
for dirName, subdirList, fileList in os.walk(rootDir):
    newDir = '../' + dirOutput + '/' + dirName  # remember, we're in the Originals dir
    if fMove:
        os.makedirs(newDir, exist_ok=True)
    else:
        print('\tCreating %s' % newDir)
    newDir = '../' + dirOutputOriginals + '/' + dirName
    if fMove:
        os.makedirs(newDir, exist_ok=True)
    else:
        print('\tCreating %s' % newDir)

# Move the pictures
os.chdir('../.')
print('Organizing Pictures in %s' % os.getcwd())
for imgName, flags in dImages.items():    # Remember imgName contains the path from the rootDir
#    print(imgName, flags)
    if fCheck:
        if not (flags[fOriginal] and flags[fExported]):
            print('\tUnexpected', imgName, flags)

    origName = dirOriginals + '/' + imgName
    expName = dirModified + '/' + imgName
    targetName = dirOutput + '/' + imgName
    targetOrigName = dirOutputOriginals  + '/' + imgName

    if flags[fModified]:
        if fMove:
            os.rename(expName, targetName)
            os.rename(origName, targetOrigName)
        else:
            print('Modified: Copy %s to  %s' % (expName, targetName))
            print('\tAnd Copy %s to %s' % (origName, targetOrigName))       # this failed, first time

    else:
        if fMove:
            os.rename(origName, targetName)
        else:
            print('Unmodified: Copy %s to %s' % (origName, targetName))

