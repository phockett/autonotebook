import os
import sys
import inspect
import subprocess
import ast
import glob
import pprint

import time
from datetime import datetime
import pytz   # From timezone handling

import dotenv

from multiprocessing import Process

from pathlib import Path

# Locl imports - hacky!
try:
    from auto_util import setPathsFile, triggerNotebook, getFigFiles   # Works at CLI with this
    from serveHTML import initNgrok, getPort, serveDir
except:
    from .auto_util import setPathsFile, triggerNotebook, getFigFiles   # Need . for general class importing, but this fails at CLI as main?
    from .serveHTML import initNgrok, getPort, serveDir

# Slack stuff... Quick hack for sister pkg import.
try:
    modDir = Path(os.path.dirname(os.path.realpath(__file__))).parent  # Get parent dir for current script.
    sys.path.append(modDir.as_posix())
    # print(sys.path)
    from analysis_bot.analysis_bot import slack_client_wrapper
except Exception as e:
    print(f"*** Slack routines not available. Error: {e}")


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

        watch dir for changes to settings file & update running processes.

    """

    # Updated version from file
    def __init__(self, settingsFile = '.settings'):
        """Init autoProc class using settings file."""

        self.getOptions(settingsFile)


        # Slack stuff...
        self.slack_client_wrapper = False
        try:
            if self.options['slack']:
                self.slack_client_wrapper = slack_client_wrapper(token = self.options['SLACK_TOKEN'])
                self.channel_ID = self.options['channel_ID']

                if self.verbose:
                    print(f"\n*** Slack client OK, channel_ID: {self.channel_ID}")

            else:
                if self.verbose:
                    print(f"\n*** Slack integration off.")

        except Exception as e:
            print(f"Slack client failed: {e}")

            # if self.verbose:
            #     print(f"Couldn't load Slack client")

        # Server stuff
        # Note explicit setting for ports etc here.
        if self.options['serve']:
            if self.verbose:
                print(f"\n*** Spawning server...")

            if not self.options['port']:
                self.options['port'] = getPort().getsockname()[1]
            else:
                self.options['port'] = int(self.options['port'])  # Force to int value if read from settings file.

            # Try to init pyngrok, skip if not present
            if not self.options['public_url']:
                self.options['public_url'] = f"http://127.0.0.1:{self.options['port']}"  # Default to localhost
            else:
                self.options['public_url'] = f"{self.options['public_url']}:{self.options['port']}"  # Add port if base supplied

            if self.options['ngrok']:
                self.options['public_url'] = initNgrok(self.options['port'])
                # try:
                #     self.options['public_url'] = initNgrok(port)
                # except:
                #     pass


            # Spawn server - process or thread?
            # See, e.g., https://stackoverflow.com/questions/63928479/unable-to-run-python-http-server-in-background-with-threading
            # serveDir(port = None, htmlDir = None, public_url=None)

            p = Process(target=serveDir, kwargs = {'port':self.options['port'], 'htmlDir':self.paths['htmlDir'].as_posix(),
                                    'public_url':self.options['public_url'], 'useNgrok':self.options['ngrok']})
            p.start()


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

    def getOptions(self, settingsFile = None):
        """
        Get settings from file.

        TODO: watch dir for changes to settings file & update running processes.
        """

        # Get options from file
        updateFlag = False
        if settingsFile is None:
            settingsFile = self.settingsFile  # Use this if set

            if settingsFile:
                updateFlag = True
            else:
                settingsFile = '.settings'  # Default case

        if updateFlag:
            optionsOld = self.options.copy()
            options = dotenv.dotenv_values(dotenv_path = settingsFile)
            self.options.update({k:v for k,v in options.items() if (k not in ['port','public_url']) and (not k.endswith('Dir'))})  # Skip these for update case
            # optionDiffs = {k:v for k,v in options.items() if v != optionsOld[k]}  # Log changes - do this later, after type checks etc.

        else:
            self.options = dotenv.dotenv_values(dotenv_path = settingsFile)

        # Check options loaded... dotenv returns empty dict if file not found.
        if not self.options:
            print(f"***FAILED to load settings file {settingsFile}.")
        else:
            self.settingsFile = Path(settingsFile).expanduser().resolve()
            if self.options['verbose']:
                if updateFlag:
                    print(f"Updating settings from file...")

                else:
                    print(f"***Loaded settings file {self.settingsFile}.")

        # Ensure fileType list is set correctly
        # if isinstance(self.options['fileType'], str):
        #     if self.options['fileType'].startswith('['):
        #         self.options['fileType'] = ast.literal_eval(self.options['fileType'])  # Convert string list to list type
        #     else:
        #         self.options['fileType'] = [self.options['fileType']]  # Wrap single item to list

        # General check for lists.
        [self.options.update({k:ast.literal_eval(v)}) for k,v in self.options.items() if isinstance(v, str) and v.startswith('[')]

        # Fix int type, ugh. Must be a neater way to do this for dotenv lib, only pulls to str type?
        # [self.options.update({k:int(self.options[k])}) for k in ['verbose', 'pollRate', 'subdirs','outputSub','serve','ngrok','slack']]
        [self.options.update({k:int(v)}) for k,v in self.options.items() if isinstance(v, str) and v.isdigit()]

        if self.options['figList']:
            self.options['figList'] = [(int(v[0]), int(v[1])) for v in self.options['figList']]  # Force figList to int, since above will miss it.

        self.verbose = self.options['verbose']


        # Set paths
        self.paths = setPathsFile(pathType = self.options['pathType'], fileIn = settingsFile, fType = 'settings', verbose = self.verbose if not updateFlag else False)

        # Check current file list
        self.files = {}
        self.files['init'] = self.getFileList()

        # Log changes
        if updateFlag:
            optionDiffs = {k:v for k,v in self.options.items() if v != optionsOld[k]}

            if optionDiffs:
                print(f"\t Updated settings: {optionDiffs}.")
            else:
                print("\t No changes found.")

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
        times.update({'local':localTime.strftime(timeFormat), 'utc':utcNow.strftime(timeFormat)})

        return times


    # Basic fn. wrapper - but better to put here for self?
    # def poll(self):
    #     self.pollDir(dir = self.paths['watchDir'], pollRate = self.options['pollRate'], verbose = self.verbose)

   # Adapted polling code
    def pollDir(self):
        """
        Basic dir polling.

        Adapted from http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html

        NOTE: now runs getSettings() on data file appearance, but doesn't monitor file directly.

        NOTE: Slack message posting with simple Markdown only, but can implement blocks. Also posts messages independently, but may want to consolidate all messages for a dataset?

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
                        # Check settings are up-to-date
                        self.getOptions()

                        # Spawn notebook(s)
                        for item in fileDiffs[k][fType]:
                            currDataFile = Path(item).name  # Set to use later for current dataFile.

                            # triggerNotebook(item, nbDir = self.paths['nbDir'], nbTemplate = self.options['nbTemplate'])  # Direct notebook build call

                            # Subproc call
                            # cmd = f"auto_util({item}, nbDir = {self.paths['nbDir']}, nbTemplate = {self.options['nbTemplate']})"
                            # subprocess.run(cmd)

                            # As python process, https://docs.python.org/3/library/multiprocessing.html
                            # p = Process(target=triggerNotebook, args=[item], kwargs = {'nbDir': self.paths['nbDir'], 'nbTemplate': self.options['nbTemplate']})

                            # If specified, output to relative subdir
                            # CHECK OLD CODE FOR THIS - want relative subdir only for case when watchDir != outDir?
                            self.itempaths = self.paths.copy()   # Set copy to reuse master dict.
                            if self.options['subdirs'] and self.options['outputSub']:

                                self.itempaths['subdir'] = Path(item).parent.relative_to(self.paths['watchDir'])  # Get subdirs for item (relative to base dir)
                                # self.paths['outDir'] = self.paths['outDir']/subdir   # Build same dir tree for outDir - CAN'T RETURN TO MASTER OR WILL TREE
                                self.itempaths['outDir'] = self.paths['outDir']/self.itempaths['subdir']
                                self.itempaths['htmlDir'] = self.paths['htmlDir']/self.itempaths['subdir']
                                self.itempaths['nbTemplate'] = self.options['nbTemplate']

                                # Format output filename
                                self.itempaths['nbOut'] = Path(item).stem + '_' + Path(self.itempaths['nbTemplate']).stem + '_' + self.getTimes(timeFormat = '%Y-%m-%d_%H-%M-%S')['utc']

                            # Check dirs exist, create if not
                            for checkDir in ['outDir','htmlDir']:
                                Path(self.itempaths[checkDir]).mkdir(parents=True, exist_ok=True)

                            p = Process(target=triggerNotebook, args=[item], kwargs = self.itempaths)
                            p.start()


                            if self.verbose:
                                now = self.getTimes()
                                print(f"{now['local']}: Triggered build for {item}")
                                # print(type(item))

                            # Optional import, set to False if missing.
                            if self.slack_client_wrapper and self.options['slack']:
                                # Do some slack posting here!
                                now = self.getTimes()
                                timeStr = pprint.pformat(now).strip('{').strip('}')

                                # self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f'Found new datafile {Path(item).name}, processing... \n({now}))')  #\n\n (Images & URL go here!)')
                                hostTemplateStr = f"\nhost: `{os.uname()[1]}`\ntemplate: `{Path(self.itempaths['nbTemplate'])}`\ntime: {self.getTimes(timeFormat = '%Y-%m-%d_%H-%M-%S')['utc']} UTC."
                                ts = self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f":robot_face: *Found new data file: {Path(item).name}*.")
                                if ts is not None:
                                    self.slack_client_wrapper.post_message(channel=self.channel_ID, thread_ts = ts, message=f":clock2: Time \n{timeStr}")
                                    self.slack_client_wrapper.post_message(channel=self.channel_ID, thread_ts = ts, message=f":computer: Processing... {hostTemplateStr}... ")


                    if k == 'added' and fType == 'html':
                        # Upload HTML file(s)
                        for item in fileDiffs[k][fType]:
                            # Skip linked HTML docs (used for figure output only)
                            postFlag = True if not item.endswith('_linked.html') else False

                            itemURL = ''
                            if postFlag and self.options['serve']:
                                base = self.options['public_url']
                                itemURL = f"{base}/{Path(item).relative_to(self.paths['htmlDir'])}"

                                if self.verbose:
                                    print(f"URL: {itemURL}")


                            # Optional import, set to False if missing.
                            if self.slack_client_wrapper and self.options['slack']:
                                now = self.getTimes()
                                if postFlag:
                                    # Do some slack posting here!

                                    # self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f'Processed {currDataFile}: {itemURL}.')

                                    if itemURL:
                                        ts = self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f":notebook: *Processed notebook link:* <{itemURL}|*{currDataFile}*>")
                                        if ts is not None:
                                            self.slack_client_wrapper.post_message(channel=self.channel_ID, thread_ts = ts, message=f":computer: Processed {hostTemplateStr}")
                                    else:
                                        ts = self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f":notebook: *Processed notebook {currDataFile}*")
                                        if ts is not None:
                                            self.slack_client_wrapper.post_message(channel=self.channel_ID, thread_ts = ts, message=f":computer: Processed {hostTemplateStr}")

                                # Case for HTML file with separate figs - just post these
                                # Not sure whether to run this as separate job, or integrate with above?
                                # Would just need figDir = Path(nbHTMLout).parent/Path(nbHTMLout).stem as per convertHTMLfigs() code.
                                else:
                                    figFiles = getFigFiles(Path(item).parent/Path(item[:-12]).stem, refList = self.options['figList'])
                                    sortedKeys = [k for k in self.options['figList'] if k in figFiles.keys()]

                                    if figFiles:
                                        ts = self.slack_client_wrapper.post_message(channel=self.channel_ID, message=f":chart_with_upwards_trend: *{currDataFile} figures:*",
                                                                                # attachments = {k:v.as_posix() for k,v in figFiles.items()})
                                                                                # attachments = [v.as_posix() for k,v in figFiles.items()])
                                                                                attachments = [figFiles.get(sortedKey).as_posix() for sortedKey in sortedKeys])
                                        if ts is not None:
                                            self.slack_client_wrapper.post_message(channel=self.channel_ID, thread_ts = ts, message=f":computer: Processed {hostTemplateStr}")

                                    if self.verbose:
                                        print(f"Posting figures {figFiles}")



            # Actions for removed files
            # k = 'removed'
            # if fileDiffs[k] and self.verbose:
            #     now = self.getTimes()
            #     print(f"{now['local']}: Files removed: {fileDiffs[k][fType]}")

            # Update master list
            before = after.copy()



if __name__ == '__main__':
    """
    If main, start watcher process from passed file, or default.
    """

    if len(sys.argv)>1:
        autoNote = autoProc(settingsFile=sys.argv[1])
    else:
        autoNote = autoProc()

    autoNote.pollDir()
