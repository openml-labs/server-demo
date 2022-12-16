if __name__ == "__main__":
    from setup import connect_to_database, populate_database

    engine = connect_to_database(
        "mysql://root:ok@127.0.0.1:3307/aiod",
        delete_first=True,
    )
    populate_database(engine)
