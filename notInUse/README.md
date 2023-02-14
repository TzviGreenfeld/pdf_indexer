# PDF indexer

Merges pdf files and creates an  table of content psge + bookmarks

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Support](#support)

## Installation

Download main.py and install libraries from requirements.txt


```
$ git clone https://github.com/TzviGreenfeld/pdf_indexer
$ pip install -r requirements.txt
```

## Usage

send as arguments pdf files, or folder containing all the files to merge. 
Last argument is the output file name

```
$ python3 main.py <1.pdf> <2.pdf> ... <n.pdf> <out.pdf>
```
or

```
$ python3 main.py <path_to_folder_containing_pdf_files> <out.pdf>
```


## Support

Please [open an issue](https://github.com/TzviGreenfeld/pdf_indexer/issues/new) for support.
