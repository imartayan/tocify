# Tocify

A tool for manipulating table of contents and writing them to pdf or djvu files.

`tocify` is written in Python and requires `cpdf` for pdf files and `djvulibre` for djvu files.

```
usage: python3 tocify.py [-h] [--clean] [--offset n] toc file

A tool for writing outline to pdf or djvu files

positional arguments:
  toc         table of contents
  file        pdf or djvu file

optional arguments:
  -h, --help  show this help message and exit
  --clean     export a clean outline
  --offset n  add offset to page numbers
```

See the `example` folder for some examples of table of contents.
