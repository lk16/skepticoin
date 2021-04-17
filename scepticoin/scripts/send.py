from time import sleep
import argparse

from scepticoin.params import SASHIMI_PER_COIN
from scepticoin.signing import SECP256k1PublicKey
from scepticoin.wallet import save_wallet
from scepticoin.wallet import is_valid_address, parse_address, create_spend_transaction

from .utils import (
    initialize_peers_file,
    create_chain_dir,
    read_chain_from_disk,
    open_or_init_wallet,
    start_networking_peer_in_background,
    check_for_fresh_chain,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("amount", help="The amount of to send", type=int)
    parser.add_argument("denomination", help="'scepticoin' or 'sashimi'", choices=['scepticoin', 'sashimi'])
    parser.add_argument("address", help="The address to send to")
    args = parser.parse_args()

    value = args.amount * (SASHIMI_PER_COIN if args.denomination == 'scepticoin' else 1)

    if not is_valid_address(args.address):
        print("Invalid address")
        return

    create_chain_dir()
    coinstate = read_chain_from_disk()
    wallet = open_or_init_wallet()
    initialize_peers_file()
    thread = start_networking_peer_in_background(coinstate)

    # we need a fresh chain because our wallet doesn't track spending/receiving, so we need to look at the real
    # blockchain to know what we can spend.
    check_for_fresh_chain(thread)
    print("Chain up to date")

    target_address = SECP256k1PublicKey(parse_address(args.address))
    change_address = SECP256k1PublicKey(wallet.get_annotated_public_key("change"))
    save_wallet(wallet)

    transaction = create_spend_transaction(
        wallet,
        coinstate,
        value,
        0,  # we'll get to paying fees later
        target_address,
        change_address,
    )

    print("Broadcasting transaction on the network", transaction)
    thread.local_peer.network_manager.broadcast_transaction(transaction)

    print("Monitoring...")

    while True:
        sleep(5)

        # it's late and I'm too lazy for the efficient & correct implementation.
        coinstate = thread.local_peer.chain_manager.coinstate
        max_height = coinstate.head().height

        for i in range(10):
            block = coinstate.by_height_at_head()[max(max_height - i, 0)]
            if transaction in block.transactions:
                print("Transaction confirmed at", block.height, "with", i, "confirmation blocks")

                if i == 6:  # this is the magic number of confirmations according to the "literature" on the subject
                    thread.stop()
                    return