# Gpx Splitter

This app was created out of the need to split large GPX files into smaller chunks for GPS devices which can handle only a limmiten number of track points. Another possible use case is, to split a large track into smaller pieces for daily stages.

## Install Requirements
```
pip install -r requirements.txt
```

## Running

From within directory.
```
python . <GPX_FILE> [-o <OUTPUT_DIR>] [-t (p|l)] [-m INTEGER]  [-d True]
```

Or from top directory.
```
python gpx_edit <GPX_FILE> [-o <OUTPUT_DIR>] [-t (p|l)] [-m INTEGER]  [-d True]
```

## Help
```
python gpx_edit --help
```