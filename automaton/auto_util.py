"""
Functions for folder monitoring + notebook automation
17/10/21

Pulling mainly from ePSproc & ePSman existing routines.

"""

import os
import inspect
import subprocess
import shlex
import time

from pathlib import Path

# Set paths
def setPaths(verbose = True):
    """
    Set paths from current file/context.

    """

    paths = {}
    paths['currDir'] = Path(os.getcwd())
    paths['repoDir'] = Path(os.path.abspath(inspect.getfile(setPaths))).parent # inspect.getfile(inspect)   # OK - call on a function
    paths['scpDir'] = Path(os.path.dirname(os.path.realpath(__file__)))  # Get path for current file/script

    if verbose:
        print(f"Working dir {paths['currDir']} \nrepo dir {paths['repoDir']} \nscript dir {paths['scpDir']}")

    return paths

# Basic dir scan
def getFileList(scanDir = None, fileType = 'h5', verbose = True):
    """Get a file list from host - scan directory=dir for files of fileType.

    Parameters
    ----------
    scanDir : string, defaults to cwd
        Directory to scan.

    fileType : string, default = 'h5'
        File ending to match.

    verbose : bool, optional
        Print output details, default True.


    Returns
    -------
    list
        List files found.

    """

    currDir = os.getcwd()

    if scanDir is None:
        scanDir = currDir

    fileList = [os.path.join(scanDir, f) for f in os.listdir(scanDir) if f.endswith(fileType)]

    if verbose:
        print(f'\n***File List (from {scanDir}):')
        print(*fileList, sep='\n')


def pollDir(dir = None, pollRate = 5, verbose = True):
    """
    Basic dir polling.

    Adapted from http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html

    NOTE: may want to switch to scandir() for subdir processing?
    E.g. subfolders = [ f.path for f in os.scandir(folder) if f.is_dir() ]

    """

    currDir = os.getcwd()

    if dir is None:
        dir = currDir

    if verbose:
        print(f'Watching {dir} for changes...')

    before = dict ([(f, None) for f in os.listdir(dir) if f.endswith(fileType)])
    while 1:
      time.sleep (pollRate)
      after = dict ([(f, None) for f in os.listdir(dir) if f.endswith(fileType)])
      added = [f for f in after if not f in before]
      removed = [f for f in before if not f in after]

      if added:
          if verbose:

            print("Added: ", ", ".join (added))

          # Spawn trigger per new item
          for item in added:
              triggerNotebook(item)
              # print(type(item))

      if removed and verbose: print("Removed: ", ", ".join (removed))
      before = after


def triggerNotebook(dataFile, outDir = None, nbOut = None, nbDir = None, nbTemplate = None, htmlDir = None, **kwargs):
    """
    Run nbconvert from notebook template with specified data file (passed as env var).

    This requires the notebook to include something like `dataFile = os.environ.get('DATAFILE', '')`

    TODO: separately extract figures from HTML, see https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html#Using-different-preprocessors
    Alternatively, could save figs from notebook at execute.

    """

    # Set and modify env, https://stackoverflow.com/questions/2231227/python-subprocess-popen-with-a-modified-environment
    currEnv = os.environ.copy()
    currEnv["DATAFILE"] = dataFile

    # print(currEnv)

    # Launch subprocess
    # TODO: trigger notebook with nbconvert or jupyter-runner
    # See ePSman...
    # subprocess.Popen(TODO, env=currEnv)
    # cmd = 'python subproc_test.py'  # Quick test - this is OK on Win, but fails on Linux, need full path (best practice in any case!)

    if nbDir is None:
        nbDir = os.getcwd()

    nbDir = Path(nbDir)

    if nbTemplate is None:
        nbTemplate = 'autoTestNB.ipynb'

    if outDir is None:
        outDir = nbDir

    if htmlDir is None:
        htmlDir = outDir

    if nbOut is None:
        nbOut = Path(dataFile).stem

    # nbTemplate = 'subproc_test.py'  # ENV test script
    # cmd = f"python {Path(nbDir, nbTemplate).as_posix()}"

    # Set command for nbconvert
    # Note "" for paths to allow for cases with whitespace
    # cmd1 = f'jupyter nbconvert --to notebook --execute "{Path(nbDir, nbTemplate).as_posix()}" --output "{Path(outDir, nbOut).as_posix()}" --allow-errors'
    # print(f"Running {cmd1}; {cmd2}")
    # subprocess.run([cmd1, cmd2], env=currEnv)  # Parallel?
    # subprocess.run(f'{cmd1}; {cmd2}', env=currEnv, capture_output=True, shell=True)  # Sequential - NOT working on Win machine? https://stackoverflow.com/questions/17742789/running-multiple-bash-commands-with-subprocess
                                                                                        # May need to use POPEN, https://stackoverflow.com/questions/39721924/how-to-run-multiple-commands-synchronously-from-one-subprocess-popen-command

    # Sequential run seems - default is for .run to wait for completion. Should be OK in general, unless processing in step 1 is very slow.
    cmd1 = f'jupyter nbconvert --to notebook --execute "{Path(nbDir, nbTemplate).as_posix()}" --output "{Path(outDir, nbOut).as_posix()}" --allow-errors'
    print(f"Executing notebook with: {cmd1}")
    # subprocess.run(cmd1, env=currEnv)
    subprocess.run(shlex.split(cmd1), env=currEnv) # Better form - OK on Linux & Win (without needing shell=True)

    # Generate HTML
    cmd2 = f'jupyter nbconvert --to HTML "{Path(outDir, nbOut).as_posix()}" --output "{Path(htmlDir, nbOut).as_posix()}" --allow-errors'
    print(f"Generating HTML with: {cmd2}")
    # subprocess.run(cmd2, env=currEnv)
    subprocess.run(shlex.split(cmd2), env=currEnv) # OK


#
# def main():
#     # getFileList()
#     pollDir()


# Use main to allow for building notebooks as subproc.
if __name__ == '__main__':
    setPaths()
    # main()
