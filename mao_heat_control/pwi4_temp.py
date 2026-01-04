'''Module for requesting temperature readings from PWI4'''

import win32com.client
import urllib.request

class PWI4:
    def __init__(self):
        '''Create a COM object conected to PWI3 for quick temperature retrieval'''
        self.com = win32com.client.Dispatch("PlaneWave.AutoFocus")
        self.port = self.com.Port

    def getPrimaryTemp(self):
        '''Gets the current tempreature of the Pirmay Mirror in C'''
        #Default to a very high temperature to turn off heater.
        temp = 999.0
        try:
            contents = urllib.request.urlopen("http://localhost:8220/temperatures/pw1000").read()
            data_dict = {}
            for line in contents.decode('utf-8').strip().split('\n'):
                key, value = line.split('=')
                data_dict[key] = float(value) # Convert the value to a float

            # Select the value for 'temperature.primary'
            temp = data_dict.get('temperature.primary')
        except Exception as e:
            print("Unable to get Temperature: ", e)
            pass

        #return self.com.GetTemperatureByName("Primary.EFA")
        return temp

if __name__ == "__main__":
    '''testing'''
    p = PWI4()
    print("DewPoint %.1f" % p.getPrimaryTemp())
