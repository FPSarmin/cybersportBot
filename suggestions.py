import pandas


class Suggestions:
    def __init__(self, df: pandas.DataFrame):
        self.df = df

    @staticmethod
    def from_csv_file(csv_path: str):
        return Suggestions(
            pandas.read_csv(csv_path)
        )

    @staticmethod
    def create_empty_db():
        df = pandas.DataFrame(
            {
                'user_id': [],
                'suggestion': []
            }
        )
        df.to_csv('suggestions_db.csv', encoding='utf-8', index=False)
        return Suggestions.from_csv_file('suggestions_db.csv')

    def add_suggestion(self, user_id: int, suggestion: str):
        self.df = self.df.append({
            'user_id': user_id,
            'suggestion': suggestion
        }, ignore_index=True)
        self.df.to_csv('suggestions_db.csv', encoding='utf-8', index=False)


try:
    suggestions = Suggestions.from_csv_file('suggestions_db.csv')
except BaseException:
    suggestions = Suggestions.create_empty_db()
