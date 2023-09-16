
class Request(object):

    def __int__(self, topic, data):
        self._topic = topic
        self._data = data

    def raw(self):
        return self._data

    def data(self):
        data_array = bytes(self._data)
        data_string = data_array.decode('utf-8')
        return data_string
