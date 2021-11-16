from flask import Flask, request, send_file
from flask.helpers import make_response
from werkzeug.utils import secure_filename
import requests
import os, zipfile, tempfile

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

    cmd = r"java -jar iBioSim/analysis/target/iBioSim-analysis-3.1.0-SNAPSHOT-jar-with-dependencies.jar "
    print("Running: " + cmd + file_path)
    os.system(cmd + file_path)

    print('Running ls')
    name = filename.replace('.omex','')
    nP = file_path[:file_path.rfind('/')] + '/' + name
    os.system('ls ' + nP)

    for file in os.listdir(nP):
        if file.endswith(".png"):
            image = os.path.join(nP, file)

    print(image)

    return image

    #send_file(image, as_attachment=True, attachment_filename='Test.png')

def call(archive_url):

    # Save file locally
    with tempfile.TemporaryDirectory() as tempDir:
        return analysis(archive_url, tempDir)
