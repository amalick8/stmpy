# stmpy

Stmpy is a python-based data analysis package for scanning tunneling microscopy data.

  - Load all default Nanonis filetypes
  - Analysis tools: curve fitting, linecuts, drift correction and more.
  - Easily create movies and high-quality figures

Get started with the stmpy 101 tutorial in `stmpy/doc/`

### Installation

STMPY requires Python 3.9 or newer.

For developers:

1. **Clone** or **download** `stmpy` to your local drive.
2. Navigate to the local copy of STMPY.
3. Install it in editable mode:

```sh
python -m pip install -e .
```

Run the automated tests from the repository root:

```sh
python -m unittest discover -s tests -v
```

### Reproducible analysis records

STMPY can optionally save a small JSON record beside a processed data file or
figure. The record includes the STMPY version, timestamps, parameters, input
and output filenames, SHA-256 file fingerprints, and loaded array dimensions.
Existing loading and saving code is unchanged unless a record is supplied.

```python
import stmpy

record = stmpy.AnalysisRecord(
    "topography correction",
    parameters={"sample": "FeSe", "temperature_K": 4.2},
)

data = stmpy.load("measurement.sxm", record=record)
# Run analysis and export a figure or processed file here.
stmpy.save(data, "corrected.spy", record=record)
record.save("corrected.analysis.json")
```

For users (in progress)

```sh
$ pip install hoffmanstmpy
```

### Usage
In the stmpy-doc folder, there are three tutorial notebooks and one coding template.
1. **Stmpy 101 - getting started.ipynb**: basic usage of stmpy to analyze topography maps and DOS maps
2. **Stmpy 102 - dfc tutorial.ipynb**: drift correction tutorial, including theory behind drift correction and usage of this module
3. **piezo calibration.ipynb**: describe how to calibrate your piezo with two topos
4. **stmpy notebook template -- topos and dos maps.ipynb**: template notebook that has example codes for different usage of stmpy (kinda of serving as table of content for this library), including loop through all the topos in a folder, drift correct and take linecuts on a DOS map, still growing...

License
----

MIT
