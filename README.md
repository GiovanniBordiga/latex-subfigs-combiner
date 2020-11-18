# LaTeX Subfigs Combiner

Python script for combining LaTeX figures composed of subfigures

---

## What

This package provides a simple Python script for combining LaTeX figures composed of subfigures into single PDF files, i.e. one PDF per composite figure.

## Why

If you have ever tried to publish on scientific journals, you have probably encountered at least _one_ journal that either does not accept LaTeX [`subfigures`](https://www.ctan.org/pkg/subcaption) or will combine your composite figures during production with a very high chance of making a mess (both scenarios are completely unreasonable, but yet they happen sometimes).
Of course, you really like those shiny composite LaTeX figures and do not want to waste time painstakingly stitching them together by hand (e.g. using Inkscape).
This Python script provides an hands-free automated solution to this problem.

## How

The job is done by parsing the given TeX file, extracting the preamble, setting the page style to empty, extracting the `figure` environments that contain `subfigures`, compiling to a PDF via [`latexmk`](https://www.ctan.org/pkg/latexmk/), and then crop each figure to a separate PDF file using [`pdfcrop`](https://www.ctan.org/pkg/pdfcrop).

---

## Installation

Easy peasy via `pip` or equivalent

```bash
pip install latex-subfigs-combiner
```

## Usage

In a terminal, simply run `combine-subfigs` on your LaTeX main file

```bash
combine-subfigs /path/to/my/awesome/paper.tex
```

This will produce all the composite figures in a directory named `composite-figures` at the location you called the script from.

By default, the output figures will be named as `fig_1.pdf`, `fig_2.pdf`, etc.
If you want to change the output directory or the filename prefix `fig_` of the figures, you can use the optional arguments `--target_dir` and `--prefix`, respectively.
Execute `combine-subfigs -h` for more details.

---

## Tips are welcomed! :love_you_gesture:

If you found this useful, feel free to offer me a beer :beer: via [PayPal](https://paypal.me/GiovanniBordiga/3 "Send tip via PayPal") or [send me a few sats](http://deadcat.epizy.com/ "Send tip via LN") :zap:.
