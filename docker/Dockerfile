# Jupyterlab with autonotebook install.
# Based on ePSproc Docker setup, https://github.com/phockett/ePSproc/tree/master/docker
# Uses Jupyter Stacks scipy notebook as base container, https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook

FROM jupyter/scipy-notebook

# Add conda env hook
# COPY ./conda-activate.sh /usr/local/bin/before-notebook.d/

#*** Add ePSproc + dependencies
# Note some may become/are optional
RUN pip install nbconvert nbformat pytz python-dotenv slackclient pyngrok

# Note optional @branch here
RUN git clone https://github.com/phockett/autonotebook.git

# Copy local files to container.
COPY settingsDemoDocker .

# Init ngrok - this gives issues with `docker-compose` otherwise (although OK with `docker run`)
# Edit: seems to be networking/port-mapping issue with docker-compose, not sure why as yet.
COPY testPyngrok.py .
RUN python testPyngrok.py
