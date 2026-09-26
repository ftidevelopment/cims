from app.extensions import db


class TransactionManager:

    def __enter__(self):
        return self

    def flush(self):
        db.session.flush()

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()

    def __exit__(self, exc_type, exc_value, traceback):

        if exc_type is None:
            self.commit()
        else:
            self.rollback()

        return False

    def refresh(self, entity):
        db.session.refresh(entity)

    def add(self, entity):
        db.session.add(entity)