def dfs_to_conn(conn_dfs, index=False):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    for table_name, df in conn_dfs.items():
        # df.rename_axis(index='index').to_sql(table_name, conn, if_exists='replace')
        df.to_sql(table_name, conn, if_exists='replace', index=index)
    return conn
