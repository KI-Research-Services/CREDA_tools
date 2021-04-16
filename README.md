# CREDA Tools

This repository contains the primary code base for the [CREDA Project](https://kenaninstitute.unc.edu/publication/commercial-real-estate-data-towards-parity-with-other-asset-classes-a-report-on-the-progress-of-the-commercial-real-estate-data-alliance-creda/) at UNC's [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/). This code is specifically meant to take various commercial real estate data sources, identifying properties by addresses, to joining datasets via DOE UBIDs.

## CREDA Mission Statement

The Commercial Real Estate Data Alliance is a consortium of academics dedicated to achieving data parity with other major asset classes. Specifically, we believe that improved access to and understanding of available data in commercial real estate is key to fostering higher quality research and interactions between academia and industry, to the benefit of the entire CRE community.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

CREDA_tools is built in Python, so a Python installation will be needed. Basic CREDA_tools has fairly lightweight requirements, but will require a few extra libraries depending on functions used. Requirements include:

* Numpy
* Pandas
* Shapely
* buildingid from the Department of Energy. Instructions for this installation can be found at [their GitHub Repository](https://github.com/pnnl/buildingid-py).
* censusgeocode is needed to use the Census Geocoder. Run with 'pip install censusgeocode'

### Installing

As this goes public, we would like to transition to a pip install of CREDA_tools as well. In the meantime, we recommend cloning/downloading the repository such that CREDA_tools is a subdirectory in the root folder you wish to run projects in.

NOTE: Besides installation, you will also need a .ini file and a 'temp_files' folder in your working directory. A .ini sample file can be copied out of the CREDA_tools main directory.


<!--- ## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```
-->

## Basic Usage

The tools in this package are organized around various useful tasks encountered when attempting to map addresses to a spatial identifier. A spatial identifier is a reference to a unique geometry in a standardized grid. For instance, a polygon in the Google Open Location Code grid. The reference can also be to a polyhedron in a 3D grid. Currently, we employ the spatial reference approach pioneered by the US Department of Energy (DOE) through their Unique Building Identifier (UBID) project linked above.

### Instantiation
Once you have a root folder with CREDA_tools inside it, we can begin a task or sequence of tasks. First, one must import the tool library (do this from within the top CREDA_tools directory):
```
from CREDA_tools import helper
```

Instantiatiation of a CREDA_Project object with a data file takes the following form (sample files demonstrating various tasks have been provided in the /test_data directory). 
```
project = helper.CREDA_Project(<task_type>, <in_file>)
```

* Parsing a string containing multiple addresses into an expanded list of street addresses that can be geocoded.
  * <task_type> = "addresses"  
  * <in_file> is the name of a (CSV) file (placed in quotes) with required data fields 'addr', 'city', 'postal', and 'state'. Auxiliary data columns are permitted. 
  * Note that the 'addr' field can contain multiple street addresses (e.g., the single string "140 Main St., 20-52 Ford Ave., 67 & 122 Glenn Dr.").
* Associating geocodes with geospatial polygons that the geocodes ``pierce''.
  * <task_type> = "geocodes"  
  * <in_file> is the name of a (CSV) file (placed in quotes) with required data fields 'lat', 'long', and 'confidence'. Auxiliary data columns are permitted. 
  * The confidence field is a number between 0 and 1 that scores the confidence associated with the geocoded data. When geocoding addresses, greater confidence should be associated with a returned geocode if it corresponds to a rooftop geocode rather than a zip code centroid. The confidence level is assumed to be assigned by the user (it is subjective) based on their knowledge/experience with the geocoder(s) used.
  * If a non-unique 'TempID' field is included, then it can be used to refer to user-defined groupings of geocodes. This may happen when a record in a dataset is associated with multiple geocodes (e.g., multiple addresses, structures, or properties).  
* Assigning a spatial identifier to each shape in a list. 
  * <task_type> = "parcels"  
  * <in_file> is the name of a (CSV) file (placed in quotes) with required data field 'GEOM' containing WKT strings. At this point, the only WKT strings that can be processed are
    * POLYGON
    * MULTIPOLYGON
    * GEOMETRYCOLLECTION containing either POLYGON or MULTIPOLYGON shapes
  * If a non-unique 'ShapeID' field is provided, then it can be used to refer to user-defined groupings of shapes. This may happen, for instance, when multiple shapes are related (e.g., a multi-parcel property).   

Once a project has been instantiated, several function can be applied to the created object to achieve the desired result (e.g., cleaning addresses, associating geocodes with shapes, etc.). In what follows, we provide details on each of the main tasks described above. 

## Addresses list expansion

In many commercial real estate data sets, the address field for a "property" record contains items such as "1650 - 1750 S. Babcock Avenue" or "1610-1650 Bienvenue Road", each of which refers to a _list_ of addresses rather than a single address. When linking or merging data sets, or simply looking for related records within the same data set (e.g., repeat sales transactions), it seems useful to allow for partial overlap. For instance, a record referring to "1650 - 1750 S. Babcock Avenue" might have some relationship to one referring to "1700 S. Babcock Avenue". The tool we developed and describe in this section are meant for expanding such address references into address lists. We are not aware of the availability of similar tools. 

At this point, the tool creates a list from compounded street addresses that use one or more of the following conjunctions and delimiters (not case sensitive): "and", "&", "/", "\\", "-", ";", ",". Some examples of compound addresses are found in _san_jose_d1.csv_, available in the _CREDA_tools/test_data_ directory. The following sequence of commands expands this file into a list of addresses (please remember to work in the top CREDA_tools directory). 

```
from CREDA_tools import helper
project = helper.CREDA_Project("addresses", "test_data/san_jose_d1.csv")
project.clean_addresses()
project.addr_parse_report("report_san_jose_d1.csv")
```
As described earlier, the first command imports the project tools. The second instantiates a "project" object that contains the address file. The object _project_ assigns a sequential unique internal identifier, 'TempID', to each row of data in _san_jose_d1.csv_. The `clean_addresses()` method does the following:
* Expands each row into multiple single addresses, sequentially identified by a new variable, 'TempIDZ'. Hyphen delimiters are, in most cases, assumed to imply a range of same-parity addresses (all numbers with the same parity delimited by the hyphen). Although this may lead to the creation of non-existent addresses, we assume that the expanded list will be fed to an address validator (e.g., USPS or a geocoder) and consequently reduced.  
* Generates a code detailing suspected problems or errors. 

The `addr_parse_report` method creates an output file that reports on the the attempt to parse the address data into an expanded list of well-formed street address strings. The report flags exceptional rows --- those with with problematic addresses or expandable addresses. The flags, in turn, explain the nature of the exception. A table of flags and their meaning is in the Excel spreadsheet, "FunctionMap.xlsx", provided with this package.  

An output of the expanded address list (together with 'TempID' and 'TempIDZ' internal identifiers) can be obtained by subsequently running the command
```
project.make_geocoder_file("expanded_san_jose_d1.csv")
```
As its syntax suggests, the output of this file can be fed to a geocoder or address validator. If a row in the address data generates a parsing error, it is **not** included in the output of this method. To examine such problem rows, consult the report file. An alternative to using the `addr_parse_report` or `make_geocoder_file` commands is the command `project.save_all("tstoutfile7.csv")`, which will create an output containing the full data structure stored in _project_.

This tool is still under development and offered "as is" in the hopes that users might pass along improvements. 


### Geocoding
Currently, CREDA_tools contains only one built-in approach to geocode the data generated using the address expansion tools. The following method uses the US Census geocoding API to geocode an expanded address list processed using the steps described above. 
```
project.run_geocoding('Census')
```
After execution, the _project_ object's data structure is appended with lat/long data. In addition, a 'confidence' score for each successful geocoder response request.

To generate an output of the geocoded data, one can use the following method,
```
project.save_geocoding("Census_output.csv", data_fields=True, address_fields=True)
```
where the original address and/or auxiliary data fields may be included by setting the command options to True or False.

There are far more reliable geocoders, and we expect that most users will wish to apply one or more of these to their expanded address data.  

## Parcel piercing

A second method is to export a file to be run externally in Geocoders, and then add the geocoded results back in when they are finished. We expect 3 columns including a 'lat', 'long', and 'confidence', and the analysis will fail without these.
The command make_geocoder_file() creates a generic file with TempIDZ and address information that many geocoders can use. After sending the generic file to your geocoder of choice, import the results back with the add_geocoder_results() function.
The add_geocoder_results() function will accept the output of some geocoders natively (e.g. it will parse ArcGIS output as is), but can also accept generic geocoder files, provided they have 1) a TempIDZ field, 2) 'lat' and 'long' fields, and 3) a 'confidence' field.
```
project.make_geocoder_file(outfile) #This creates a file with TempIDZ and cleaned address for geocoding
# Run Geocoding in other program
project.add_geocoder_results(geocoder, infile) # This will fail if infile doesn't contain lat, long, and confidence scores
```
Available geocoders can be found at (PLACEHOLDER). We do not provide licenses or API tokens to access these resources.
After you have added/run all geocoders, you can save the completed geocoding with the save_geocoding command. This takes a filename as input, and has two optional inputs for whether you want the data fields and address fields exported as well.
```
project.save_geocoding('some_file.csv')
# Or you can include optional fields
project.save_geocoding('some_file.csv', address_fields=True, data_fields_False)
```

#### Parcel Piercing
All Geocoding steps provide a latitude/longitude for each address being analyzed. Given a shapefile for parcels over the same geographic area as a set of addresses, we can then perform a parcel piercing step to determine which geometries are 'pierced' by a lat/long. This includes a nearest neighbor parsing algorithm, so that if the lat/long correspond with a position on the street (e.g. the mailbox rather than the building) there is still a high likelihood of matching the point to the property.
Parcel piercing is run on thte currently assigned shapefile, so first we assign a shapefile and then run our piercing algorithm.
```
project.assign_shapefile("CREDA_tools/test_data/san_jose_shapes.csv")
project.perform_piercing()
```
Geocoders often produce differing results, leading to different parcels pierced by lat/long coordinates. The CREDA_tools function pick_best_match() goes through each row of your piercing results where there is disagreement and can analyze them to select the optimal piercing. The function pick_best_match() by default uses a simple_max algorithm, which chooses the piercing with the highest confidence score based on the geocoder output. That being said, it is likely that among your available geocoders some will excel in other geographies while others are preferable another set. CREDA_tools provides a 'config.ini' that can adjust the confidence values generated from the geocoders to help solve this. The best selection for your dataset may require a custom scorer. For this reason, pick_best_match() accepts a function as input to allow for a custom picking algorithm to be run on each row.
The code below uses the default simple_max() function to choose the optimal matches.
```
project.pick_best_match()
```
Note: Although pick_best_match() is trivial when only a single geocoder is used, UBID creation requires a best_matches object generated in the pick_best_matches() step. If this step is omitted, it is automatically run during UBID generation.
#### UBID generation
Addresses should now be matched to the ShapeIDs from the Shapefile. As parcel shapes and property boundaries may change over time, we recommend a final switch to DOE UBIDs for the highest-confidence unique identifier for a property. This also allows for efficient joining with other data sets with UBID property values via Jaccard index.
```
project.generate_UBIDs()
```
After you have generated UBIDs, you can save the completed UBID results with the save_UBIDs() command. This takes a filename as input, and has two optional inputs for whether you want the data fields and address fields exported as well.
```
project.save_UBIDs('some_file.csv')
# Or you can include optional fields
project.save_UBIDs('some_file.csv', address_fields=True, data_fields_False)
```

#### Adding additional datasets
To combine multiple datasets, this process can be completed on another file, followed by a jaccard score match. For example:
```
project2 = helper.CREDA_Project("test_data\\san_jose_d2.csv")
project2.clean_addresses()

project2.run_geocoding('Census')
project2.assign_shapefile("CREDA_tools/test_data/san_jose_shapes.csv")
project2.perform_piercing()
project2.pick_best_match()
project2.generate_UBIDs()

temp = project.jaccard_combine(project2)
```

## Contributing

We welcome all help in furthering the CREDA Initiative. To contribute in code development, please read (THIS IS ONLY A PLACEHOLDER) [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us. To collaborate with additional data and tools, please reach out to David_Fisher @ kenan-flagler.unc.edu.

## Authors

* **David Fisher** - *Development of Initial Pipeline, ongoing code improvements* - [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/)
* **Jacob Sagi** - *Professor at UNC's Kenan-Flagler Business School, primary architect of CREDA* - [Kenan-Flagler Business School](https://www.kenan-flagler.unc.edu/faculty/directory/jacob-sagi/)
* **[Huan Lian](https://kenaninstitute.unc.edu/people/huan-lian/)** - *Wizard data analyst and tester supporting the project* - [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/)

See also the list of (PLACEHOLDER) [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License (PLACEHOLDER. We need to decide on licensing) - see the [LICENSE.md](LICENSE.md) file for details
