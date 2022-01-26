from flask.helpers import make_response
from werkzeug.utils import secure_filename
import os, zipfile, tempfile

class argData:
    def __init__(self):
        self.argsDict = {}

    def setArgs(self, dict):
        self.argsDict = dict

    def getArgs(self):
        return self.argsDict

args = argData()


def analysis(tempDir, argsDict, pathToInFile):
    # Get omex or SED-ML file from the zip
    filePath = ''
    dirToArchive = tempDir
    if(pathToInFile.endswith('.zip')):
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
        # send OMEX, SED-ML, or topModule SBML file to iBioSim
        filePath = path_to_omex
        if path_to_omex == None:
            filePath = path_to_sedml
            if path_to_sedml == None:
                print('Error: Failed to locate OMEX or SED-ML file in directory.')
                return(make_response('Error: Missing omex/sedml file from combine archive', 202))
        print('Done. Extracted file to: ' + filePath.__str__())

    # otherwise, the input file was the top module SBML, so check for all the proper arguments to run the first-time simulation
    else:
        filePath = pathToInFile
        # check for args
        if argsDict['sim'] == None:
            print('No simulation type given, defaulting to jode')
            argsDict['sim'] = 'jode'
        if argsDict['limTime'] == None:
            print('No time limit given, defaulting to 250')
            argsDict['limTime'] = '250'
        if argsDict['runs'] == None:
            print('No run count given, defaulting to 1')
            argsDict['runs'] = '1'

    return exec_analysis_jar(tempDir, filePath, dirToArchive, argsDict['projectDir'], argsDict['props'], argsDict['initTime'],argsDict['limTime'], argsDict['outTime'], argsDict['pInterval'], argsDict['minStep'],argsDict['maxStep'], argsDict['absErr'], argsDict['relErr'], argsDict['seed'], argsDict['runs'], argsDict['sim'])

def conversion(tempDir, argsDict, pathToInFile, package):
    # call conversion jar with arguments from HTTP request
    return exec_conversion_jar(tempDir, pathToInFile, package, argsDict['b'], argsDict['cf'], argsDict['d'], argsDict['e'], argsDict['esf'], argsDict['f'], argsDict['i'], argsDict['l'], argsDict['mf'], argsDict['n'], argsDict['no'], argsDict['oDir'], argsDict['p'], argsDict['rsbml'], argsDict['rsbol'], argsDict['s'], argsDict['t'], argsDict['v'], argsDict['r'], argsDict['env'], argsDict['Cello'])

# Adapted from Biosimulators_iBioSim
def exec_analysis_jar(tempDir, archive_file, out_dir, directory, properties, inittime, limtime, outtime, printinterval, minstep, maxstep, abserr, relerr, seed, runs, simulation):
    # Execute the SED tasks defined in a COMBINE archive and save the outputs

    #print(os.path.isfile(archive_file))

    if not os.path.isfile(archive_file):
        print('Wrong file type')
        raise FileNotFoundError("File does not exist: {}".format(archive_file))

    cmd = r"java -jar iBioSim/analysis/target/iBioSim-analysis-3.1.0-SNAPSHOT-jar-with-dependencies.jar " #hode sim is java based
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

    print("Running: " + cmd + archive_file)

    os.system(cmd + archive_file)

    # Put output files into zipfile
    print('Analysis complete, collecting output!')
    pathToZip = os.path.join(tempDir,'out.zip')
    z = zipfile.ZipFile(pathToZip, 'w')
    if out_dir == None:
        out_dir = '.'
    recursiveZipOutputFiles(out_dir, z)

    return pathToZip

def exec_conversion_jar(tempDir, sbolFile, package, b, cf, d, e, esf, f, i, l, mf, n, no, oDir, p, rsbml, rsbol, s, t, v, r, env, Cello):
    # Execute the conversion jar on the inputted SBOL file

    if not os.path.isfile(sbolFile):
        print('Wrong file type')
        raise FileNotFoundError("File does not exist: {}".format(sbolFile))

    outputDir = ''

    cmd = r"java -jar iBioSim/conversion/target/iBioSim-conversion-3.1.0-SNAPSHOT-jar-with-dependencies.jar "
    # add args to command
    if not b == None:
        cmd += '-b ' + b + ' '
    if not cf == None:
        cmd += '-cf ' + cf + ' '
    if not d == None:
        cmd += '-d ' + d + ' '
    if not e == None:
        cmd += '-e ' + e + ' '
    if not esf == None:
        cmd += '-esf ' + esf + ' '
    if not f == None:
        cmd += '-f ' + f + ' '
    if not i == None:
        cmd += '-i '
    if not l == None:
        cmd += '-l ' + l + ' '
    if not mf == None:
        cmd += '-mf ' + mf + ' '
    if not n == None:
        cmd += '-n ' + n + ' '
    if not oDir == None:
        cmd += '-oDir ' + oDir + ' '
    if not p == None:
        cmd += '-p ' + p + ' '
    if not rsbml == None:
        cmd += '-rsbml ' + rsbml + ' '
    if not rsbol == None:
        cmd += '-rsbol ' + rsbol + ' '
    if not s == None:
        cmd += '-s ' + s + ' '
    if not t == None:
        cmd += '-t ' + t + ' '
    if not v == None:
        cmd += '-v ' + v + ' '
    if not r == None:
        cmd += '-r ' + r + ' '
    if not env == None:
        cmd += '-env ' + env + ' '
    if not Cello == None:
        cmd += '-Cello '
    if not no == None:
        cmd += '-no '
    else:
        outputDir = os.path.join(tempDir,'modules/')
        os.system('mkdir ' + outputDir)
        cmd += '-o ' + outputDir + 'collection.xml '

    print("Running: " + cmd + sbolFile)

    os.system(cmd + sbolFile)
    print('Conversion complete, collecting output!')
    if package:
        print('Collecting to zip...')
        pathToZip = os.path.join(tempDir,'out.zip')
        z = zipfile.ZipFile(pathToZip, 'w')
        recursiveZipOutputFiles(tempDir, z)
        return pathToZip
    else:
        print('Returning topModule file')
        for f in os.listdir(outputDir):
            if f.endswith('topModule.xml'):
                return os.path.join(outputDir, f)
        return ''


def exec(request, type, tempDir):
    # Get cmd line arguments from HTTP request parameters
    # NOTE: -o argument is not needed for analysis or conversion on Dockerized version of this app
    d = {
        # Analysis arguments
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
        'sim': request.args.get('simulation'),

        # Conversion arguments
        'b': request.args.get('best_practices'),
        'cf': request.args.get('results_file'),
        'd': request.args.get('display_error_trace'),
        'e': request.args.get('second_SBOL_file'),
        'esf': request.args.get('export_single_file'),
        'f': request.args.get('cont_first_error'),
        'i': request.args.get('allow_incomplete'),
        'l': request.args.get('language'),
        'mf': request.args.get('main_file_name'),
        'n': request.args.get('allow_noncompliant_uri'),
        'o': request.args.get('output_path'),
        'no': request.args.get('no_output'),
        'oDir': request.args.get('output_dir'),
        'p': request.args.get('prefix'),
        'rsbml': request.args.get('sbml_ref'),
        'rsbol': request.args.get('sbol_ref'),
        's': request.args.get('select'),
        't': request.args.get('types_in_uri'),
        'v': request.args.get('mark_version'),
        'r': request.args.get('repository'),
        'env': request.args.get('environment'),
        'Cello': request.args.get('cello')
    }

    args.setArgs(d)
    argsDict = args.getArgs()

    # Sanitize parameters
    for key in argsDict:
        if not argsDict[key] == None:
            argsDict[key] = str(argsDict[key])

    # Get archive file from HTTP request body
    f = None
    if not 'file' in request.files:
        # print(request.files)
        print('Error: Expected input file, none found')
        return(make_response('Error: Expected input file, none found', 202))
    f = request.files['file']

    # Save file locally

    pathToInFile = os.path.join(tempDir, secure_filename(f.filename))
    f.save(pathToInFile)

    output = None

    os.environ["BIOSIM"] = r"/iBioSim"
    os.environ["PATH"] = os.environ["BIOSIM"]+r"/bin:"+os.environ["BIOSIM"]+r"/lib:"+os.environ["PATH"]
    os.environ["LD_LIBRARY_PATH"] = os.environ["BIOSIM"] + r"/lib:"

    if type == 'conversion' or type == 'both':
        # run conversion
        p = True
        if type == 'both':
            p = False
        output = conversion(tempDir, argsDict, pathToInFile, p)
        return output
    elif type == 'analysis':
        # run analysis
        output = analysis(tempDir, argsDict, pathToInFile)
        return output


def recursiveZipOutputFiles(path, zipf):
    for f in os.listdir(path):
        p = os.path.join(path, f)
        if os.path.isdir(p):
            recursiveZipOutputFiles(p, zipf)
        elif not p.endswith('.zip'):
            zipf.write(p)
