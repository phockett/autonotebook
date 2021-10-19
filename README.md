# autonotebook

 Basic automatic notebook generation from datafiles.

 ## Implemented

 - Slack messaging with `analysis_bot`
 - Dir watch for files & pass to notebook automation with `automaton`
    - Dir watch with basic polling routine.
    - Notebook execution with nbconvert + HTML generation.


 ## To do

- Better Slack integration from `automaton`
  - Nbconvert figure export, see https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html#Using-different-preprocessors
  - Host & serve HTML versions (python simple server + Ngrox)
- Daemonize, see https://pypi.org/project/python-daemon/
- Output & logging.
