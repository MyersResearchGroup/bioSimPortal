# bioSimPortal
Flask API to facilitate communication between SBOLCanvas and iBioSim

## Local Testing/Usage
To create the Docker container, navigate to the bioSimPortal directory on your machine and run:

`docker build . -t biosimportal`

Once the build is finished, run:

`docker run -p 5000:5000 biosimportal`

Now HTTP requests can be sent to localhost:5000

# HTTP Post Request Parameters (Postman)

When sending a POST request to the app, parameters for simulation or conversion are required in the query parameters of the request.
Without these parameters, iBioSim won't have any arguments to run the conversion or analysis jar files with, so it will likely error out (with the exception of running analysis on a COMBINE Archive).

## Analysis (For COMBINE Archives)

In Postman, attach a COMBINE Archive with a .zip extension to the body of the request, and send the request to:

`http://localhost:5000/analyze`

--------------------------------

## Analysis (For SBML files)

Attach the SBML file ending with 'topModule.xml' to the body of the request, and put the following in the request field:

`http://localhost:5000/analyze`

Then under the Params tab using the Key-Value Edit, add (at minimum) arguments for the simulation type, number of runs, and time limit for the simulation.

Argument Keys and Values should be in the following form:

| Key Name        |  Value  | Description | Corresponding Flag |
| -------------   | ------------- | -------------   | ------------- |
| directory | path-to-project-directory | project directory | -d |
| properties | path-to-properties-file | loads a properties file | -p |
| init_time | number (usually 0) | non-negative double initial simulation time | -ti |
| lim_time | number | non-negative double simulation time limit | -tl |
| out_time | number | non-negative double output time | -ot |
| print_interval | number | positive double for print interval | -pi |
| min_step | number | positive double for minimum step time | -m0 |
| max_step | number | positive double for maximum step time | -m1 |
| abs_err | number | positive double for absolute error | -aErr |
| rel_err | number | positive double for relative error | -sErr |
| seed | number | long for random seed | -sd |
| runs | number | positive integer for number of runs | -r |
| simulation | ode, hode, ssa, hssa, dfba, jode, jssa. | simulation type | -sim |

- Note: any paths in either the 'directory' or 'properties' values should have every "/" replaced with "-".

--------------------------------

## Conversion

Attach the file to be converted in the body of the request, and put the following in the request field:

`http://localhost:5000/convert`

Argument Keys and Values should be in the following form:

| Key Name        |  Value  | Description | Corresponding Flag |
| -------------   | ------------- | -------------   | ------------- |
| best_practices | (leave empty) | check best practices | -b |
| results_file | (leave empty) | the name of the file that will be produced to hold the result of the second SBOL file, if SBOL file diff was selected | -cf |
| display_error_trace | (leave empty) | display detailed error trace | -d |
| second_SBOL_file | (leave empty) | the second SBOL file to compare to the main SBOL file | -e |
| export_single_file | (leave empty) | export SBML hierarchical models in a single output file | -esf |
| cont_first_error | (leave empty) | continue after first error | -f |
| allow_incomplete | (leave empty) | allow SBOL document to be incomplete | -i |
| language | SBOL1, SBOL2, GenBank, FASTA, SBML | specifies language for output (default=SBOL2). To output FASTA or GenBank, no SBOL default URI prefix is needed. | -l |
| main_file_name | file_name.xml | The name of the file that will be produced to hold the result of the main SBOL file, if SBOL file diff was selected | -mf |
| allow_noncompliant_uri | (leave empty) | allow non-compliant URIs | -n |
| no_output | (leave empty) | indicate no output file to be generated from validation. Instead, print result to console/command line. | -no |
| prefix | `<URIPrefix>` | default URI prefix to set an SBOLDocument | -p |
| sbml_ref | full-path-to-SBML | The full path of external SBML files to be referenced in the SBML2SBOL conversion | -rsbml |
| sbol_ref | full-path-to-SBOL | The full path of external SBOL files to be referenced in the SBML2SBOL conversion | -rsbol |
| select | `<topLevelURI>` | select only this object and those it references | -s |
| types_in_uri | (leave empty) | uses types in URIs | -t |
| mark_version | number | mark version of data objects created during conversion | -v |
| repository | "https://www.link-to-repository.dummy" | The specified synbiohub repository the user wants VPR model generator to connect to | -r |
| environment | full-path-to-SBML-env-file | is the complete directory path of the environmental file to instantiate to your model. This only works when VPR model generator is used | -env |
| cello | (leave empty) | This option is for dynamic modeling of Cello parts and parametrization | -Cello |

- Note: When the value of an argument's field is left blank, that key should still be checked if it needs to be included in the request.

--------------------------------

## Conversion and Analysis

Attach the SBOL file in the body of the request, and put the following in the request field:

`http://localhost:5000/convert_and_simulate`

Argument key-value pairs follow the previously specified formats. Any and all arguments for conversion or analysis go into the query for this request.

--------------------------------

# Plug-in Endpoints

*Plug-in endpoint information*

## Status

## Evaluate

## Run
