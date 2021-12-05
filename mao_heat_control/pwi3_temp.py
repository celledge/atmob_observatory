'''Module for requesting temperature readings from PWI3'''

import win32com.client

class PWI3:
    def __init__(self):
        '''Create a COM object conected to PWI3 for quick temperature retrieval'''
        self.com = win32com.client.Dispatch("PlaneWave.AutoFocus")

    def getPrimaryTemp(self):
        '''Gets the current tempreature of the Pirmay Mirror in C'''
        return self.com.GetTemperatureByName("Primary.EFA")

if __name__ == "__main__":
    '''testing'''
    p = PWI3()
    print("DewPoint %.1f" % p.getPrimaryTemp())
