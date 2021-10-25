# autonotebook + JupyterLab builds with Docker

Dockerfiles for autonotebook, based on [Jupyter Docker Stacks images](https://jupyter-docker-stacks.readthedocs.io/en/latest/index.html), are in `/docker`.


Quick build container only:

```
docker build -t autonotebook .
```

Run:

```
docker run -p 9866:8888 autonotebook
```

Note this runs a Jupyter server by default. Use the start script to run a different process, e.g. `docker run -it --rm autonotebook start.sh ipython` or `docker run -it --rm autonotebook start.sh bash`. See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#start-sh

docker run -it --rm autonotebook start.sh python autonotebook/automaton/autoProc.py

Settings: can either be copied or mapped into the container, or passed via Docker.

--env-file
