from log import log

id_ = 0


def nextID():
    global id_

    ret_id = id_
    id_ += 1

    return ret_id


class Component:
    def __init__(self, type_, data):
        self.id = nextID()
        self.type = type_
        self.data = data

        log(f'Component#{self.id}', f'Created (type {self.type}).', 'debug')
