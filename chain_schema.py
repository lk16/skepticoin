import sqlite3


def main() -> None:
    con = sqlite3.connect('chain.db')
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE "block" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "hash" BLOB,
        "height" INTEGER
    )
    """)

    cur.close()


if __name__ == "__main__":
    main()
