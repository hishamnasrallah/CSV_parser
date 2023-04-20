from core.database.settings.session_maker import DBSession


def crud(query):
    with DBSession() as db:
        db.add(query)
        db.commit()
        db.refresh(query)
        return query


class CRUD:

    def __init__(self):
        self._query = None
        self.db = None

    def db_conn(self):
        with DBSession() as db:
            self.db = db
            return self.db

    def add(self, _query):
        self._query = _query
        db = self.db_conn()
        db.add(self._query)
        db.commit()
        db.refresh(self._query)
        return self._query

    def get(self):
        pass

    def delete(self):
        pass

    def all(self):
        pass

    def filter(self, model, field, value):
        database = self.db_conn()
        result = database.query(eval(model)).filter(
            exec(model.eval(".field==value)")))
        return result
