# autonotebook

 Basic automatic notebook generation from datafiles.

 For a [quick demo, see the demo notebook.](https://github.com/phockett/autonotebook/blob/main/demo/automaton_demo_241021.ipynb)

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
