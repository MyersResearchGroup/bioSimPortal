# Get cmd line arguments from HTTP request parameters
# NOTE: -o argument is not needed for analysis or conversion on Dockerized version of this app

url = 'https://subtest.synbiohub.org/download/ECEN5003_ToggleSwitch_LukasBuecherl.omex'


def exec_combine_archive(tempDir, archive_file, out_dir, directory, properties, inittime, limtime, outtime, printinterval, minstep, maxstep, abserr, relerr, seed, runs, simulation):
    # Execute the SED tasks defined in a COMBINE archive and save the outputs

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
    recursiveZipOutputFiles(tempDir, z)
    return pathToZip

def recursiveZipOutputFiles(path, zipf):
    for f in os.listdir(path):
        p = os.path.join(path, f)
        if os.path.isdir(p):
            recursiveZipOutputFiles(p, zipf)
        elif not p.endswith('.zip'):
            zipf.write(p)

def analysis(tempDir, argsDict, pathToInFile):
    # Get omex or SED-ML file from the zip
    filePath = ''
    dirToArchive = tempDir
    if(pathToInFile.endswith('.zip')):
        dirToArchive = os.path.join(tempDir, 'combine_archive')
        os.makedirs(dirToArchive)
        print('')
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

    print('')
    print('Done. Extracted file to: ' + filePath.__str__())
    return exec_combine_archive(tempDir, filePath, dirToArchive, argsDict['projectDir'], argsDict['props'], argsDict['initTime'],argsDict['limTime'], argsDict['outTime'], argsDict['pInterval'], argsDict['minStep'],argsDict['maxStep'], argsDict['absErr'], argsDict['relErr'], argsDict['seed'], argsDict['runs'], argsDict['sim'])



def caller(archive_url, output_filename):

  argsDict = {
      # Argument for: should the API run analysis, conversion, or conversion and then analysis
      'runType': request.args.get('execute'),

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
      'sim': request.args.get('simulation')
  }

  # Sanitize parameters
  for key in argsDict:
      if not argsDict[key] == None:
          argsDict[key] = str(argsDict[key])

  # Get archive file from HTTP request body
  f = None
  if not 'file' in request.files:
      print('Error: Expected input file, none found')
      return(make_response('Error: Expected input file, none found', 202))
  f = request.files['file']

  run_type = argsDict['runType']

  # Save file locally
  with tempfile.TemporaryDirectory() as tempDir:
      pathToInFile = os.path.join(tempDir, secure_filename(f.filename))
      #print('pathToInFile')
      #print(pathToInFile)
      f.save(pathToInFile)

      output = None

      os.environ["BIOSIM"] = r"/iBioSim"
      os.environ["PATH"] = os.environ["BIOSIM"]+r"/bin:"+os.environ["BIOSIM"]+r"/lib:"+os.environ["PATH"]
      os.environ["LD_LIBRARY_PATH"] = os.environ["BIOSIM"] + r"/lib:"

      print('')
      print('Running analysis!')
      output = analysis(tempDir, argsDict, pathToInFile)

      #print('Working Directory')
      #print(os.getcwd())

      return send_file(output, as_attachment=True, attachment_filename=output_filename)
