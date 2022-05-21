FROM geneticlogiclab/ibiosim:snapshot

LABEL base_image="geneticlogiclab/ibiosim"
LABEL version="1.0.0"
LABEL software="bioSimAPI"
LABEL software.version="1.0.0"
LABEL about.summary="API for SBOLCanvas/SynBioHub communication with iBioSim"
LABEL about.home="https://github.com/MyersResearchGroup/iBioSim"
LABEL about.documentation="https://github.com/MyersResearchGroup/iBioSim"
LABEL about.license_file="https://github.com/MyersResearchGroup/iBioSim/blob/master/LICENSE.txt"
LABEL about.license="Apache-2.0"
LABEL about.tags="kinetic modeling,dynamical simulation,systems biology,biochemical networks,SBML,SED-ML,COMBINE,OMEX,BioSimulators"
LABEL maintainer="Chris Myers <chris.myers@colorado.edu>"

# Install requirements
RUN apt-get update --fix-missing \
	&& DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y unzip
	
COPY . .

RUN pip3 install -r requirements.txt


ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENTRYPOINT FLASK_APP=/app.py flask run --host=0.0.0.0
