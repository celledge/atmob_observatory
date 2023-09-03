'''Module for reading weather from ASCOM Observing Conditions Hub'''

import win32com.client

class Conditions:
    def __init__(self):
        '''Create a COM object conected to Observing Conditions Hub'''
        self.com = win32com.client.Dispatch("ASCOM.OCH.ObservingConditions")

    def __del__(self):
        if self.com:
            del self.com

    def getDewPoint(self):
        '''Gets the current dewpoint in C'''
        return self.com.DewPoint

if __name__ == "__main__":
    '''testing'''
    p = Conditions()
    print("DewPoint %.1f" % p.getDewPoint())
