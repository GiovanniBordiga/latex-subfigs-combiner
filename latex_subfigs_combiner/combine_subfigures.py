#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import glob
from PyPDF2 import PdfFileReader, PdfFileWriter


# arguments handling and parsing
parser = argparse.ArgumentParser(
    description="""
    Combines LaTeX figures composed of subfigures into single PDF files, i.e. one PDF per composite figure.
    This is done by parsing the "text_source" TeX file, extracting the preamble, setting the page style to empty,
    extracting the figure environments that contain subfigures, compiling to a PDF via latexmk, and then crop each figure to a separate PDF file using pdfcrop.
    """
)
parser.add_argument("tex_source",
                    help="Source TeX file containing composite figures to be combined.", type=str)
parser.add_argument("--target_dir", "-d",
                    help="Target directory for output figures. Default is \"./combined-figures\".", type=str, default="./combined-figures")
parser.add_argument("--prefix", "-p",
                    help="Prefix for naming output figures. Default is \"fig_\".", type=str, default="fig_")

args = parser.parse_args()
texFile = args.tex_source       # input tex file
targetPath = args.target_dir    # target directory where final figures will be collected
prefix = args.prefix            # prefix for figure figNames


def extractCompositeFigureStrings(latexString):
    """
    Returns a list of latex figures as strings stripping out captions
    """
    # extract figures
    figureStrings = re.findall(r"\\begin{figure}.*?\\end{figure}", latexString, re.S)
    # filter composite figures only i.e. containing subfigures
    figureStrings = [figureString for figureString in figureStrings if "\\begin{subfigure}" in figureString]
    # remove captions (preserving captions in subfigures)
    figureStrings = [
        re.findall(r"\\begin{figure}.*(?=\n.*\\caption)", figureString, re.S)[0] + "\n\\end{figure}"
        for figureString in figureStrings
    ]
    return figureStrings


def main():
    """
    Executes main program
    """

    # read in tex file
    with open(texFile) as latex:
        latexString = latex.read()

    # remove all commented code
    latexStringCleaned = "\n".join(re.findall(r"^\s*(?!%)\S.*$", latexString, re.MULTILINE))
    # extract the preamble
    preambleString = re.findall(r"^(.*?)\\begin{document}", latexStringCleaned, re.S)[0]
    # set page style to empty in order to crop only the figure
    preambleString = preambleString + "\\pagestyle{empty}\n"
    # extract the figure containing subfigures
    figureStrings = extractCompositeFigureStrings(latexStringCleaned)

    beginDocument = "\\begin{document}\n"
    endDocument = "\\end{document}\n"

    tmpFilename = "comb_fig_tmp"  # name of auxiliary files
    figNames = [prefix + str(i + 1) + ".pdf" for i in range(len(figureStrings))]  # figure filenames for output

    # compile auxiliary tex file with one figure per page
    # TODO: would be nice to compile only those figures that have changes since last compilation (can be done by storing the list figureStrings)
    with open(tmpFilename + ".tex", "w") as tmpTex:
        tmpTex.write(preambleString + beginDocument + "\n\\pagebreak\n".join(figureStrings) + endDocument)
    # compile auxiliary tex files
    subprocess.run(["latexmk", "-pdf", tmpFilename])

    # create target directory
    try:
        os.mkdir(targetPath)
    except OSError:
        # clean up target directory
        for file in glob.glob(targetPath + "/*"):
            os.remove(file)

    # extract figures from pages
    tmpPDF = PdfFileReader(open(tmpFilename + ".pdf", "rb"))
    for i in range(tmpPDF.numPages):
        # extract i-th page containing figure to crop
        output = PdfFileWriter()
        output.addPage(tmpPDF.getPage(i))
        with open(tmpFilename + "_page.pdf", "wb") as outputStream:
            output.write(outputStream)
        # crop figure and move it into target directory
        subprocess.run(["pdfcrop", tmpFilename + "_page.pdf", targetPath + "/" + figNames[i]])

    # clean up auxiliary files
    for file in glob.glob(tmpFilename + "*"):
        os.remove(file)


# entrypoint
if __name__ == "__main__":
    main()
