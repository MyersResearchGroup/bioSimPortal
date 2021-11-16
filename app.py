from flask import Flask, request, send_file
from flask.helpers import make_response
from werkzeug.utils import secure_filename
import os, zipfile, tempfile
import sys
import lib

app = Flask(__name__)

# Start API
@app.route('/status', methods=['GET', 'POST'])
def status():
    return("The Download iBioSim Plugin Flask Server is up and running")

# Follow SBH plug-in structure
@app.route('/evaluate', methods=['GET', 'POST'])
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
            archive_url = 'https://subtest.synbiohub.org/download/ECEN5003_ToggleSwitch_LukasBuecherl.omex' #top_level_url + '/archive'
            image = lib.call(archive_url)

            out_name = "iBioSim_Results.png"
            file_out_name = os.path.join(temp_dir.name, out_name)

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
