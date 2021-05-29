from datetime import datetime

from skepticoin.files.chain import (
    read_chain_from_disk,
)

from .utils import (
    open_or_init_wallet,
    configure_logging_from_args,
    DefaultArgumentParser,
)

from ..params import SASHIMI_PER_COIN


def main() -> None:
    parser = DefaultArgumentParser()
    args = parser.parse_args()
    configure_logging_from_args(args)

    coinstate = read_chain_from_disk()
    wallet = open_or_init_wallet()
    print(
        wallet.get_balance(coinstate) / SASHIMI_PER_COIN, "SKEPTI at h. %s," % coinstate.head().height,
        datetime.fromtimestamp(coinstate.head().timestamp).isoformat())
