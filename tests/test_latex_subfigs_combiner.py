from latex_subfigs_combiner import __version__
import subprocess
import glob


def test_version():
    assert __version__ == '0.1.0'


def test_script():

    # execute script with test parameters
    job = subprocess.run(["combine-subfigs", "./tests/data/latex-project/paper.tex", "--target_dir",
                          "./tests/data/combined-figures"])
    assert job.returncode == 0

    # check number of figures produced
    numOutputFigs = len(glob.glob("./tests/data/combined-figures/*.pdf"))
    assert numOutputFigs == 5
