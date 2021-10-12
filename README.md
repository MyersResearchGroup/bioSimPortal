# bioSimPortal
Flask API to facilitate communication between SBOLCanvas and iBioSim

## Local Testing/Usage
To create the Docker container, navigate to the bioSimPortal directory on your machine and run:

`docker build . -t biosimportal`

Once the build is finished, run:

`docker run -p 5000:5000 biosimportal`

Now HTTP requests can be sent to localhost:5000
