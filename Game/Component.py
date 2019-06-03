from log import log

id_ = 0


def nextID():
    global id_

    ret_id = id_
    id_ += 1

    return ret_id


class Component:
    def __init__(self, parent, type_, data):
        self.id = nextID()
        self.parent = parent
        self.type = type_
        self.data = data

        log(f'Component#{self.id}', f'Created (type {self.type}).', 'debug')

    def get(self, data_name):
        if data_name in self.data:
            return self.data[data_name]

    def toJSON(self):
        return {
            'id': self.id,
            'data': self.data
        }
