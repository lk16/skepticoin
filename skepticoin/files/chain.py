from io import BytesIO
import os
from skepticoin.utils import block_filename
import zipfile
import urllib.request
from pathlib import Path
from skepticoin.datatypes import Block
from skepticoin.coinstate import CoinState


def read_chain_from_disk() -> CoinState:
    print("Reading chain from disk")
    coinstate = CoinState.zero()
    for filename in sorted(os.listdir('chain')):
        height = int(filename.split("-")[0])
        if height % 1000 == 0:
            print(filename)

        try:
            with open(Path("chain") / filename, 'rb') as f:
                block = Block.stream_deserialize(f)
        except Exception as e:
            raise Exception("Corrupted block on disk: %s" % filename) from e

        coinstate = coinstate.add_block_no_validation(block)

    return coinstate


def create_chain_dir() -> None:
    if not os.path.exists('chain'):
        print("Pre-download blockchain from trusted source to 'blockchain-master'")
        with urllib.request.urlopen("https://github.com/skepticoin/blockchain/archive/refs/heads/master.zip") as resp:
            with zipfile.ZipFile(BytesIO(resp.read())) as zip_ref:
                print("Extracting...")
                zip_ref.extractall()

        print("Created new directory for chain")
        os.rename('blockchain-master', 'chain')


def save_block(block: Block) -> None:
    with open(Path('chain') / block_filename(block), 'wb') as f:
        f.write(block.serialize())
