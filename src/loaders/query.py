


class Query:
    def __init__(self):
        self.query: str = None
        
    def all_matches(self, table_name):
        self.query = f'''
            SELECT *
            FROM {table_name}
            '''
    
    def leagues_specific(self, table_name, leagues, countries):
        leagues_q = self.list_to_sql(leagues)
        leagues_q = f"league IN {leagues_q}" if leagues_q else None

        countries_q = self.list_to_sql(countries)
        countries_q = f"country IN {countries_q}" if countries_q else None

        filter = ' AND '.join([i for i in [leagues_q, countries_q] if i])
        filter = f'WHERE {filter}' if filter else ''

        self.query = f'''
            SELECT *
            FROM {table_name}
            {filter}
            '''
        
    def list_to_sql(self, list_):
        if len(list_) > 0:
            str_list = [str(i) for i in list_]
            return "('" + "', '".join(str_list) + "')"
        else:
            return ''