import sqlite3
import datetime
import time



def human_time(unixtime):
    return datetime.datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%d %H:%M:%S')


class logDB:
    def __init__(self):
        self.con = sqlite3.connect('log.db')
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS "Messages"
                    ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
                    "user_name" VARCHAR(100),
                    "user_id" VARCHAR(100),
                    "date" VARCHAR(100),
                    "human_date" VARCHAR(100),
                    "file" VARCHAR(100),
        			"first" INTEGER);
                    ''')

    def add_message(self, user_name, user_id, date, file_path):
        self.cur.execute('SELECT * FROM Messages WHERE user_id ={0}'.format(user_id))
        first_flag = 1
        if self.cur.fetchone():
            first_flag = 0

        self.cur.execute('''INSERT INTO  
        				Messages(user_name, user_id, date, human_date, file, first) 
        				VALUES ('{0}','{1}','{2}','{3}','{4}', '{5}')'''.format(user_name, user_id, date, human_time(date), file_path, first_flag))
        self.con.commit()
        return

    def get_status(self, hours_count):
        time_right = time.time()
        time_left = time_right - hours_count*60*60

        self.cur.execute('SELECT COUNT(DISTINCT(id)) FROM Messages')
        count_requests_all = int(self.cur.fetchone()[0])

        self.cur.execute('SELECT COUNT(DISTINCT(user_id)) FROM Messages')
        count_users_all = int(self.cur.fetchone()[0])

        self.cur.execute('SELECT COUNT(DISTINCT user_id) FROM Messages Where date >={0} AND date<={1}'.format(time_left, time_right))
        count_users = int(self.cur.fetchone()[0])

        self.cur.execute('SELECT * FROM Messages Where date >={0} AND date<={1}'.format(time_left, time_right))
        count_requests = len(self.cur.fetchall())

        self.cur.execute('SELECT * FROM Messages Where date >={0} AND date<={1} AND first =1'.format(time_left, time_right))
        count_newcomer = len(self.cur.fetchall())

        status_24 = '''In the last {0} hours: \n   {1} unique users; \n   {2} users; \n   {3} requests.\n________________________'''.format(hours_count, count_newcomer, count_users, count_requests)
        status_all ='''At All: \n   {0} users; \n   {1} requests.\n________________________'''.format(count_users_all, count_requests_all)
        status = status_24 + '\n\n' + status_all
        return status

    def get_user_list(self):
        self.cur.execute('SELECT DISTINCT(user_id) FROM Messages')
        user_list = self.cur.fetchall()
        return [int(user[0]) for user in user_list]
