#!python
''' MAO Heat Controller

MAO heat controller is an app that will watch temperature of the primary mirror
plus weather conditions to determine if the wall heaters should be enabled.

Oddity in APC strip is that when remote access is used, it will disconnect other logins
including the web interface.
'''

import apc_controller
from config import mao_heat_apc_ip, mao_heat_apc_user, mao_heat_apc_password, mao_heat_apc_outlet
from config import mao_mirror_temp_offset, mao_mirror_temp_offset_hyst

mao_heat_apc = apc_controller.ApcController(mao_heat_apc_ip, mao_heat_apc_user, mao_heat_apc_password)

mao_heat_icon = None

heat_enabled = False

import threading
import queue
import time
import enum
class HeatStates(enum.Enum):
    HEAT_ALWAYS_ON = enum.auto()
    HEAT_ALWAYS_OFF = enum.auto()
    HEAT_AUTO = enum.auto()
    HEAT_TIMER = enum.auto()
    HEAT_QUIT = enum.auto()

def mao_heat_on():
    '''Enables the Heaters'''
    global heat_enabled
    mao_heat_apc.turnOnOutlet(mao_heat_apc_outlet)
    heat_enabled = True
    if mao_heat_icon:
        mao_heat_icon.notify("Heaters On")

def mao_heat_off():
    '''Disables the Heaters'''
    global heat_enabled
    mao_heat_apc.turnOffOutlet(mao_heat_apc_outlet)
    heat_enabled = False
    if mao_heat_icon:
        mao_heat_icon.notify("Heaters Off")

def mao_heat_hyst(mirror_temp, dew_point):
    '''Compares Primary Mirror Temperature to Dew Point with hysteresis'''
    if heat_enabled:
        if mirror_temp > (dew_point + mao_mirror_temp_offset_hyst):
            mao_heat_off()
    else:
        if mirror_temp < (dew_point + mao_mirror_temp_offset):
            mao_heat_on()

runloop_queue = queue.Queue(4)

def mao_heat_timer():
    '''Started to run a periodic timer for the runloop'''
    time.sleep(10) #First one is short
    while True:
        runloop_queue.put(HeatStates.HEAT_TIMER)
        time.sleep(60*10) #10 minutes

mao_mirror_temp = "n/a"
mao_dew_point = "n/a"

def mao_heat_runloop():
    '''Started in a separate thread to handle events and timer'''
    try:
        import pwi3_temp
        import boltwood
        global mao_mirror_temp
        global mao_dew_point
        mirror = pwi3_temp.PWI3() #create object to read mirror temp
        mirror_temp = mirror.getPrimaryTemp()
        weather = boltwood.Boltwood() #create object to read dew point
        dew_point = weather.getDewPoint()
        stop = False
        local_state = HeatStates.HEAT_ALWAYS_OFF
        threading.Thread(target=mao_heat_timer, daemon=True).start() #runloop timer
        while not stop:
            mao_mirror_temp = "%.1f\N{DEGREE SIGN}C" % mirror_temp
            mao_dew_point = "%.1f\N{DEGREE SIGN}C" % dew_point
            mao_heat_icon.update_menu()
            event = runloop_queue.get()
            print("event: %s" % event, flush=True)
            if event == HeatStates.HEAT_ALWAYS_ON:
                local_state = HeatStates.HEAT_ALWAYS_ON
                mao_heat_on()
            elif event == HeatStates.HEAT_ALWAYS_OFF:
                local_state = HeatStates.HEAT_ALWAYS_OFF
                mao_heat_off()
            elif event == HeatStates.HEAT_AUTO:
                local_state = HeatStates.HEAT_AUTO
                #timer will get to us later
            elif event == HeatStates.HEAT_TIMER:
                dew_point = weather.getDewPoint() #update interesting values
                mirror_temp = mirror.getPrimaryTemp()
                if local_state == HeatStates.HEAT_AUTO:
                    mao_heat_hyst(mirror_temp, dew_point)
            elif event == HeatStates.HEAT_QUIT:
                mao_heat_off()
                stop = True
    except:
        mao_heat_icon.stop()
        raise

# This stuff is for the Windows System Tray
import pystray


def create_image():
    from PIL import Image, ImageDraw
    # Generate an image and draw a pattern
    width = 100
    height = 100
    image = Image.new('RGB', (width, height), "red")
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill="green")
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill="green")
    return image

heat_selected = HeatStates.HEAT_ALWAYS_OFF
def select_heat_off(icon, item):
    global heat_selected
    if heat_selected != HeatStates.HEAT_ALWAYS_OFF:
        heat_selected = HeatStates.HEAT_ALWAYS_OFF
        runloop_queue.put(HeatStates.HEAT_ALWAYS_OFF)

def select_heat_on(icon, item):
    global heat_selected
    if heat_selected != HeatStates.HEAT_ALWAYS_ON:
        heat_selected = HeatStates.HEAT_ALWAYS_ON
        runloop_queue.put(HeatStates.HEAT_ALWAYS_ON)

def select_heat_auto(icon, item):
    global heat_selected
    if heat_selected != HeatStates.HEAT_AUTO:
        heat_selected = HeatStates.HEAT_AUTO
        runloop_queue.put(HeatStates.HEAT_AUTO)

def heat_off_check(item):
    return heat_selected == HeatStates.HEAT_ALWAYS_OFF

def heat_on_check(item):
    return heat_selected == HeatStates.HEAT_ALWAYS_ON

def heat_auto_check(item):
    return heat_selected == HeatStates.HEAT_AUTO

def do_exit(icon, item):
    icon.stop()

def current_mirror_temp(item):
    return "Dew Point: %s" % mao_dew_point

def current_dew_point(item):
    return "Mirror T: %s" % mao_mirror_temp

def create_menu():
    menu = pystray.Menu(
        pystray.MenuItem(current_mirror_temp, lambda icon, item: 1, enabled = False),
        pystray.MenuItem(current_dew_point, lambda icon, item: 1, enabled = False),
        pystray.MenuItem('Heat always off', select_heat_off, checked=heat_off_check, radio = True),
        pystray.MenuItem('Heat always on', select_heat_on, checked=heat_on_check, radio = True),
        pystray.MenuItem('Heat auto hyst', select_heat_auto, checked=heat_auto_check, radio = True),
        pystray.MenuItem('Exit', do_exit)
    )
    return menu

if __name__ == "__main__":
    '''Executed!'''
    mao_heat_off(); #Start in known state
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'ATMoB.MAO_Heat')
    import pystray
    icon = pystray.Icon('MAO Heat')
    icon.icon = create_image()
    icon.menu = create_menu()
    icon.title = 'MAO Heat'
    mao_heat_icon = icon

    #runloop thread
    runloop = threading.Thread(target=mao_heat_runloop)
    runloop.start()

    icon.run()

    #exiting
    print("exiting", flush=True)
    runloop_queue.put(HeatStates.HEAT_QUIT)
    runloop.join()
    print("join done", flush=True)
