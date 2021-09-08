
class socket:

    def __init__(self, data):
        self.data = data

    def recv(self, buffer_size):
        return self.data

    def send(self, data):
        self.data = data

    def close(self):
        print('socket closed')