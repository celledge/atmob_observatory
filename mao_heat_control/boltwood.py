'''Module for reading weather from Boltwood Cloud Monitor via Clarity II'''

import win32com.client
import time

class Boltwood:
    def __init__(self):
        '''Create a COM object conected to PWI3 for quick temperature retrieval'''
        self.com = None
        self.dataReady = False
        self.establishCom()

    def __del__(self):
        if self.com:
            del self.com

    def establishCom(self):
        if not self.com:
            self.dataReady = False
            try:
                self.com = win32com.client.Dispatch("ClarityII.CloudSensorII")
            except:
                self.com = None
        else:
            if not self.dataReady:
                try:
                    self.dataReady = self.com.DataReady()
                except:
                    self.com = None

    def getDewPoint(self):
        '''Gets the current dewpoint in C'''
        self.establishCom()
        if not self.dataReady:
            return float("NaN")
        try:
            return self.com.DewPointT
        except:
            self.com = None
            return float("NaN")

if __name__ == "__main__":
    '''testing'''
    b = Boltwood()
    while not b.com.DataReady():
        time.sleep(0.1)
    print("DewPoint %.1f" % b.getDewPoint())
    del b
