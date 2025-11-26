# Generic output container
class OutputContainer:
    def __init__(self):
        self.records = []

    def add_record(self, record: dict):
        """
        record = {
            "property": None,
            "payee": None,
            "receipt_amount": None,
            "status": None,
            "timestamp": None
        }
        """
        self.records.append(record)

    def get_all(self):
        return self.records
