# fsleyes-plugin-epicseg

This repository provides a FSLeyes plugin to automatically segment epicardial, paracardial fat on four chamber cine MRI using a optimised U-Net.

The plugin has been tested on FSLeyes version 0.34.2.

## Installation

```sh
git clone github/pdaude/fsleyes-plugin-epicseg.git
```

You need to unzip the file ./fsleyes_plugin_epicseg/UNet48_first_layer.zip (GITHUB does not allow files bigger than 100 MB) 

## Documentation 

```sh
cd fsleyes-plugin-epicseg/fsleyes_plugin_epicseg/userdoc
mkdir build
make html
```

Open **index.html** in *fsleyes-plugin-epicseg/fsleyes_plugin_epicseg/userdoc/build/html*

## Usage

### Installation in FSLeyes

If you want to install fsleyes-plugin-epicseg in FSLeyes :

```sh
pip install -e path/to/the/file/fsleyes-plugin-epicseg 
```
When you will start FSLeyes, the fsleyes-plugin-epicseg will be already loaded in the GUI.

## Reference


