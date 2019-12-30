# Picasa conversion
#
# Charley Chell
# December 27, 2019


import os

fCheck = True                   # Flag to do consistency checks
fMove = True                    # Flag to disable file moves, good to turn this off on first tests

dirOriginals = './Originals'    # Input directories. Pictures are in subdirectories here. This points to the originals
dirModified = './Exports'       # And this points to Picasa exports.  Exports are manually produced
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
        if fname.startswith('.') and not fname == '.picasa.ini':
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
                            # Otherwise it could mean one of several things.  Either the originals are not stored
                            # in the assumed directory structure, were moved or deleted manually, or that the script
                            # is being rerun rather than starting from scratch.  Look at the warnings and decide
                            # if its okay
                            print('\tUnexpected file %s ' % imgName)
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
            if fname.startswith('.') and not fname == '.picasa.ini':
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
            try:
                os.rename(expName, targetName)
            except FileNotFoundError:
                print('\t\tFile %s not found, skipping' % expName)
            try:
                os.rename(origName, targetOrigName)
            except FileNotFoundError:
                print('\t\tFile %s not found, skipping' % origName)
        else:
            print('\tModified: Copy %s to  %s' % (expName, targetName))
            print('\t\tAnd Copy %s to %s' % (origName, targetOrigName))

    else:
        if fMove:
            try:
                os.rename(origName, targetName)
            except FileNotFoundError:
                print('\t\tFile %s not found, skipping' % origName)
        else:
            print('\tUnmodified: Copy %s to %s' % (origName, targetName))

