from flask import Flask, request, send_file
from flask.helpers import make_response
from werkzeug.utils import secure_filename
import requests
import os, zipfile, tempfile

# Function for the analysis
def analysis(url: str, dest_path: str):
    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_path, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

    # Command to run the analysis using iBioSim
    cmd = r"java -jar iBioSim/analysis/target/iBioSim-analysis-3.1.0-SNAPSHOT-jar-with-dependencies.jar "
    print("Running: " + cmd + file_path)
    # Running the command
    os.system(cmd + file_path)

    print('Running ls')
    name = filename.replace('.omex','')
    nP = file_path[:file_path.rfind('/')] + '/' + name
    os.system('ls ' + nP)

    # Find the image of the results
    for file in os.listdir(nP):
        if file.endswith(".png"):
            image = os.path.join(nP, file)

    print(image)

    # Return the image
    return image

def call(archive_url):

    # Save file locally
    with tempfile.TemporaryDirectory() as tempDir:
        return analysis(archive_url, tempDir)
