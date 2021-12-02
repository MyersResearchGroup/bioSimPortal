from flask import Flask, request, redirect, url_for, send_file
from flask.helpers import make_response
from werkzeug.utils import secure_filename
import execute as ex
import os, zipfile, tempfile
import sys
import lib

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

@app.route('/status', methods=['GET', 'POST'])
# Status endpoint to communicate that the plug-in is up and running
def status():
    return("The Download iBioSim Plugin Flask Server is up and running")

# Follow SBH plug-in structure
@app.route('/evaluate', methods=['GET', 'POST'])
# Evaluate endpoint to check if file can be handeled by plug-in
# Plug-in works on archive so the accepted type is Collection
def evaluate():
    data = request.get_json(force=True)
    rdf_type = data['type']

    # ~~~~~~~~~~~~~~~~~ REPLACE THIS SECTION WITH OWN RUN CODE ~~~~~~~~~~~~~~
    # uses rdf types
    accepted_types = {'Collection'}

    acceptable = rdf_type in accepted_types

    # # to ensure it shows up on all pages
    # acceptable = True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~ END SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if acceptable:
        return f'The type sent ({rdf_type}) is an accepted type', 200
    else:
        return f'The type sent ({rdf_type}) is NOT an accepted type', 415

# Expected: Combine archive file, arguments given in request parameters
@app.route('/run', methods=['POST'])
def run():

        #temporary directory to write intermediate files to
        temp_dir = tempfile.TemporaryDirectory()


        data = request.get_json(force=True)

        # Set variables
        top_level_url = data['top_level']
        complete_sbol = data['complete_sbol']
        instance_url = data['instanceUrl']
        genbank_url = data['genbank']
        size = data['size']
        rdf_type = data['type']
        shallow_sbol = data['shallow_sbol']
        url = complete_sbol.replace('/sbol', '')

        try:
            # ~~~~~~~~~~~~~ REPLACE THIS SECTION WITH OWN RUN CODE ~~~~~~~~~~~~~~~
            archive_url = top_level_url + '/archive'

            # calls the function for analysis
            image = lib.call(archive_url)


            out_name = "iBioSim_Results.png"
            file_out_name = os.path.join(temp_dir.name, out_name)

            # Write file in temporary directory
            with open(file_out_name, 'wb') as out_file:
                out_file.write(image)


            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~ END SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            return send_from_directory(temp_dir.name, out_name,
                                    as_attachment=True,
                                    attachment_filename=out_name)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            lnum = exc_tb.tb_lineno
            abort(400, f'Exception is: {e}, exc_type: {exc_type}, exc_obj: {exc_obj}, fname: {fname}, line_number: {lnum}, traceback: {traceback.format_exc()}')
