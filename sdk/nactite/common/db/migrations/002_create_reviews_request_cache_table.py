def get_sql():
    return '''
    CREATE TABLE
    IF NOT EXISTS reviews_request_cache (
        id TEXT PRIMARY KEY,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    '''
