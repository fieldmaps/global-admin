# Global Admin

The Fieldmaps Global Admin project is a data processing pipeline designed to take the "best available" administration boundary information from multiple sources and aggregate them into a single dataset. By normalizing inputs in this way, the intent is to ease the process for derivative products at the global level to be automatically generated. Data processing is done to create standardization for both spatial and tabular aspects of boundary data.

## Get the Data

![dataset coverage](https://raw.githubusercontent.com/fieldmaps/global-admin/master/images/coverage.png)

At its current stage, this project is undergoing active development, with schemas and download links subject to change. Currently, data is available for over 100 countries originating from [Humanitarian Data Exchange](https://data.humdata.org/search?ext_cod=1), with remaining countries sourced from [GADM](https://gadm.org/data.html). A full breakdown of sources and metadata is available [here](https://github.com/fieldmaps/global-admin/blob/master/data.csv).

- Boundaries (most detailed level only, 1.4 GB): https://data.fieldmaps.io/global-admin/wld.gpkg.zip
- Boundaries (all levels, 2.2 GB): https://data.fieldmaps.io/global-admin/wld_levels.gpkg.zip
- Attributes only: https://data.fieldmaps.io/global-admin/wld.xlsx.zip

Special exports for particular use cases:

- Attributes only in HDX/ITOS format: https://data.fieldmaps.io/global-admin/hdx_attributes.zip

## Normalization: Boundaries

A common problem of merging spatial data from different sources is the existence of gaps and overlaps between sources. There are many ways to address this problem, with the approach taken here being to generate digital boundary files for each input. In this context, a digital boundary file is one that does not follow shorelines and international boundaries, but rather stretches out with simplified edges, intended for users to clip with their own shorelines and international boundaries. For example, Statistics Canada uses a digital boundary file when creating census blocks, later clipped with lakes and shorelines to derive a layer suitable for reference maps.

![cartographic vs digital boundary file](https://raw.githubusercontent.com/fieldmaps/global-admin/master/images/cbf-vs-dbf.jpg)

## Normalization: Attributes

Just as with boundaries, merging attribute columns between sources with different schemas need to be conditioned so that columns align with each other. For a global level boundary file, the following data would be useful to access in a predicable manner:

- Names: Countries with more than one official language may have multiple names for places.
- Types: Administration divisions may be governed differently based on their status, such as with territories, autonomous regions, etc.
- Codes: Used for joining with additional data such as population statistics and other thematic data. A number of agencies have developed their own codes for giving areas unique IDs.

## Installation

This project has only been tested with macOS to date, compatibility with Windows 10 is not guarenteed. The minimum requrements for this project are Python 3 and pandas. See [pandas documentation](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html) for more details about installing this on your system. Before running, install pip dependancies:

```sh
pip3 install -r requirements.txt
```

## Usage

To replicate the results created by the download link, a `Makefile` is available to download input data too large to be stored in GitHub. To generate a new attribute dataset, the following commands must be run:

- `make get_attributes`: fetches a zip file hosted from an S3 bucket and extracts it to a local directory. This can be done manually if there are issues using this utility.
- `make build_attributes`: sequentially runs a series of 4 python scripts that import attributes from HDX and GADM, merge into a common dataset, and them re-export layers from all sources to the format originally found on HDX.

## Methodology: Boundaries

For those looking to replicate or create workflows of their own, the following serve as a high level overview of the steps carried out during spatial data processing to create the digital boundary file that is clipped with a global admin 0 layer such as the one from [WFP GeoNode](https://geonode.wfp.org/layers/geonode%3Awld_bnd_adm0).

![Input boundaries](https://raw.githubusercontent.com/fieldmaps/global-admin/master/images/tza-1.png)

The data processing pipeline takes the most detailed admin level available as the input.

![Input boundaries](https://raw.githubusercontent.com/fieldmaps/global-admin/master/images/tza-2.png)

From this input, the boundaries between admin regions are extended outwards using voronoi polygons.

![Input boundaries](https://raw.githubusercontent.com/fieldmaps/global-admin/master/images/tza-3.png)

The original input is dissolved with the resulting voronoi polygons to create a borderless digital boundary file.

![Input boundaries](https://raw.githubusercontent.com/fieldmaps/global-admin/master/images/tza-4.png)

This new layer can be clipped with any other admin 0 layer for that country.

1. Extract the edges of the boundary file as a line, while retaining information about which part of the line corresponds to which admin area. From this input, we want to extend these edges outwards in an intelligent way that will fill in space far beyond the original boundaries.
   1. Start with the most detailed admin level available from the original source, with all attributes stripped except for codes used for joining.
   2. Dissolve to a single admin 0 polygon.
   3. Convert both the most detailed admin level and the dissolved admin 0 layer from polygons to lines.
   4. Intersect line layers together, retaining information about which line segment originated from which detailed admin level.
2. Extract points along the lines to be used in generating voronoi polygons. Due to how voronoi polygons are generated, input points cannot be overlapping, so the ends of lines need to be trimmed an extremely small amount to allow a gap in between them. For this project, very small is defined as 0.000001 degrees (approx. 10cm)
   1. Apply a very small buffer to each line segment without dissolving results.
   2. Convert the buffers into lines.
   3. Intersect the buffer lines with the line segments used at the beginning of this part. Use a line intersection tool to create points where these two layers meet. This will result in points located a very small distance from the ends of each line.
   4. Using these points placed almost at the end of every line segment, generate a buffer of 0.000002 degrees. This is to ensure that points next to each other will have their buffers fully overlapping. Dissolve results.
   5. With these small buffers covering the ends of every line segment, use the difference tool to very slightly trim each line segment, so their ends no longer touch.
3. With a properly conditioned input line segment, extract sufficient points along the line. From testing multiple variables for point spacing, 0.0001 degrees (approx. 10m) was the shortest spacing that did not produce abnormal artifacts in results for all countries tested. However, generating points at this density resulted in processing times of days, so an alternative was used by combining less processor intensive methods.
   1. Points are generated regularly every 0.001 degrees (approx. 100m) along line segments.
   2. The input line segments were exploded so that every strait part along them became it's own feature.
   3. Points are generated by taking the centre of each exploded line part.
   4. Points generated in step 2.3 are combined with the steps above to create a single layer.
4. From these points spaced along the line, voronoi polygons intelligently extend outwards and allocate available space associated with the attributes of the edge point closest to it.
   1. Generate voronoi polygons from the input points, filling an area double the size of the original bounding box of the input.
   2. Dissolve polygons that originate from the same admin polygon.
   3. Merge this dissolved layer with the original admin layer through a union.
   4. In the attribute table, in places where the original admin and the voronoi polygons intersect, ignore the voronoi attributes and use only the original. In places where there is only voronoi polygons, use those values. Merge polygons together that share the same attribute values.
   5. Apply topology cleaning to ensure the integrity of the final result.
   6. Create higher admin levels by dissolving based on attributes.
   7. Clip all layers to desired global admin 0 layer.

## Methodology: Attributes

Tabular data is split into the following sheets:

- join: ID codes used for describing hierarchal relations
- adm0: country level metadata
- adm1 - adm5: names, types, and codes for individual layers

The join table uses ID codes that are generated uniquely for this project. ID's generated use the 3-letter ISO code to identify the country (admin 0 level), followed by sequential blocks of 3 numbers for every admin level. For example, the following would represent the first admin units of each level for Tanzania:

- Admin 0: `TZA`
- Admin 1: `TZA001`
- Admin 2: `TZA001001`
- Admin 3: `TZA001001001`

Codes are automatically generated sequentially and using this coding, so if the input admin 1 originally contained three regions coded (`TZ00`, `TZ02`, `TZ04`), the output for this project would still be (`TZA001`, `TZA002`, `TZA003`), with the original coding from the source captured in metadata. More information on attributes and coding to be added soon...
