# CREDA Tools

This repository contains the primary code base for the address-matching [CREDA Project](https://kenaninstitute.unc.edu/publication/commercial-real-estate-data-towards-parity-with-other-asset-classes-a-report-on-the-progress-of-the-commercial-real-estate-data-alliance-creda/) at UNC's [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/). The code toolkit is designed to help transform commercial real estate data source address identifiers into geospatially meaningful identifiers (via Department of Energy UBIDs). These can then be used for merging data sets and to investigate relationships between records within a data set. We ask users of this repository to please cite our work. E.g.,

```
Fisher, D. and Sagi, J.S. (2021), CREDA_tools: Linking address records through geospatial identifiers. 
https://github.com/KI-Research-Services/CREDA_tools).
```

## CREDA Mission Statement

The Commercial Real Estate Data Alliance is a consortium of academics dedicated to achieving data parity with other major asset classes. Specifically, we believe that improved access to and understanding of available data in commercial real estate is key to fostering higher quality research and interactions between academia and industry, to the benefit of the entire CRE community.

## Getting Started

The document, "Install instructions for GitHub.pdf", contains detailed instructions for getting a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

CREDA_tools is built in Python and has fairly lightweight requirements. If you prefer not to follow the instructions in the installation document, please ensure that the following libraries are installed:

* Numpy
* Pandas
* Shapely
* buildingid from the Department of Energy. Instructions for this installation can be found at [their GitHub Repository](https://github.com/pnnl/buildingid-py).
* censusgeocode is needed to use the Census Geocoder. Run with 'pip install censusgeocode'

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
Once you have a root folder with CREDA_tools inside it, you can begin a task or sequence of tasks. First, one must import the tool library (do this from within the top CREDA_tools directory):
```
from CREDA_tools import helper
```

Instantiation of a CREDA_Project object using a data file takes the following form (sample data files used in demonstrating various tasks are in the /test_data directory). 
```
project = helper.CREDA_Project(<task_type>, <in_file>)
```
#### Tasks
* Parsing strings from a list, where each string contains multiple addresses, into an expanded list of street addresses that can be geocoded.
  * <task_type> = "addresses"  
  * <in_file> is the name of a (CSV) file (placed in quotes) with required data fields 'addr', 'city', 'postal', and 'state'. Auxiliary data columns are permitted. 
  * Note that the 'addr' field can contain multiple street addresses (e.g., the single string "140 Main St., 20-52 Ford Ave., 67 & 122 Glenn Dr.").
* Associating geocodes with geospatial polygons that the geocodes ``pierce''.
  * <task_type> = "geocodes"  
  * <in_file> is the name of a (CSV) file (placed in quotes) with required data fields 'lat', 'long', and 'confidence'. Auxiliary data columns are permitted. 
  * The confidence field is a number between 0 and 1 that scores the confidence associated with the geocoded data. Greater confidence should be associated with a returned geocode based on the perceived accuracy (e.g., if it corresponds to a rooftop geocode versus a zip code centroid). The confidence level is assumed to be subjectively assigned by the user based on their knowledge/experience with the geocoder(s) used.
  * If a non-unique 'TempID' field is included, then it can be used to refer to user-defined groupings of geocodes. This may happen when a record in a dataset is associated with multiple geocodes (e.g., multiple addresses/structures/properties).  
* Assigning a spatial identifier to each shape in a list. 
  * <task_type> = "parcels"  
  * <in_file> is the name of a (CSV) file (placed in quotes) with required data field 'GEOM' containing WKT strings. At this point, the only WKT strings that can be processed are
    * POLYGON
    * MULTIPOLYGON
    * GEOMETRYCOLLECTION containing either POLYGON or MULTIPOLYGON shapes
  * If a non-unique 'ShapeID' field is provided, then it can be used to refer to user-defined groupings of shapes. This may happen, for instance, when multiple shapes are related (e.g., a multi-parcel property).   

Once a project has been instantiated, several function can be applied to the created object to achieve the desired result (e.g., cleaning addresses, associating geocodes with shapes, etc.). In what follows, we provide details on each of the main tasks described above. 

## Address list expansion

In many commercial real estate data sets, the address field for a "property" record contains items such as "1650 & 1750 S. Babcock Avenue" or "1610-1650 Bienvenue Road", each of which refers to a _list_ of addresses rather than a single address. When linking or merging data sets, or simply looking for related records within the same data set (e.g., repeat sales transactions), it seems useful to allow for partial overlap. For instance, a record referring to "1650 & 1750 S. Babcock Avenue" might have some relationship to one referring only to "1700 S. Babcock Avenue". The tool we developed and describe in this section is meant for expanding such address references into address lists. We are not aware of the general availability of a similar tool. 

At this point, the tool creates a list from compounded street addresses that use one or more of the following conjunctions and delimiters (not case sensitive): "and", "&", "/", "\\", "-", ";", ",". Some examples of compound addresses are found in _san_jose_d1.csv_, available in the _CREDA_tools/test_data_ directory. The following sequence of commands expands this file into a list of addresses (please remember to work in the top CREDA_tools directory). We use data from San Jose in this and other examples because the municipality posted its parcel addresses and shapes on a public server.

```
from CREDA_tools import helper
project = helper.CREDA_Project("addresses", "test_data/san_jose_d1.csv")
project.clean_addresses()
project.addr_parse_report("report_san_jose_d1.csv")
```
As described earlier, the first command imports the project tools. The second instantiates a "project" object that contains the address file. The object _project_ assigns a sequential unique internal identifier, 'TempID', to each row of data in _san_jose_d1.csv_. The `clean_addresses()` method does the following:
* Expands each row into multiple single addresses, sequentially identified by a new variable, 'TempIDZ'. Hyphen delimiters are, in most cases, assumed to imply a range of same-parity addresses (all numbers with the same parity delimited by the hyphen). Although this may lead to the creation of non-existent addresses, we assume that the expanded list will be fed to an address validator (e.g., USPS or a geocoder) and subsequently reduced.  
* Generates a code flagging compound addresses and detailing suspected problems or errors. 

The `addr_parse_report` method creates an output file that reports on the the attempt to parse the address data into an expanded list of well-formed street address strings. The report flags exceptional rows --- those with problematic addresses or expandable addresses. The flags, in turn, explain the nature of the exception. A table of flags and their meaning is in the Excel spreadsheet, "FunctionMap.xlsx", provided with this package.  

An output of the expanded address list (together with 'TempID' and 'TempIDZ' internal identifiers) can be obtained by subsequently running the command
```
project.make_geocoder_file("expanded_san_jose_d1.csv")
```
As its syntax suggests, the output of this file can be fed to a geocoder or address validator. If a row in the address data generates a parsing error, it is **not** included in the output of this method. To examine such problem rows, consult the report file. An alternative to using the `addr_parse_report` or `make_geocoder_file` commands is the method `project.save_all(<outfile>)`, which will create an output file containing the full data structure stored in _project_.

This tool is still under development and offered "as is" in the hopes that users might pass along improvements. 


### Geocoding an expanded address list
Currently, CREDA_tools contains only one built-in approach to geocode the data generated using the address expansion tools. The following method uses the US Census geocoding API to geocode an expanded address list processed using the steps described above. 
```
project.run_geocoding('Census')
```
After execution, the _project_ object's data structure is appended with lat/long data. In addition, a 'confidence' score is assigned to each successful geocoder response request (an "Exact" geocode returned by the Census is assigned a score of 0.89, while a "Non_Exact" geocode is assigned a score of 0.7).

To generate an output of the geocoded data, one can use the following method,
```
project.save_geocoding("Census_output.csv", data_fields=True, address_fields=True)
```
where the original address and/or auxiliary data fields may be included/excluded by setting the command options to True or False.

There are far more reliable geocoders, and we expect that most users will wish to apply one or more of these to their expanded address data. To add to the _project_ structure geocodes for the expanded address data follow the following steps: 
1.  Generate an output of the expanded address list (e.g., as was done with the file _expanded_san_jose_d1.csv_ generated earlier)
2.  Feed the address list to your geocoder of choice to generate geocodes for the addresses in the expanded list
3.  Create a CSV file that contains the following data fields. Additional (auxiliary) data fields could be optionally included.
    1.  lat
    2.  long 
    3.  confidence
4.  The 'lat' and 'long' fields correspond to the geocoder output. The 'confidence' field is a required user-generated real number in the interval [0, 1] that conveys the user's confidence in the generated geocode (e.g., a rooftop geocode should be assigned a higher confidence than a zip code centroid).
5.  Run the command `project.add_geocoder_results(<geocoder_name>, <file_name.csv>)` where _geocoder_name_ is a user-defined string to identify the geocoder and _file_name.csv_ is the name of the file created in Step 3. 

Below is an example using the San Jose sample data. 
```
project.add_geocoder_results("ArcGIS", "test_data/generic_geo_2.csv")
```

It is possible to repeat steps 1-5 above using several geocoders (the data structure in _project_ will store all the geocoders' data) --- just be sure to use distinct geocoder names. This can be useful because, in our experience, no single geocoder is able to consistently outperform all others at every location. Using multiple geocoders with judicious assignment of confidence scores can achieve superior overall performance.  

**IMPORTANT:** Geocode data added using the ``add_geocoder_results`` method is assumed to line up exactly with the existing structure already stored in _project_. In particular, any excess records in the newly added file are dropped (e.g., if the base structure has 1000 rows, then only the first 1000 rows of the newly added structure are kept). To see how newly added geocode data should be lined up, compare with an output of the base structure (using the ``save_geocoding`` or the ``save_all`` methods described above).   

## Parcel piercing from a list of geocodes

A key task we foresee for using CREDA_tools is to associate geocodes (presumably generated from addresses) with geospatial shapes (e.g., building footprints or property parcels). In what follows, we will refer to a geospatial shape as a 'parcel' because legal parcel shapes are widely available for real estate properties in the United States, but one could also use finer (or coarser) shapes  (e.g., building footprints). The basic idea is to check whether a geocode associated with an address lies within, or 'pierces', a parcel from a list of distinct parcels.

### Skipping the "Address list expansion" step to work exclusively with lists of geocodes 
The previous section ("Address list expansion") outlines how one can arrive at lists of geocodes (one list for every geocoder used) associated with an expanded address list. This is not necessary if one already has a set of geocoded clean addresses. The following methods outline how one can create a data structure directly from a list of geocodes without the need to explicitly include addresses. Address information is not used in parcel piercing tasks but is, of course, important if one wishes to link parcel piercing results back to an address list. 

To skip the address list expansion task and create a data structure of geocode lists, which can then be used in parcel piercing, instantiate the _project_ object using the 
"geocodes" option instead of the "addresses" option. This is done by issuing the command ``helper.CREDA_Project("geocodes", <in_file>)`` where <in_file> is the name of a (CSV) file (placed in quotes) with required data fields 'lat', 'long', and 'confidence'. Auxiliary data columns are permitted as are optional 'TempID' and 'TempIDZ' key fields. As with the geocoding data discussed earlier, a confidence parameter is required. If 'TempID' or 'TempIDZ' fields are included the instantiated project uses these as a base for its data structure. If they are not included, they will be created. As with the earlier case of geocoding expanded address lists, non-unique 'TempID' entries be used to refer to user-defined groupings of geocodes. This may happen when a record in some source data is associated with multiple geocodes (e.g., multiple addresses, structures, or properties). Using the provided San Jose sample data, project instantiation from the top CREDA_tools directory using the "geocodes" option proceeds as follows:
```
project = helper.CREDA_Project("geocodes", "test_data/generic_geo_2.csv")
```
An output of the geocodes data structure in _project_ can be created using the ``save_geocoding`` or the ``save_all`` methods described above. To incorporate additional geocoders into the data structure, so as to benefit from their complementary strengths, follow the steps above for implementing the method ``add_geocoder_results``. 

### Parcel Piercing

If the _project_ data structure contains geocodes, one can associate each with a geospatial shape from a list. To load a list of shapes into the data structure, run ``project.assign_shapefile(<shapefile>)``, where _shapefile_ is the name of a (CSV) file (placed in quotes) with required data field 'GEOM' containing WKT strings. At this point, the only WKT shapes that can be processed correspond to POLYGON, MULTIPOLYGON, or GEOMETRYCOLLECTION (containing either POLYGON or MULTIPOLYGON shapes). If a non-unique 'ShapeID' field is provided, then it can be used to refer to user-defined groupings of shapes. This may happen, for instance, when multiple shapes are related (e.g., a multi-parcel property). If a 'ShapeID' field is not provided, it will be created sequentially. Correspondingly, the method creates a unique 'ShapeIDZ' numerical identifier to further refine all polygons that share the same 'ShapeID' (some WKT shapes are MULTIPOLYGONS or GEOMETRYCOLLECTION and these are expanded into distinct polygons). SUMMARIZING: Each ShapeIDZ refers to a single geospatial polygon while a ShapeID may link groups of geospatial polygons.   

We strongly recommend pre-processing _shapefile_ to eliminate essentially duplicate WKT shapes (e.g., those sharing 99.999% of their area). At this point, we are not offering tools to help refine shape files, so this is left to the user's discretion. Note that the presence of near-duplicate shapes is likely to lead to multiple shapes pierced by the same geocode. Once the shape file is added to a _project_ structure that includes geocodes, one can run the piercing algorithm. For example:
```
project.assign_shapefile("CREDA_tools/test_data/san_jose_shapes.csv")
project.perform_piercing()
```
The results can be viewed by generating output via the ``save_all`` method described above. In the generated output file, pierced parcels are identified by their ShapeIDZ identifier (or _identifiers_ if a geocode pierces several polygons). 


## Assigning UBIDs to shapes

WKT strings are cumbersome to use as record identifiers. A more efficient approach to code geospatial information into a string is the Unique Building Identifier (UBID) developed by the US Department of Energy (DOE). We incorporated some of their tools into our suite. To see examples of how the WKT strings can be associated with UBIDs, visit [https://buildingid.github.io/](https://buildingid.github.io/).

There are two ways to assign UBIDs to shapes in CREDA_tools. The first takes results from parcel piercing (as described above) and assigns UBIDs to all pierced shapes (polygons) as well as to polygons related to pierced shapes (via a grouping such as a ShapeID). The second method allows users to instantiate a project using only a list of WKT shapes and then assign a UBID to *every* shape in the list. The second method is useful when a user has already associated shapes with address records and simply needs transform them into the more efficient UBID identifier.

### Assigning UBIDs to pierced (and related) polygons 

 <!--  
Geocoders often produce differing results, leading to different parcels pierced by lat/long coordinates. The CREDA_tools function pick_best_match() goes through each row of your piercing results where there is disagreement and can analyze them to select the optimal piercing. The function pick_best_match() by default uses a simple_max algorithm, which chooses the piercing with the highest confidence score based on the geocoder output. That being said, it is likely that among your available geocoders some will excel in other geographies while others are preferable another set. CREDA_tools provides a 'config.ini' that can adjust the confidence values generated from the geocoders to help solve this. The best selection for your dataset may require a custom scorer. For this reason, pick_best_match() accepts a function as input to allow for a custom picking algorithm to be run on each row.
--> 

To assign UBIDs to a data structure with pierced shapes, run the following command after ``project.perform_piercing()``: 
```
project.generate_UBIDs()
```
Recall that each row in the geocode data structure represents a single "expanded address" or, equivalently, a unique TempIDZ. Each such row may be associated with multiple geocodes if, address information was sent to more than one geocoders. For each TempIDZ, the ``project.generate_UBIDs()`` method assigns a single UBID corresponding to the polygon pierced by the **highest confidence** geocode. It is possible to change the criteria for selecting the optimal geocode to use when there are several candidates that pierce different parcels. To do this, see the code for the method ``pick_best_match(<func>)`` which can accept a function, _func_, that will prioritize geocodes according to a criterion other than highest confidence.

To generate an output for this procedure, either use the ``save_all`` method or the ``save_UBIDs`` method. The latter has the same syntax and output options as the ``save_geocoding`` command described earlier. For a given TempIDZ, the output will include the following fields:
* **best_geocoder** --- The geocoder chosen (based on a criterion such as the highest confidence) 
* **matching_ShapeIDZ** --- A list of the ShapeIDZs of a polygon pierced by the chosen geocode. Note that it is possible for more than one polygon to be pierced if the shape file data isn't sufficiently pre-processed to remove near-duplicate shapes (or, more rarely, if the parcel record data contain distinct but overlapping polygons).
* **single_ShapeIDZ** --- The ShapeIDZ of one of the pierced polygons listed in 'matching_ShapeIDZ'.
* **ShapeID, ShapeIDZ, UBID** --- Polygon shape identifiers and the UBID for any polygon that is related to 'single_ShapeIDZ' (because they share the same 'Shape_ID'). As mentioned earlier, this can happen when polygons are linked through some relationship (like common ownership). 

![image](https://user-images.githubusercontent.com/69352948/115027297-885a5500-9e91-11eb-94e6-b412899fb275.png)


### Assigning UBIDs to a list of polygons 

CREDA_tools also provides solutions to users who simply wish to assign UBIDs to all shapes in a shape file. In this case, the project should be instantiated as follows:
```
project = helper.CREDA_Project("parcels",<in_file>)
```
Here, <in_file> is the name of the shape file, formatted according to the specifications outlined for _shapefile_ above (see "Parcel Piercing"). Unless a 'ShapeID' field is included, the project will automatically assign a ShapeID to every row of data (i.e., every WKT string). In addition, any WKT string containing more than one polygon will be expanded into its constituents and each will be assigned a unique ShapeIDZ. As emphasized earlier, and unless necessary for the specific use case, we encourage users to preprocess shape files to eliminate near-duplicates and incorporate any relationships across rows (i.e., shapes) using common ShapeID entries.

After instantiating the shape file data structure in _project_, UBIDs can be assigned to *all* shapes by running the ``generate_UBIDs()`` command. E.g., 
```
project.generate_UBIDs()
```
As discussed earlier, an output of the results can be generated using the ``save_all`` method or the ``save_UBIDs`` method.



## Matching on UBIDs
To allow users to merge data sets using UBID identifiers, we incorporated into CREDA_tools the Department of Energy's code for determining geospatial overlap (specifically, their ``--left-group-by-jaccard`` and ``--right-group-by-jaccard`` functions). Our version of this tool matches a row in one CSV file with a row in another CSV file if the geospatial overlap of their respective UBID identifiers exceeds some threshold fraction of their combined areas. This is also known as an intersection over union ratio or the Jaccard index of the two regions. The merge can be performed without instantiating a project object, but first one must run ``from CREDA_tools import helper`` if it was not previously run during the session. Usage is as follows:
```
helper.jaccard_combine(<in_file1>, <in_file2>, threshold, <out_file>)
```
where <in_file1> and <in_file2> are CSV files, each containing a 'UBID' field with UBID identifiers. The two input files can contain auxiliary data (useful for linking back to source data sets). The argument _threshold_ should be a real number between 0 and 1 and represents a minimum Jaccard index for determining a match between two geospatial regions (we have had good success using 0.65). <out_file> is the output file name. Each row in <out_file> contains a row from <in_file1> matched to a row in <in_file2> (a many-to-many merge) and all auxiliary data fields from both sources are included (fields in the input files with identical names are renamed with an _x_ and _y_ subscript, corresponding to <in_file1> and <in_file2>, respectively). <out_file> also includes two additional fields called 






## Contributing

We welcome all help in furthering the CREDA Initiative. To contribute in code development, please read (THIS IS ONLY A PLACEHOLDER) [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us. To collaborate with additional data and tools, please reach out to David_Fisher @ kenan-flagler.unc.edu.

## Authors and acknowledgements

* **David Fisher** - *Development of Initial Pipeline, ongoing code improvements* - [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/)
* **Jacob Sagi** - *Professor at UNC's Kenan-Flagler Business School, primary architect of CREDA* - [Kenan-Flagler Business School](https://www.kenan-flagler.unc.edu/faculty/directory/jacob-sagi/)

This project would not have been possible without the financial support of the [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/) and the [Wood Center for Real Estate Studies](https://realestate.unc.edu/). Significant contributions have also been made by [Huan Lian](https://kenaninstitute.unc.edu/people/huan-lian/) and [Tomek Wisniewski](https://www.linkedin.com/in/tomwi).

<!--- 
See also the list of (PLACEHOLDER) [contributors](https://github.com/your/project/contributors) who participated in this project.
--->

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/) - see the [LICENSE.md](LICENSE.md) file for details
