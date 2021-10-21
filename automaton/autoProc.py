import os
import sys
import inspect
import subprocess
import ast
import glob

import time
from datetime import datetime
import pytz   # From timezone handling

import dotenv

from multiprocessing import Process

from pathlib import Path

# Locl imports - hacky!
try:
    from auto_util import setPathsFile, triggerNotebook   # Works at CLI with this
except:
    from .auto_util import setPathsFile, triggerNotebook   # Need . for general class importing, but this fails at CLI as main?

# Slack stuff... Quick hack for sister pkg import.
try:
    modDir = Path(os.path.dirname(os.path.realpath(__file__))).parent  # Get parent dir for current script.
    sys.path.append(modDir.as_posix())
    # print(sys.path)
    from analysis_bot.analysis_bot import slack_client_wrapper
except ImportError as e:
    print(f"*** Slack routines not available. ImportError: {e}")


class autoProc():
    """
    - Wrap auto_util.py functions to class.
    - Add file handling routines.

    TODO: use .env file for paths? Easier than using init() method.
        THIS IS CURRENTLY VERY UGLY. Some automation with locals() possible, although all a bit ad hoc here.

        Logging - see watchdog for example https://pypi.org/project/watchdog/

        Time for notebook generation (currently in notebook only)

        Running as deamon, see https://pypi.org/project/python-daemon/

        Test & finish Slack integration. May want to use nbconvert figure export, see https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html#Using-different-preprocessors

    """

    # Updated version from file
    def __init__(self, settingsFile = '.settings'):
        """Init autoProc class using settings file."""

        # Get options from file
        self.options = dotenv.dotenv_values(dotenv_path = settingsFile)

        # Check options loaded... dotenv returns empty dict if file not found.
        if not self.options:
            print(f"***FAILED to load settings file {settingsFile}.")

        # Ensure fileType list is set correctly
        if isinstance(self.options['fileType'], str):
            if self.options['fileType'].startswith('['):
                self.options['fileType'] = ast.literal_eval(self.options['fileType'])  # Convert string list to list type
            else:
                self.options['fileType'] = [self.options['fileType']]  # Wrap single item to list

        # Fix int type, ugh. Must be a neater way to do this for dotenv lib, only pulls to str type?
        [self.options.update({k:int(self.options[k])}) for k in ['verbose', 'pollRate']]

        self.verbose = self.options['verbose']

        # Set paths
        self.paths = setPathsFile(pathType = self.options['pathType'], fileIn = settingsFile, fType = 'settings', verbose = self.verbose)

        # Check current file list
        self.files = {}
        self.files['init'] = self.getFileList()


        # Slack stuff...
        try:
            self.slack_client_wrapper = slack_client_wrapper()
            self.channel_ID = self.options['channel_ID']
        except:
            self.slack_client_wrapper = False



    # def __init__(self, watchDir = None, pollRate = 5,
    #             nbDir = None, nbTemplate = None,
    #             outDir = None, htmlDir = None,
    #             fileType = ['h5','html'], channel_ID = 'C02HP5X1F2S',
    #             verbose = True):
    #
    #


        # Old init
        # # Set paths - repo defaults
        # self.paths = setPaths()
        #
        # # Path for notebook templates
        # if nbDir is None:
        #     nbDir = self.paths['repoDir']/'nbTemplates'
        #
        # self.paths['nbDir'] = Path(nbDir)
        #
        # # Watch path
        # if watchDir is None:
        #     watchDir = Path(os.getcwd())
        #
        # self.paths['watchDir'] = Path(watchDir)
        #
        # # Output paths
        # if outDir is None:
        #     outDir = watchDir
        #
        # self.paths['outDir'] = Path(outDir)
        #
        # if htmlDir is None:
        #     htmlDir = outDir
        #
        # self.paths['htmlDir'] = Path(htmlDir)
        #
        #
        # # Additional options
        # self.options = {}
        # self.options['pollRate'] = pollRate
        #
        # if fileType is None:
        #     fileType = ['*']
        #
        # if not isinstance(fileType, list):   # Force to list for glob routine
        #     fileType = [fileType]
        #
        # self.options['fileType'] = fileType
        #
        # if nbTemplate is None:
        #     self.options['nbTemplate'] = 'autoTestNB.ipynb'
        #
        # self.verbose = verbose
        #
        # # Check current file list
        # self.files = {}
        # self.files['init'] = self.getFileList()
        #
        #
        # # Slack stuff...
        # try:
        #     self.slack_client_wrapper = slack_client_wrapper()
        #     self.channel_ID = channel_ID
        # except:
        #     self.slack_client_wrapper = False

    # def getFileList(self):
    #     """Get file list from dir & return as dict (as per demo pollDir code)."""
    #     return dict([(f, None) for f in os.listdir(self.paths['watchDir']) if f.endswith(self.options['fileType'])])

    def compareFileDicts(self, dict1, dict2):
        """Compare two file dictionaries for differences"""

        fileDiffs = {}
        fileDiffs['added'] = {}
        fileDiffs['removed'] = {}

        for fileType in self.options['fileType']:

            removed = set(dict1[fileType]) - set(dict2[fileType])  # Files missing in dict2 (=="removed")
            added = set(dict2[fileType]) - set(dict1[fileType])  # Files missing in dict1 (=="added")

            for k in fileDiffs.keys():
                if locals()[k]:
                    fileDiffs[k][fileType] = locals()[k]

                    if self.verbose:  print(f"{k}: {locals()[k]}")

#             if fileDiffs[fileType]['removed']:
#                 print(f"Removed: {fileDiffs[fileType]['removed']}")

#             if fileDiffs[fileType]['added']:
#                 print(f"Added: {fileDiffs[fileType]['added']}")

        return fileDiffs


    def getFileList(self):
        """
        Get file list from dir & return as dict.

        Checks multiple fileTypes and returns as fileDict['fileType'] = fileList
        Will also check subdirs if self.options['subdirs'] = True (default).

        """

        fileDict = {}

        for fileType in self.options['fileType']:
            fileDict[fileType] = glob.glob((self.paths['watchDir']/'**'/f'*.{fileType}').as_posix(), recursive = self.options['subdirs'])  # ** and recursive = True for subdirs

        return fileDict


    def getTimes(self, timezones = ['Asia/Tokyo','Europe/London','US/Eastern','US/Pacific'], timeFormat = '%Y-%m-%d %H:%M:%S'):
        """Get times in various zones."""

        utcNow = datetime.now(pytz.utc)
        localTime = datetime.now()  #.astimezone()  # .astimezone returns full tz object from system, https://stackoverflow.com/a/52606421

        times = {tz: utcNow.astimezone(pytz.timezone(tz)).strftime(timeFormat) for tz in timezones}
        times.update({'local':localTime.strftime(timeFormat)})

        return times


    # Basic fn. wrapper - but better to put here for self?
    # def poll(self):
    #     self.pollDir(dir = self.paths['watchDir'], pollRate = self.options['pollRate'], verbose = self.verbose)

   # Adapted polling code
    def pollDir(self):
        """
        Basic dir polling.

        Adapted from http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html

        NOTE: may want to switch to scandir() for subdir processing?
        E.g. subfolders = [ f.path for f in os.scandir(folder) if f.is_dir() ]

        """

        dir = self.paths['watchDir']

        if self.verbose:
            print(f'Watching {dir} for changes...')

        before = self.getFileList()

        while 1:
            time.sleep(self.options['pollRate'])
            after = self.getFileList()
        #             added = [f for f in after if not f in before]
        #             removed = [f for f in before if not f in after]

            fileDiffs = self.compareFileDicts(before, after)

        #             for k in fileDiffs.keys():
            # Actions for new files
            k = 'added'
            if fileDiffs[k]:
                # Execute specific actions for different file types.
                for fType in fileDiffs[k]:

                    if self.verbose:
                        now = self.getTimes()
                        print(f"{now['local']}: Files added: {fileDiffs[k][fType]}")


                    if k == 'added' and fType == 'h5':
                        # Spawn notebook(s)
                        for item in fileDiffs[k][fType]:
                            # triggerNotebook(item, nbDir = self.paths['nbDir'], nbTemplate = self.options['nbTemplate'])  # Direct notebook build call

                            # Subproc call
                            # cmd = f"auto_util({item}, nbDir = {self.paths['nbDir']}, nbTemplate = {self.options['nbTemplate']})"
                            # subprocess.run(cmd)

                            # As python process, https://docs.python.org/3/library/multiprocessing.html
                            # p = Process(target=triggerNotebook, args=[item], kwargs = {'nbDir': self.paths['nbDir'], 'nbTemplate': self.options['nbTemplate']})
                            p = Process(target=triggerNotebook, args=[item], kwargs = self.paths)
                            p.start()


                            if self.verbose:
                                now = self.getTimes()
                                print(f"{now['local']}: Triggered build for {item}")
                                # print(type(item))

                            # Optional import, set to False if missing.
                            if self.slack_client_wrapper:
                                # Do some slack posting here!
                                now = self.getTimes()
                                self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f'Found new datafile {item}, processing... \n({now}))')  #\n\n (Images & URL go here!)')


                    if k == 'added' and fType == 'html':
                        # Upload HTML file(s)
                        for item in fileDiffs[k][fType]:
                            # Optional import, set to False if missing.
                            if self.slack_client_wrapper:
                                # Do some slack posting here!
                                now = self.getTimes()
                                self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f'Processed {item}. Images & URL go here!)')

            # Actions for removed files
            k == 'removed'
            if fileDiffs[k] and self.verbose:
                now = self.getTimes()
                print(f"{now['local']}: Files removed: {fileDiffs[k][fType]}")

            # Update master list
            before = after



if __name__ == '__main__':

    testClass = autoProc()

    testClass.pollDir()
