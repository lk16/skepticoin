import immutables
import sqlite3


def main() -> None:
    con = sqlite3.connect('chain.db')
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE "block" (
        "hash" BLOB PRIMARY KEY,
        "height" INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE "transaction_outputs" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        block_hash BLOB,
        transaction_hash BLOB,
        output_index INTEGER,
        FOREIGN KEY (block_hash) REFERENCES block (hash)
    )
    """)

    cur.close()


# block_by_hash: immutables.Map[bytes, Block]
# block_by_height_by_hash: immutables.Map[bytes, immutables.Map[int, Block]]

unspent_transaction_outs_by_hash: immutables.Map[bytes, immutables.Map[OutputReference, Output]]
heads: immutables.Map[bytes, Block]
public_key_balances_by_hash: immutables.Map[bytes, immutables.Map[PublicKey, PKBalance]]


if __name__ == "__main__":
    main()
