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

## Contributing

We welcome all help in furthering the CREDA Initiative. To contribute in code development, please read (THIS IS ONLY A PLACEHOLDER) [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us. To collaborate with additional data and tools, please reach out to David_Fisher @ kenan-flagler.unc.edu.

## Authors

* **David Fisher** - *Development of Initial Pipeline, ongoing code improvements* - [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/)
* **Jacob Sagi** - *Professor at UNC's Kenan-Flagler Business School, primary architect of CREDA* - [Kenan-Flagler Business School](https://www.kenan-flagler.unc.edu/faculty/directory/jacob-sagi/)
* **Huan Lian** - *Wizard data analyst and tester supporting the project* - [Kenan Institute for Private Enterprise](https://kenaninstitute.unc.edu/)

See also the list of (PLACEHOLDER) [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License (PLACEHOLDER. We need to decide on licensing) - see the [LICENSE.md](LICENSE.md) file for details
