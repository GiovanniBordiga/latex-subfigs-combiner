# LaTeX Subfigs Combiner

Python script for combining LaTeX figures composed of subfigures

## What

This package provides a simple Python script for combining LaTeX figures composed of subfigures into single PDF files, i.e. one PDF per composite figure.

## Why

If you have ever tried to publish on scientific journals, you have probably encountered at least *one* journal that either does not accept LaTeX `subfigures` or will combine your composite figures during production with a very high chance of making a mess (both scenarios are completely unreasonable to me, but yet sometimes they happen).
Of course, you really like those shiny composite LaTeX figures and do not want to waste time painstakingly stitching them together by hand (e.g. using InkScape).
This Python script provides an hands-free automated solution to this problem.

## How

The job is done by parsing the given TeX file, extracting the preamble, setting the page style to empty, extracting the `figure` environments that contain `subfigures`, compiling to a PDF via `latexmk`, and then crop each figure to a separate PDF file using `pdfcrop`.

## Usage

<!-- TODO -->