# autonotebook + JupyterLab builds with Docker

Dockerfiles for autonotebook, based on [Jupyter Docker Stacks images](https://jupyter-docker-stacks.readthedocs.io/en/latest/index.html), are in `/docker`.


## Quick build

Quick build container only:

```
docker build -t autonotebook .
```

Note the Jupyter Docker Stacks container runs a Jupyter server by default. Use the start script to run a different process, e.g. `docker run -it --rm autonotebook start.sh ipython` or `docker run -it --rm autonotebook start.sh bash`. See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#start-sh

Run with default demo settings, note this assumes that:
- watchDir (on host) = $(pwd)/data
- port=8080 set in settingsDemoDocker

```
docker run -p 9056:8080 -v "$(pwd)/data:/data" -it --rm autonotebook start.sh python autonotebook/automaton/autoProc.py settingsDemoDocker
```

Run with alternate settings:
To pass/use a different settings file (and allow for updating), put it in the data dir, then run

```
docker run -p 9056:8080 -v "$(pwd)/data:/data" -it --rm autonotebook start.sh python autonotebook/automaton/autoProc.py /data/settings
```


## With Docker-compose

For more control, try docker-compose

Settings: can either be copied or mapped into the container, or passed via Docker.

```
docker-compose up --env-file settingsDemoDocker
```

NOTE: this is currently working for processing only, but has network connection issues.
For Ngrok, see https://github.com/shkoliar/docker-ngrok/blob/master/Dockerfile
