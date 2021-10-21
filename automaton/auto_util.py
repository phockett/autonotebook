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

import dotenv

from pathlib import Path

#************* Paths

# Set paths
def setPaths(verbose = True):
    """
    Get paths from current file/context.

    """

    paths = {}
    paths['currDir'] = Path(os.getcwd())
    paths['repoDir'] = Path(os.path.abspath(inspect.getfile(setPaths))).parent # inspect.getfile(inspect)   # OK - call on a function
    paths['scpDir'] = Path(os.path.dirname(os.path.realpath(__file__)))  # Get path for current file/script

    if verbose:
        print(f"Working dir {paths['currDir']} \nrepo dir {paths['repoDir']} \nscript dir {paths['scpDir']}")

    return paths

def setPathsFile(pathType = 'rel', fileIn = 'settings', fType = 'settings', verbose = True):
    """
    Set paths from settings or path file.

    Parameters
    ----------
    pathType : str, optional, default = 'abs'
        Set for 'rel' or 'abs' paths.
        If rel, the current working dir is assumed to be the base path.

    fileIn : str or path, optional, default = 'settings'
        Settings file to read. Assumed to be in the working dir if no path specified.

    fType : str, optional, default = 'settings'
        If 'settings' use only values *Dir for paths.
        Otherwise assuem ALL values are paths.

    verbose : bool, optional, default = True
        Print output

    Returns
    -------
    paths dictionary


    """

    paths = setPaths()  # Get defaults

    # Read settings file
#     if dirType == 'rel':
#         fileInd = Path(fileIn
#     if not Path(fileIn).is_file():

    if fType == 'settings':
        paths.update({k:v for k,v in dotenv.dotenv_values(dotenv_path = fileIn).items() if k.endswith('Dir')}) # For shared options file
    else:
        paths.update(dotenv.dotenv_values(dotenv_path = fileIn))  # For dedicated file


    # Set defaults for missing paths & output to dict
    if not paths['nbDir']:
        paths['nbDir'] = paths['repoDir']/'nbTemplates'

    if not paths['watchDir']:
        paths['watchDir'] = paths['currDir']

#     {paths[k]:paths['watchDir'] for k in paths.keys() if not paths[k]}
    [paths.update({k:paths['watchDir']}) for k in paths.keys() if not paths[k]]  # Set missing paths = watchDir
    [paths.update({k:Path(paths[k]).expanduser()}) for k in paths.keys() if not isinstance(paths[k],Path)]  # Wrap with Path() & expanduser().


    # Check paths
    for k,v in paths.items():

#         if not v.expanduser().is_dir():
#             print(f"***WARNING: path {k}: {v} not found.")
        if not v.is_dir():
            # Check if paths have been passed by reference
            if v.name in paths.keys():
                paths[k] = paths[v.name]
            else:
                paths[k] = Path('None')  # Set to None or empty?  Note Path('').is_dir() = True however.

            # Set abs if not specified
            if pathType == 'rel':
                paths[k] = paths['currDir']/paths[k]

            # Test again
            if not paths[k].is_dir(): print(f"***WARNING: path {k}: {paths[k]} not found.")

    if verbose:
        print(f"\n*** Got paths from file {fileIn}.")
        [print(k,':\t', v) for k,v in paths.items()]

    return paths

#****************** Polling

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


#***************** Runner

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
