from io import BytesIO
import os
from typing import Dict, List, Optional
from skepticoin.utils import block_filename
import zipfile
import urllib.request
from pathlib import Path
from skepticoin.datatypes import Block
from skepticoin.coinstate import CoinState
import tarfile

"""
>>> with tarfile.open('dump.tar.gz', 'r:gz') as f:
...    for member in f.getmembers():
...       print(f.extractfile(member).read())

with tarfile.open('00000000.tar.gz', 'r:gz') as f:
    for member in f.getmembers()[:10]:
        print(member)
"""


CHAIN_PATH = Path('chain')

BLOCKS_PER_TAR_FILE = 10000

def _store_chain_as_tar() -> None:

    os.chdir(CHAIN_PATH)

    tar: Optional[tarfile.TarFile] = None
    prev_tar_name = ''

    for path in sorted(Path('.').iterdir()):
        if path.name.endswith('tar.gz'):
            continue

        height = int(path.name.split("-")[0])
        tar_height = height - (height % BLOCKS_PER_TAR_FILE)
        tar_name = f'{tar_height:08d}.tar.gz'

        if (not tar) or prev_tar_name != tar_name:
            if tar:
                tar.close()

            prev_tar_name = tar_name
            tar = tarfile.open(tar_name, 'w:gz')
            print(f"Compressing chain: creating {tar_name}")

        tar.add(path)

    if tar:
        tar.close()

    for block_file in Path('.').iterdir():
        if not block_file.name.endswith('tar.gz'):
            block_file.unlink()

    os.chdir('..')


def read_chain_from_disk() -> CoinState:
    print(f"Checking if {CHAIN_PATH} directory exists")

    if not CHAIN_PATH.exists():
        _create_chain_dir()

    _store_chain_as_tar()

    print("Reading chain from disk")

    coinstate = CoinState.zero()

    for tar_path in sorted(CHAIN_PATH.iterdir()):
        if not tar_path.name.endswith('tar.gz'):
            continue

        print(f"Loading chain from {tar_path}")

        with tarfile.open(tar_path.absolute(), 'r:gz') as f:
            for member in f.getmembers():
                try:
                    block = Block.stream_deserialize(f.extractfile(member))  # type: ignore
                except Exception as e:
                    raise Exception("Corrupted block on disk: %s, %s" % (tar_path.name, member)) from e

                coinstate = coinstate.add_block_no_validation(block)

    return coinstate


def _create_chain_dir() -> None:
    print(f"Creating {CHAIN_PATH} directory")

    print("Downloading partial blockchain from trusted source to 'blockchain-master' folder")

    with urllib.request.urlopen("https://github.com/skepticoin/blockchain/archive/refs/heads/master.zip") as resp:
        with zipfile.ZipFile(BytesIO(resp.read())) as zip_ref:
            print("Extracting...")
            zip_ref.extractall()

    Path('blockchain-master').rename(CHAIN_PATH)
    print("Created new directory for chain")


def save_block_to_disk(block: Block) -> None:
    with open(CHAIN_PATH / block_filename(block), 'wb') as f:
        f.write(block.serialize())
