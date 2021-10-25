# Jupyterlab with autonotebook install.
# Based on ePSproc Docker setup, https://github.com/phockett/ePSproc/tree/master/docker
# Uses Jupyter Stacks scipy notebook as base container, https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook

FROM jupyter/scipy-notebook

# Add conda env hook
# COPY ./conda-activate.sh /usr/local/bin/before-notebook.d/

#*** Add ePSproc + dependencies
# Note some may become/are optional
RUN pip install nbconvert, nbformat, pytz, python-dotenv, slackclient, pyngrok

# Note optional @branch here
RUN pip install git+git@github.com/phockett/autonotebook.git
