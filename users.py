import pandas
import datetime


class Users:
    def __init__(self, df: pandas.DataFrame):
        self.df = df

    @staticmethod
    def from_csv_file(csv_path: str):
        return Users(
            pandas.read_csv(csv_path)
        )

    @staticmethod
    def create_empty_db():
        df = pandas.DataFrame(
            {
                'user_id': [],
                'state': [],
                'dota2': [],
                'csgo': [],
                'pubg': [],
                'games': [],
                'other': [],
                'lol': [],
                'valorant': [],
                'apex-legends': [],
                'fifa': [],
                'overwatch': [],
                'silent_begin': [],
                'silent_end': []
            }
        )
        df.to_csv('users_db.csv', encoding='utf-8', index=False)
        return Users.from_csv_file('users_db.csv')

    def __call__(self, user_id: int, tp: str) -> bool:
        return self.df['user_id' == user_id][tp]

    def subscribe_user(self, user_id: int, tp: str) -> bool:
        self.df.loc[self.df[self.df.user_id == user_id].index, tp] = \
            (self.df[self.df.user_id == user_id][tp] + 1) % 2
        self.df.to_csv("users_db.csv", encoding='utf-8', index=False)
        return self.df[self.df.user_id == user_id][tp]

    def change_state(self, user_id: int, state: int):
        self.df[self.df.user_id == user_id]['state'] = state
        self.df.to_csv("users_db.csv", encoding='utf-8', index=False)

    def find_user(self, user_id: int):
        return not self.df[self.df.user_id == user_id].empty

    def add_user(self, user_id: int):
        if len(self.df[self.df.user_id == user_id]) == 0:
            self.df = self.df.append({
                'user_id': user_id,
                'state': 0,
                'dota2': 0,
                'cs-go': 0,
                'pubg': 0,
                'games': 0,
                'others': 0,
                'lol': 0,
                'valorant': 0,
                'apex-legends': 0,
                'fifa': 0,
                'overwatch': 0,
                'silent_begin': 23,
                'silent_end': 8
            }, ignore_index=True)
            self.df.to_csv("users_db.csv", encoding='utf-8', index=False)

    def get_sub_status(self, user_id: int, tp: str):
        return self.df.loc[self.df.user_id == user_id, tp].item()

    def remove_user(self, user_id: int):
        self.df = self.df[self.df.user_id != user_id]
        self.df.to_csv("users_db.csv", encoding='utf-8', index=False)

    def get_users_ids(self):
        return self.df['user_id'].tolist()

    def is_in_time(self, user_id: int):
        now = datetime.datetime.now()
        silent_begin = now.replace(hour=int(self.df.loc[self.df.user_id == user_id, 'silent_begin'].item()))
        silent_end = now.replace(hour=int(self.df.loc[self.df.user_id == user_id, 'silent_end'].item()))
        print(silent_end > now > silent_begin)
        return silent_end > now > silent_begin

    def change_silent_begin(self, user_id: int, hour: int):
        self.df.loc[self.df[self.df.user_id == user_id].index, 'silent_begin'] = hour
        self.df.to_csv("users_db.csv", encoding='utf-8', index=False)

    def change_silent_end(self, user_id: int, hour: int):
        self.df.loc[self.df[self.df.user_id == user_id].index, 'silent_end'] = hour
        self.df.to_csv("users_db.csv", encoding='utf-8', index=False)


try:
    users = Users.from_csv_file('users_db.csv')
except BaseException:
    users = Users.create_empty_db()
