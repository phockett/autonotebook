# autonotebook

 Basic automatic notebook generation from datafiles: watch a dir, trigger notebook builds on new data, serve and post the results to Slack.

## Installation

Currently only importable as a local demo package... run `git clone https://github.com/phockett/autonotebook.git` to grab it.

Requires the following non-standard libs (all pip-installable):

- Notebook execution: nbconvert, nbformat
- Timezones: pytz
- Settings files: python-dotenv
- Slack: slackclient

Coming soon: proper installer & Docker version.


## Usage

For a [quick demo, see the demo notebook.](https://github.com/phockett/autonotebook/blob/main/demo/automaton_demo_241021.ipynb)


### Templates

For templates, see [the nbTemplates dir](https://github.com/phockett/autonotebook/tree/main/nbTemplates).

In general, only the following lines are required to make a notebook compatible, to grab the datafile passed from the triggering event:

```
import os

dataFile = os.environ.get('DATAFILE', '')
```

Which will get the datafile into the template notebook.

Note that for use with [nb_conda_kernels some additional setup may be required for nbconvert](https://github.com/Anaconda-Platform/nb_conda_kernels#use-with-nbconvert-voila-papermill).


## Implemented

- Slack messaging with `analysis_bot`

- Dir watch for files & pass to notebook automation with `automaton`
  - Dir watch with basic polling routine.
  - Notebook execution with nbconvert + HTML generation.
  - Settings file for paths and options.  


- Event triggering.
  - Currently supports .h5 and .html files.
  - On .h5 (data file) automatically process using template notebook, including export to HTML.
  - On HTML file, post to Slack (if using) and generate URL (if serving).


- Host & serve HTML versions (python simple server + Ngrok)
  - [Nbconvert figure export](https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html#Using-different-preprocessors)
  - Python http.server for serving.
  - [(py)Ngrok for local server access.](https://pyngrok.readthedocs.io/en/latest/integrations.html#python-http-server) (May require setup on first use.)


- Settings file. See [demo for minimal example](https://github.com/phockett/autonotebook/blob/main/demo/settingsDemo).
  - Define watch path & output path(s) (optional).
  - Define notebook template.
  - Turn integrations on/off and set additional options.
  - File is checked upon each event trigger to allow for template file updates while watching.



 ## To do

- Better Slack integration from `automaton` (message types & formatting)
- Daemonize, see https://pypi.org/project/python-daemon/
- Output & logging.
- Preproc notebook
  - Figure output from HTML (as above).
  - Calibration parameters?
  - Rerun notebooks with different parameters?
