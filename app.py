from flask import Flask, request, redirect, url_for, send_file
from flask.helpers import make_response
import tempfile, os

import execute as ex

app = Flask(__name__)

# Start API
@app.route('/', methods=["POST, GET"]) 
def default():
    return redirect(url_for('status')) #redirect empty url to status check

@app.route('/analyze', methods=['POST'])
def analyze():
    print('Running analysis!')
    with tempfile.TemporaryDirectory() as tempDir:
        output = ex.exec(request, 'analysis', tempDir)
        if(output == -1):
            return make_response('An error occured during analysis', 202)
        return send_file(output, as_attachment=True, attachment_filename='sim_output.zip')

@app.route('/convert', methods=['POST'])
def convert():
    print('Running conversion!')
    with tempfile.TemporaryDirectory() as tempDir:
        output = ex.exec(request, 'conversion', tempDir)
        if(output == -1):
            return make_response('An error occured during conversion', 202)
        return send_file(output, as_attachment=True, attachment_filename='conv_output.zip')

@app.route('/convert_and_simulate', methods=['POST'])
def conv_and_sim():
    print('Running conversion and analysis!')
    with tempfile.TemporaryDirectory() as tempDir:
        c_output = ex.exec(request, 'both', tempDir)
        if(c_output == ''):
            return make_response('An error occured during conversion', 202)
        # copy topModule file to new working tempDir
        with tempfile.TemporaryDirectory() as aTempDir:
            os.system('cp ' + c_output + ' ' + aTempDir)
            
            topMod = os.listdir(aTempDir)[0]
            pathToTopMod = os.path.join(aTempDir, topMod)

            output = ex.analysis(aTempDir, ex.args.getArgs(), pathToTopMod)
            return send_file(output, as_attachment=True, attachment_filename='sim_output.zip')


# Follow SBH plug-in structure
@app.route('/status', methods=['GET', 'POST'])
def status():
    # This could be a more complicated check to see if dependencies are online
    return('online')

@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    return('Evaluate')

# Expected: Combine archive file, arguments given in request parameters
@app.route('/run', methods=['POST'])
def run():  
    return()