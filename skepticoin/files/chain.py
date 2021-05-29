from io import BytesIO
from typing import List
from skepticoin.utils import block_filename
import zipfile
import urllib.request
from pathlib import Path
from skepticoin.datatypes import Block
from skepticoin.coinstate import CoinState


CHAIN_PATH = Path('chain')


def read_chain_from_disk() -> CoinState:
    print("Reading chain from disk")

    coinstate = CoinState.zero()
    block_files: List[Path] = sorted(CHAIN_PATH.iterdir())

    for block_file in block_files:
        height = int(block_file.name.split("-")[0])
        if height % 1000 == 0:
            print(block_file.name)

        try:
            with open(block_file.absolute(), 'rb') as f:
                block = Block.stream_deserialize(f)
        except Exception as e:
            raise Exception("Corrupted block on disk: %s" % block_file.name) from e

        coinstate = coinstate.add_block_no_validation(block)

    return coinstate


def create_chain_dir() -> None:
    if CHAIN_PATH.exists():
        return

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
