import socket

class ApcControllerConnection:
    def __init__(self, apcSocket):
        self.socket = apcSocket

    def turnOnOutlet(self, i):
        '''Sends command for turning on the outlet #i'''
        self.socket.sendall(b"on %d\r\n" % i)
        ApcController.expect(self.socket, "APC> ")

    def turnOffOutlet(self, i):
        '''Sends command for turning off the outlet #i'''
        self.socket.sendall(b"off %d\r\n" % i)
        ApcController.expect(self.socket, "APC> ")


class ApcController:
    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.connection = None

    def __enter__(self):
        '''Open APC CLI socket, Login, and wait for prompt'''
        if self.connection:
            raise Exception("ApcControllerConnection already established.")
        apcSocket = socket.create_connection((self.address, 23), 10)
        apcSocket.recv(4) #ditch the initial telnet garbage
        self.expect(apcSocket, "User Name : ")
        apcSocket.sendall(self.username.encode("utf-8")+b"\r\n")
        self.expect(apcSocket, "Password  : ")
        apcSocket.sendall((self.password + " -c").encode("utf-8")+b"\r\n")
        self.expect(apcSocket, "APC> ")
        self.connection = ApcControllerConnection(apcSocket)
        return self.connection

    def __exit__(self, exception_type, exception_value, traceback):
        '''Disconnect'''
        if (self.connection):
            self.connection.socket.close()
        self.connection = None

    @staticmethod
    def expect(sock, prompt):
        '''Waits for an expected prompt before returning'''
        last_prompt = ""
        while True:
            check_val = sock.recv(256).decode("utf-8")
            if len(check_val) == 0:
                raise Exception("Expect Empty! Closed connection?")
            #only look for data after a newline
            x = check_val.splitlines()
            if len(x) > 1:
                last_prompt = x[-1]
            else:
                last_prompt += x[0]
            if last_prompt == prompt:
                return True

    def turnOnOutlet(self, i):
        with self as c:
            c.turnOnOutlet(i)

    def turnOffOutlet(self, i):
        with self as c:
            c.turnOffOutlet(i)
