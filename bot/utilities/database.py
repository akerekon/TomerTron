import sqlite3


class Database:
    def __init__(self) -> None:
        con = sqlite3.connect("find_name_from_slack_id.db")
        cur = con.cursor()
        self.execute = cur.execute
        self.commit = con.commit
        self.close = con.close
    
    def close(self):
        self.close()
    
    def create_new_table(self):
        self.execute("CREATE TABLE IF NOT EXISTS slack_id(slack_id, name)")
        self.commit()

    def set_connection(self, name, slack_id):
        self.execute("INSERT OR REPLACE INTO slack_id(slack_id, name) VALUES ('" + slack_id + "', '" + name + "')")
        self.commit()

    def delete_connection(self, slack_id):
        self.execute("DELETE FROM slack_id WHERE slack_id = \"" + slack_id + "\"")
        self.commit()

    def get_names(self):
        return self.execute("SELECT name FROM slack_id").fetchall()

    def get_slack_id_from_name(self, name):
        return self.execute("SELECT slack_id FROM slack_id WHERE name LIKE '%" + name + "%'").fetchone()

    def get_name_from_slack_id(self, slack_id):
        return self.execute("SELECT name, slack_id FROM slack_id sid WHERE sid.slack_id = \"" + slack_id + "\"").fetchone()
