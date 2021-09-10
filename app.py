from flask import Flask, request, send_file
from flask.helpers import make_response
from werkzeug.utils import secure_filename
import os, zipfile, tempfile

app = Flask(__name__)

# From Biosimulators_iBioSim
__all__ = ['exec_combine_archive']

def exec_combine_archive(tempDir, archive_file, out_dir, directory, properties, inittime, limtime, outtime, printinterval, minstep, maxstep, abserr, relerr, seed, runs, simulation):
    """ Execute the SED tasks defined in a COMBINE archive and save the outputs

    Args:
        archive_file (:obj:`str`): path to COMBINE archive
        out_dir (:obj:`str`): directory to store the outputs of the tasks
    """
    #print(os.path.isfile(archive_file))
    #localDirForTesting = r"/home/tom-stoughton"
    os.environ["BIOSIM"] = r"/iBioSim"
    os.environ["PATH"] = os.environ["BIOSIM"]+r"/bin:"+os.environ["BIOSIM"]+r"/lib:"+os.environ["PATH"]
    os.environ["LD_LIBRARY_PATH"] = os.environ["BIOSIM"] + r"/lib:"
    
    if not os.path.isfile(archive_file):
        print('Wrong file type')
        raise FileNotFoundError("File does not exist: {}".format(archive_file))
    
    #cmd = r"java -jar 'C:/Users/Tom Stoughton/iBioSim/iBioSim-win64/bin/iBioSim'" #hode sim is java based
    cmd = r"java -jar iBioSim/analysis/target/iBioSim-analysis-3.1.0-SNAPSHOT-jar-with-dependencies.jar "
    if not directory == None:
        cmd += "-d " + directory + " "
    if not properties == None:
        cmd += "-p " + properties + " "
    if not inittime == None:
        cmd += "-ti " + inittime + " "
    if not limtime == None:
        cmd += "-tl " + limtime + " "
    if not outtime == None:
        cmd += "-ot " + outtime + " "
    if not printinterval == None:
        cmd += "-pi " + printinterval + " "
    if not minstep == None:
        cmd += "-m0 " + minstep + " "
    if not maxstep == None:
        cmd += "-m1 " + maxstep + " "
    if not abserr == None:
        cmd += "-aErr " + abserr + " "
    if not relerr == None:
        cmd += "-sErr " + relerr + " "
    if not seed == None:
        cmd += "-sd " + seed + " "
    if not runs == None:
        cmd += "-r " + runs + " "
    if not simulation == None:
        cmd += "-sim "  + simulation + " "
    #print("command: " + cmd + " '" + archive_file + "'")
    os.system(cmd + " '" + archive_file + "'")

    # Put output files into zipfile 
    pathToZip = os.path.join(tempDir,"out.zip")
    z = zipfile.ZipFile(pathToZip, "w")
    if out_dir == None:
        out_dir = '.'
    recursiveZipOutputFiles(out_dir, z)

    return pathToZip

def recursiveZipOutputFiles(path, zipf):
    for f in os.listdir(path):
        p = os.path.join(path, f)
        if os.path.isdir(p):
            recursiveZipOutputFiles(p, zipf)
        else:
            zipf.write(p)

# Start API
@app.route("/status")
def status():
    # This could be a more complicated check to see if dependencies are online
    return("online")

# Expected: Combine archive file, arguments given in request parameters
@app.route("/run", methods=["POST"])
def run():
    # Get cmd line arguments from HTTP request parameters
    # NOTE: out_dir argument is not needed on Dockerized version of this app
    argsDict = {
        'projectDir': request.args.get('directory'),
        'props': request.args.get('properties'),
        'initTime': request.args.get('init_time'),
        'limTime': request.args.get('lim_time'),
        'outTime': request.args.get('out_time'),
        'pInterval': request.args.get('print_interval'),
        'minStep': request.args.get('min_step'),
        'maxStep': request.args.get('max_step'),
        'absErr': request.args.get('abs_err'),
        'relErr': request.args.get('rel_err'),
        'seed': request.args.get('seed'),
        'runs': request.args.get('runs'),
        'sim': request.args.get('simulation')
    }

    # Sanitize path arguments for exec_combine_archive method
    for key in argsDict:
        if not argsDict[key] == None:
            argsDict[key] = str(argsDict[key]).replace('-','/')
        

    # Get archive file from HTTP request body
    f = None
    if not 'file' in request.files:
        return(make_response('Error: Expected input combine archive, none found', 202))
    f = request.files['file']

    # Save file locally
    with tempfile.TemporaryDirectory() as tempDir:
        pathToInFile = os.path.join(tempDir, secure_filename(f.filename))
        f.save(pathToInFile)

        # Extract zip file contents and find omex file
        if pathToInFile.endswith('.zip'):
            dirToArchive = os.path.join(tempDir, 'combine_archive')
            os.makedirs(dirToArchive)
            print('Extracting from zip...')
            with zipfile.ZipFile(pathToInFile, 'r') as ca:
                ca.extractall(dirToArchive)
            
            path_to_omex = None
            path_to_sedml = None
            
            for filename in os.listdir(dirToArchive):
                file = os.path.join(dirToArchive, filename)
                if file.endswith('.omex'):
                    path_to_omex = file
                    break
                if file.endswith('.sedml'):
                    path_to_sedml = file
                    break
            filePath = path_to_omex
            if path_to_omex == None:
                filePath = path_to_sedml
                if path_to_sedml == None:
                    print('Error: Failed to locate OMEX or SED-ML file in directory.')
                    return(make_response('Error: Missing omex/sedml file', 202))
            
            print('Done. Extracted file to: ' + filePath.__str__())
            
        output = exec_combine_archive(tempDir, filePath, dirToArchive, argsDict['projectDir'], argsDict['props'], argsDict['initTime'],argsDict['limTime'], argsDict['outTime'], argsDict['pInterval'], argsDict['minStep'],argsDict['maxStep'], argsDict['absErr'], argsDict['relErr'], argsDict['seed'], argsDict['runs'], argsDict['sim'])
        return send_file(output, as_attachment=True, attachment_filename='output.zip')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)