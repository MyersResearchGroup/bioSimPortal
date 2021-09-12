# bioSimPortal
Flask API to facilitate communication between SBOLCanvas and iBioSim

## Local Testing/Usage
To create the Docker container, navigate to the bioSimPortal directory on your machine and run:

`docker build . -t biosimportal`

Once the build is finished, run:

`docker run -p 8080:5000 biosimportal`
