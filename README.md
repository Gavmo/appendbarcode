# appendbarcode

Add a Code 128A barcode to another PDF.

Basic usage:
```python
    combiner = AppendBarcode(save_path="output/")
    combiner.add_barcode("Barcode", path/to/original/doc)
```

The Barcode generator is provided in a distinct class to allow it to be used to generate stand alone barcode PDFs if required.

Basic usage:
```python
    generator = Barcode()
    generator.generate_barcode("Barcode")
```
