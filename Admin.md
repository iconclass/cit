# CIT Administration

## Introduction

The CIT is administered by at team at the V&A in London, UK.

## How to run your own copy of the CIT software, and convert the source data.

_First_, make a clone of the [CIT Git repository](https://github.com/iconclass/cit) to your local machine.

Ensure that you then have [Docker](https://www.docker.com/) installed to your machine.

Now run the following command in a Terminal window to get the latest CIT Docker image:

```shell
docker pull ghcr.io/iconclass/cit:latest
```

### Running a test version

To run a local test copy of the CIT, you first need to create the database.

Run the following command:

```shell
docker run --rm -it -v $(pwd):/home ghcr.io/iconclass/cit:latest python /home/scripts/convert_todb.py /home/data/CIT.dmp /home/data/CATALOG.dmp
```

This will create a file named `src/CIT.sqlite` - which is a searchable index database file containing all the data from the CIT.dmp and CATALOG.dmp files.

To run the CIT server, use this command:

```shell
docker run --rm -it -v $(pwd)/src/templates:/home/src/templates -v $(pwd)/src/translations.dmp:/home/src/translations.dmp  -p 8000:8000 ghcr.io/iconclass/cit:latest
```

Now you can look at this link [http://localhost:8000/](http://localhost:8000/) in your web-browser.

## Data Conversion

The data for the CIT is managed in the collections management system of the V&A, and periodically exported and converted to a format that is used for the website.

An XML dump of the thesaurus and catalog information is made, and then converted using the Python scripts in this repo. One converts the thesaurus, and another converts the catalog data. The output of these conversion scripts then create .dmp files, which are more human-friendly to read and use for further analysis and dissussion.

### Thesaurus terms

From the CIT.dmp file, we also create some further derivatives; a SQLITE database used for navigation and searching, and a SKOS version in JSON-LD.

Ensure you have a thesaurus exported datafile named `CIT.xml` in the same directory of the checked-out repository.
To convert an XML thesaurus data file to the CIT format, run the following command:

```shell
python ./src/scripts/convert_thesaurus.py CIT.xml
```

this should all be on one line, exactly as shown.

When this command runs, the file named `CIT.dmp` is overwritten with the latest data.

### Catalog Entries

Once you have a CIT.dmp file, this can be used to convert the XML files as exported by the V&A CMS. First, make sure that you have a folder that contains all the .JPG images to be used, as a sub-folder of where the XML files are that you would like to import. The image files can be in separate folders, as long as they all have the same containing folder.

For example, if you have a folder that looks similar to this:

```
.
├── allimages
├── CIT.dmp
├── CMA.xml
├── HYL.xml
├── MET.xml
├── NPM.xml
├── VAM.xml
```

-- and in the `allimages` folder are all your JPG images.

```shell
python ./src/scripts/convert_catalog.py -i allimages -c CMA CMA.xml
python ./src/scripts/convert_catalog.py -i allimages -c HYL HYL.xml
python ./src/scripts/convert_catalog.py -i allimages -c MET MET.xml
python ./src/scripts/convert_catalog.py -i allimages -c NPM NPM.xml
python ./src/scripts/convert_catalog.py -i allimages -c VANDA VAM.xml
```

This needs to be run for each XML file, and the output will be a file named CATALOG.dmp.

**NOTE** The correct collection abbreviation needs to be used to match the file. In the above example this is _VANDA_ while the file is named VAM.xml
