


class Query:
    def __init__(self):
        self.query: str = None
        
    def all_matches(self, table_name):
        self.query = f'''
            SELECT *
            FROM {table_name}
            '''
    
    def leagues_specific(self, table_name, leagues):
        self.query = f'''
            SELECT *
            FROM {table_name}
            WHERE league in {leagues}
            '''