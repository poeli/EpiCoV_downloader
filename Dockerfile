FROM continuumio/miniconda3:4.8.2

LABEL developer="Po-E Li"
LABEL email="po-e@lanl.gov"
LABEL version="v21.02.18"
LABEL software="gisaid_downloader"
LABEL tags="covid19, bioinformatics, genome, sars-cov-2, gisaid"

ENV container docker

WORKDIR /opt/conda/bin/
COPY  *.py ./
COPY  *.yml ./

# installing and activating environment
RUN conda env create -f environment.yml
RUN echo "source activate gisaid" > ~/.bashrc
ENV PATH /opt/conda/envs/gisaid/bin:/opt/conda/bin:$PATH

CMD ["/bin/bash"]
