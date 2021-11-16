def analysis(tempDir, pathToInFile):
    # Get omex or SED-ML file from the zip
    filePath = ''
    dirToArchive = tempDir

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
    return exec_combine_archive(tempDir, filePath, dirToArchive, argsDict['projectDir'], argsDict['props'], argsDict['initTime'],argsDict['limTime'], argsDict['outTime'], argsDict['pInterval'], argsDict['minStep'],argsDict['maxStep'], argsDict['absErr'], argsDict['relErr'], argsDict['seed'], argsDict['runs'], argsDict['sim'])





def exec_combine_archive(tempDir, archive_file, out_dir, directory, properties, inittime, limtime, outtime, printinterval, minstep, maxstep, abserr, relerr, seed, runs, simulation):
    # Execute the SED tasks defined in a COMBINE archive and save the outputs

    #print(os.path.isfile(archive_file))

    if not os.path.isfile(archive_file):
        print('Wrong file type')
        raise FileNotFoundError("File does not exist: {}".format(archive_file))

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
