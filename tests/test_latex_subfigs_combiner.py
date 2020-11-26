import glob
import shutil
import subprocess
from pathlib import Path

import toml
from latex_subfigs_combiner import __version__


def test_version():
    tomlVersion = toml.load(Path("./pyproject.toml")).get("tool").get("poetry").get("version")
    assert __version__ == tomlVersion


def test_script():

    # execute script with test parameters
    job = subprocess.run(["combine-subfigs", "./tests/data/paper.tex",
                          "--target_dir", "./tests/data/composite-figures"])
    assert job.returncode == 0

    # check number of figures produced
    numOutputFigs = len(glob.glob("./tests/data/composite-figures/*.pdf"))
    assert numOutputFigs == 5

    # clean up test output figures
    shutil.rmtree("./tests/data/composite-figures")
