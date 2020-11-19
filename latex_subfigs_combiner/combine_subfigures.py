#!/usr/bin/env python3

import argparse
import glob
import os
import re
import subprocess
from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter

from . import __version__


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
                    help="Target directory for output figures. Default is \"./composite-figures\".", type=str, default="./composite-figures")
parser.add_argument("--prefix", "-p",
                    help="Prefix for naming output figures. Default is \"fig_\".", type=str, default="fig_")
parser.add_argument("--version", "-v", action="version",
                    version="%(prog)s v{version}".format(version=__version__), help="Shows current version.")

args = parser.parse_args()
texFilePath = Path(args.tex_source)     # input tex file
targetPath = Path(args.target_dir)      # target directory where final figures will be collected
prefix = args.prefix                    # prefix for figure filenames


def extractCompositeFigureStrings(latexString):
    """
    Returns a list of latex figures as strings stripping out captions.
    """

    # extract figures
    figureStrings = re.findall(r"\\begin{figure}.*?\\end{figure}", latexString, re.S)
    # filter composite figures only and remove captions (preserving captions in subfigures)
    figureStrings = [
        re.findall(r"\\begin{figure}.*(?=\n.*\\caption)", figureString, re.S)[0] + "\n\\end{figure}"
        for figureString in figureStrings if "\\begin{subfigure}" in figureString
    ]
    return figureStrings


def parseTexFile(texFilePath):
    """
    Parses the TeX file, returning the list of composite figures and the preamble.
    """

    # read in tex file
    with open(texFilePath) as latex:
        latexString = latex.read()

    # remove all commented code
    latexStringCleaned = "\n".join(re.findall(r"^\s*(?!%)\S.*$", latexString, re.MULTILINE))
    # extract the preamble
    preambleString = re.findall(r"^(.*?)\\begin{document}", latexStringCleaned, re.S)[0]
    # set page style to empty in order to crop only the figure
    preambleString = preambleString + "\\pagestyle{empty}\n"
    # extract the figure containing subfigures
    figureStrings = extractCompositeFigureStrings(latexStringCleaned)

    return preambleString, figureStrings


def compileLatex(preambleString, figureStrings, compilationPath, tmpFilename):
    """
    Compiles the auxiliary TeX file with one figure per page.
    """

    beginDocument = "\\begin{document}\n"
    endDocument = "\\end{document}\n"

    # compile auxiliary tex file with one figure per page
    # TODO: would be nice to compile only those figures that have changes since last compilation (can be done by storing the list figureStrings)
    tmpTexPath = compilationPath / (tmpFilename + ".tex")
    with open(tmpTexPath, "w") as tmpTex:
        tmpTex.write(preambleString + beginDocument + "\n\\pagebreak\n".join(figureStrings) + endDocument)

    # compile auxiliary tex file
    subprocess.run(["latexmk", "-pdf", "-silent", "-cd", str(tmpTexPath)])


def createCompositeFigures(targetPath, figNames, tmpFilename):
    """
    Creates the composite figures in targetPath and clean up auxiliary files.
    """

    # create target directory
    try:
        os.mkdir(targetPath)
    except OSError:
        # clean up target directory
        for file in targetPath.iterdir():
            os.remove(file)

    # extract figures from pages
    tmpPDFPath = Path(tmpFilename + ".pdf")
    tmpPDF = PdfFileReader(open(tmpPDFPath, "rb"))
    for i in range(tmpPDF.numPages):
        # extract i-th page containing figure to crop
        output = PdfFileWriter()
        output.addPage(tmpPDF.getPage(i))
        pagePath = Path(tmpFilename + "_page.pdf")
        with open(pagePath, "wb") as outputStream:
            output.write(outputStream)
        # crop figure and move it into target directory
        subprocess.run(["pdfcrop", str(pagePath), str(targetPath / figNames[i])])


def cleanUp(compilationPath, tmpFilename):
    """
    Deletes auxiliary files in both current path and compilationPath.
    """

    for file in glob.glob(tmpFilename + "*"):
        os.remove(file)  # clean up current directory
    os.remove(compilationPath / (tmpFilename + ".tex"))  # remove auxiliary tex file


def main():
    """
    Executes main program.
    """

    # parse tex file extracting composite figures and preable
    preambleString, figureStrings = parseTexFile(texFilePath)

    # compile auxiliary tex file with one figure per page
    tmpFilename = "comb_fig_tmp"  # name of auxiliary files
    compileLatex(preambleString, figureStrings, compilationPath=texFilePath.parent, tmpFilename=tmpFilename)

    # create composite figures
    figNames = [prefix + str(i + 1) + ".pdf" for i in range(len(figureStrings))]  # figure filenames for output
    createCompositeFigures(targetPath, figNames, tmpFilename=tmpFilename)

    # clean up auxiliary files
    cleanUp(compilationPath=texFilePath.parent, tmpFilename=tmpFilename)


# entrypoint for cli invocation
if __name__ == "__main__":
    main()
