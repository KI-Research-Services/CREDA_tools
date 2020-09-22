# CREDA Tools

This repository contains the primary code base for the [CREDA Project](https://kenaninstitute.unc.edu/publication/commercial-real-estate-data-towards-parity-with-other-asset-classes-a-report-on-the-progress-of-the-commercial-real-estate-data-alliance-creda/) at UNC's [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/). This code is specifically meant to take various commercial real estate data sources, identifying properties by addresses, to joining datasets via DOE UBIDs.

## CREDA Mission Statement

The Commercial Real Estate Data Alliance is a consortium of academics dedicated to achieving data parity with other major asset classes. Specifically, we believe that improved access to and understanding of available data in commercial real estate is key to fostering higher quality research and interactions between academia and industry, to the benefit of the entire CRE community.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

CREDA_tools is built in Python, so a Python installation will be needed. Basic CREDA_tools has fairly lightweight requirements, using only the following basic data science libraries:

* Numpy
* Pandas
* Shapely

Many Python distributions include these as standard, but otherwise all can be installed via pip, such as in 'pip install numpy'. Advanced CREDA_tools modules, such as those that allow for geocoding within the pipeline, often require specialized libraries, such as the googlemaps library to use GAPI.

### Installing

As this goes public, we would like to transition to a pip install of CREDA_tools as well. In the meantime, we recommend cloning/downloading the repository such that CREDA_tools is a subdirectory in the root folder you wish to run projects in.



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

### CREDA_Project Objects
Analysis with CREDA Tools revolves around the CREDA_Project object. This is passed a file at initialization, and can then be taken through several different analysis steps ending in creation of UBIDs for each address. After multiple CREDA_Project objects have been prepared, one for each data source, they can be combined with functions such as our jaccard_combine() to generate joined datasets.

### Basic Usage
#### Instantiation
Once you have a root folder with CREDA_tools inside it, we can start processing a file of addresses with data. First we instantiate a CREDA_Project object with a data file. Sample files have been provided (/test_data) to show the pipeline.
```
from CREDA_tools import helper

project = helper.CREDA_Project("/CREDA_tools/test_data/san_jose_d1.csv")
```

#### Clean Addresses
Now that we have an analysis object, we can clean the addresses.
```
project.clean_addresses()

```
The following above code creates two objects with our CREDA_File object, a parsed_addresses object matching original addresses to parsed addresses, and an address_errors object which tracks issues and errors in the parsing. If we want a report of address parsing errors, we can produce a file summarizing these with
```
project.addr_parse_report(outfile)
```

#### Geocoding
CREDA_tools supports two main methods of Geocoding. First, some Geocoders can be called in real time from within CREDA_tools. The code below runs Census geocoding on our processed addresses, creating a geocoding object with Census_lat, Census_long, and Census_confidence fields.API
```
project.run_geocoding('Census')
```
A second method is to export a file to be run externally in Geocoders, and then add the geocoded results back in when they are finished. This can be accomplished through
```
project.make_geocoder_file(outfile) #This creates a file with TempIDZ and cleaned address for geocoding
# Run Geocoding in other program
project.add_geocoder_results(geocoder, infile)
```
Available geocoders can be found at (PLACEHOLDER). We do not provide licenses or API tokens to access these resources.

#### Parcel Piercing
All Geocoding steps provide a latitude/longitude for each address being analyzed. Given a shapefile for parcels over the same geographic area as a set of addresses, we can then perform a parcel piercing step to determine which geometries are 'pierced' by a lat/long. This includes a nearest neighbor parsing algorithm, so that if the lat/long correspond with a position on the street (e.g. the mailbox rather than the building) there is still a high likelihood of matching the point to the property.
Parcel piercing is run on thte currently assigned shapefile, so first we assign a shapefile and then run our piercing algorithm.
```
project.assign_shapefile("/CREDA_tools/test_data/san_jose_shapes.csv")
project.perform_piercing()
```
Geocoders often produce differing results, leading to different parcels pierced by lat/long coordinates. The CREDA_tools function pick_best_match() goes through each row of your piercing results where there is disagreement and can analyze them to select the optimal piercing. The function pick_best_match() by default uses a simple_max algorithm, which chooses the piercing with the highest confidence score based on the geocoder output. That being said, it is likely that among your available geocoders some will excel in other geographies while others are preferable another set. CREDA_tools provides a 'config.ini' that can adjust the confidence values generated from the geocoders to help solve this. The best selection for your dataset may require a custom scorer. For this reason, pick_best_match() accepts a function as input to allow for a custom picking algorithm to be run on each row.
The code below uses the default simple_max() function to choose the optimal matches.
```
project.pick_best_match()
```
Addresses should now be matched to the ShapeIDs from the Shapefile. As parcel shapes and property boundaries may change over time, we recommend a final switch to DOE UBIDs for the highest-confidence unique identifier for a property. This also allows for efficient joining with other data sets with UBID property values via Jaccard index.
```
project.generate_UBIDs()
```
To combine multiple datasets, this process can be completed on another file, followed by a jaccard score match. For example:
```
project2 = helper.CREDA_Project("test_data\\san_jose_d2.csv")
project2.clean_addresses()

project2.run_geocoding('Census')
project2.assign_shapefile("test_data\\san_jose_shapes.csv")
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
