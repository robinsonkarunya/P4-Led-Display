import threading
import time
import serial
import array
import time
import os
import traceback
# from reply import *


# -------------------------------------------------------------------------------------------------------------------------------
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import string

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 40
options.cols = 80
options.chain_length = 4
options.parallel = 2
options.multiplexing = 20
options.brightness = 100  # Example: Set brightness to 50%
options.hardware_mapping = 'regular'  # Adjust if needed
options.gpio_slowdown = 3
options.pwm_bits = 2
options.gpio_slowdown = 4
options.pwm_lsb_nanoseconds = 50
options.limit_refresh_rate_hz = 350
options.pixel_mapper_config = "U-mapper"
# options.row_address_type = 5
# options.disable_hardware_pulsing = False
options.disable_hardware_pulsing = False
#print("print matix widtch", matrix.width)
matrix = RGBMatrix(options=options)

# Load font and color
font = graphics.Font()
# font.LoadFont("sample13.bdf")
font.LoadFont("/home/pi/rpi-rgb-led-matrix/bindings/python/samples/sample13.bdf")
textColor = graphics.Color(255, 0, 0)
textColor2 = graphics.Color(255, 255, 0)
textColor3 = graphics.Color(255, 255, 0)


# -------------------------------------------------------------------------------------------------------------------------------


# SIZE = pygame.display.Info()
FPS = 0.5
faulty_serialport = 0
# screen = pygame.display.set_mode((SIZE.current_w, SIZE.current_h))
try:
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.06

    )
except Exception as ex:
    faulty_serialport = 1
    print(ex)
a_string = ""
anc_lng = 0
addr_chck = 0
addr_chck = '31'
addr = 0x31
no_of_line = 14  # LED disp lines
to_no_of_line = 1  # LED tmeout disp lines

py_display_char_color = 'yellow'
port_on = False
port_off = True
intrupt = 0


gpio_pin_ack_nack = 13
gpio_pin_addr = 15
gpio_pin_scr_mode = 11
ack_mode_switch = True
screen_mode_switch = 0
firsttime = 0
anc_stop = 0

py_display_font = 0o5


anc_intrupt = 0
tme_out_minus = 50  # timeout truck is calculated as +50
hesub = int('30', 16)
nortruck = []  # normal truck array <50
tmeoutruck = []
show_off = []
repadd = 0x30

# Commands code
enq = 69
data = 68
tmeout = 84
cmd = 67

# ReadRegcno var
read_arec = 62
read_arec_all = 55
announce_delay = 1
announce_option = bytearray(
    [0x52, 0x48, 0x45, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20])
feedbackon = 0x31
feedbackoff = 0x30
enable_feedbck = feedbackoff  # ----feedbckoff 0--->off && 1--->On
muteon = 0x31
muteoff = 0x30
anc_mute = muteon
disp_stat = 0x31
scan_anc_mode = 0x50   # scan is stopped ->p = 0x50
scanstatus = 0x30  # stooped 0x30 & running 0x31
anc_recno = 0
bright = 2
start_display_index = 0

# code Var in decimal
stx = 2
etx = 3
ack = 65
nack = 78
new = 48
appe = 49
insrt = 50
delet = 51
eras_all = 52
st_ind = 53
off_val = 54
ancoption = 55
scan_delay = 56
anc_delay = 57
brightness = 58
anc = 57
sft = 56
up_stat = 59

# commands var
stop_scan = 48
strt_scan = 49
pause_scan = 50
cont_scan = 51
clr_disp = 53
display_status = 1
anc_status = 0x42   # busy->B= 0x42
lastfree_regno = 0
current_regno = 0
current_TO_regno = 0
scand = 5  # scan_delay
dflt = 54
ancmute = 58
enab_fedbck = 60
stpanc = 61
getstat = 63
sftst = []

# temp var
view1 = 0
pyot = ''

repack = ''
offset = 1  # offset value set
time_out_index = 0  # timeout truck display
starting_index = 0
display_index = 0
running = True
nortruck_len = 50  # normal truck array size
tmeoutruck_len = 15  # Timeout truck array size
self_test_mode = True
new_message = False
self_test_new_message = False

global normaldata


def repfunc(lne, truckdata):  # replace function normal truck
    nortruck[lne] = truckdata


def tmeoutruckrep(regno, tstring):  # replace function tmeout truck
    tmeoutruck[regno] = tstring


def norappen(sdata):  # append function normal truck
    norlen = len(nortruck)
    if norlen < nortruck_len:
        nortruck.append(sdata)
    else:
        del nortruck[1]
        nortruck.append(sdata)


def tmeappen(tdata):  # append function tmeout truck
    tmeoutlen = len(tmeoutruck)
    if tmeoutlen < tmeoutruck_len:
        tmeoutruck.append(tdata)
    else:
        del tmeoutruck[1]
        tmeoutruck.append(tdata)


rs485 = 7
n_count = 0


def rep_ack(ackmsg):  # reply_ack_message to host
    global rs485, ack_mode_switch
    check_outme = 0.0015
    # print("Entered into reply")
    if ack_mode_switch == True:
        time.sleep(0.001)
        #print(ackmsg)
        ser.write(ackmsg)
        time.sleep(len(ackmsg)*check_outme)
        #print("---------------ack sent to host---------------------")


temp = 0


def respone_readarec(record):
    global temp
    try:
        lastfree_regno = len(nortruck) + 0x30
        current_regno = 1 + 0x30
        offset1 = offset + 0x30
        scn_dly = scand + 0x30
        acdly = announce_delay + 0x30  # -------anc delay
        if record < 65:
            pyot = bytearray([stx, addr, ack, cmd, read_arec, lastfree_regno])
        else:
            pyot = bytearray([stx, addr, ack, cmd, read_arec_all, lastfree_regno])
        pyot.append(current_regno)
        pyot.append(offset1)
        pyot.append(scn_dly)
        pyot.append(acdly)
        for p in announce_option:
            pyot.append(p)
        pyot.append(enable_feedbck + 0x30)
        if record < 65:
            pyot.append(record + 0x30)
            space = 0
            for i in nortruck[record]:
                space = space + 1
                #print(f"i = {i} and type = {type(i)}")
                pyot.append(ord(i))
            while (space < 25):
                space = space + 1
                pyot.append(0x20)
        else:
            nortruck_arrlen = len(nortruck)
            tmeoutruck_arrlen = len(tmeoutruck)
            for i in range(0, 50):
                if i < nortruck_arrlen:
                    space = 0
                    for i in nortruck[i]:
                        space = space + 1
                        pyot.append(ord(i))
                    while (space < 25):
                        space = space + 1
                        pyot.append(0x20)
                else:
                    for i in range(0, 25):
                        pyot.append(0x20)

            for i in range(0, 15):
                if i < tmeoutruck_arrlen:
                    space = 0
                    for i in tmeoutruck[i]:
                        space = space + 1
                        pyot.append(ord(i))
                    while (space < 25):
                        space = space + 1
                        pyot.append(0x20)
                else:
                    for i in range(0, 25):
                        pyot.append(0x20)

        chcks = 0
        for y in pyot:
            if y == 2:
                a = 0
            else:
                chcks = chcks ^ y
        cs1 = ((chcks & 0xF0) >> 4)+hesub
        cs2 = (chcks & 0x0F)+hesub
        pyot.append(cs1)
        pyot.append(cs2)
        pyot.append(etx)
   #     temp = len(pyot)
        # rep_ack(pyot)
        return pyot
    except Exception as e:
        # Get the traceback object
        tb = traceback.extract_tb(e.__traceback__)
        filename, line_number, _, _ = tb[-1]
        #print(tb, filename, line_number)


def check_anc_option_range(indx, value):
    if value in set(['R', 'H', 'E']):
        announce_option[indx] = value
    else:
        announce_option[indx] = 32


def get_status():
    lastfree_regno = len(nortruck) + hesub
    lastfree_To_regno = len(tmeoutruck) + hesub
    current_regno = display_index + 1 + hesub
    current_To_regno = hesub
    if running == True:
        scanstatus = 0x31
    else:
        scanstatus = 0x30
    anc_rec_no = 0x30  # which record is anc
    # version = bytearray([0x56,0x45,0x52,0x31])
    repack = bytearray([stx, addr, ack, cmd, getstat])
    repack.append(lastfree_regno)
    repack.append(lastfree_To_regno)
    repack.append(current_regno)
    repack.append(current_To_regno)
    repack.append(disp_stat)
    repack.append(scan_anc_mode)
    repack.append(scand + hesub)
    repack.append(scanstatus)
    repack.append(announce_delay+hesub)
    repack.append(muteon)
    repack.append(anc_status)
    repack.append(0x30)
    repack.append(announce_option[0])
    repack.append(announce_option[1])
    repack.append(announce_option[2])
    repack.append(announce_option[3])
    repack.append(announce_option[4])
    repack.append(announce_option[5])
    repack.append(announce_option[6])
    repack.append(announce_option[7])
    repack.append(announce_option[8])
    repack.append(announce_option[9])
    repack.append(enable_feedbck)
    repack.append(offset+hesub)
    repack.append(start_display_index+hesub)
    repack.append(0x33)  # default value fr brightness is 3
    repack.append(0x56)
    repack.append(0x45)
    repack.append(0x52)
    repack.append(0x30)  # ver0
    chcks = 0
    for y in repack:
        if y == 2:
            a = 0
        else:
            chcks = chcks ^ y
    cs1 = ((chcks & 0xF0) >> 4)+0x30
    cs2 = (chcks & 0x0F)+0x30
    repack.append(cs1)
    repack.append(cs2)
    repack.append(etx)
    # rep_ack(repack)
    return repack


# nortruck.append("REGULAR TRUCK")
# tmeoutruck.append("TIMEOUT TRUCK")

clrdisp = ""


def decodeserialdata(y):
    global enq, intrupt, anc_intrupt, anc_stop, nortruck, tmeoutruck, offset, running, display_index, FPS, clrdisp, nortruck_len, tmeoutruck_len, stx, etx, addr, ack, data, new, appe, repack, insrt, delet, eras_all, st_ind, off_val, ancoption, scan_delay, anc_delay
    global stop_scan, strt_scan, pause_scan, cont_scan, clr_disp, display_status, anc_status, lastfree_regno, current_regno, announce_delay, announce_option, enable_feedbck, view1, pyot, scand, dflt, feedbackoff, feedbackon
    global anc_mute, muteon, muteoff, stpanc, enab_fedbck, getstat, current_TO_regno, disp_stat, scan_anc_mode, scanstatus, anc_recno, anc_lng, bright, anc, sft, up_stat, sftst, self_test_mode
    global start_display_index, port_on, port_off, read_arec_all, addr_chck, starting_index, time_out_index, new_message, self_test_new_message
    if y[0:2] == '02':

        if y[2:4] == addr_chck:
            if y[4:6] == '45':  # ENQ command
                #print("ENQ command")
                self_test_mode = False
                lastfree_regno = len(nortruck)
                current_regno = display_index + 1
                calchck = addr ^ ack ^ enq ^ (
                    display_status + 0x30) ^ anc_status ^ (lastfree_regno + 0x30) ^ (current_regno + 0x30)
                cs1 = ((calchck & 0xF0) >> 4)+hesub
                cs2 = (calchck & 0x0F)+hesub
                repack = bytearray([stx, addr, ack, enq, display_status + 0x30, anc_status,
                                    lastfree_regno + 0x30, current_regno + 0x30, cs1, cs2, etx])
                #print("ENQ command ack", repack)
                rep_ack(repack)
            if y[4:6] == '44':
                #print("Data commmand")  # DATA COMMAND
                text = "DATACommand"
                if y[6:8] == '30':                                        # new Data
                    #print("New Data")
                    self_test_mode = False
                    lineno = int(y[8:10], 16)
                    lne = lineno-hesub
                    newline = bytes.fromhex(y[10:62]).decode('ascii')
                    # y[60:62] vari to anounce r not in DATA & TMEOUT=(new,append,insert)
                    chck1 = int(y[62:64], 16)
                    chck2 = int(y[64:66], 16)
                    if (lne > len(nortruck)):
                        repack = bytearray(
                            [stx, addr, nack, data, new, chck1, chck2, etx])
                    else:
                        repfunc(lne, newline)
                        repack = bytearray(
                            [stx, addr, ack, data, new, chck1, chck2, etx])  # len 66
                elif y[6:8] == '31':  # Append data
                    #print("reached data append")
                    new_message = True
                    running = True
                    self_test_new_message = False
                    self_test_mode = False
                    appen = bytes.fromhex(y[10:62]).decode('ascii')
                    norappen(appen)
                    chck1 = int(y[62:64], 16)
                    chck2 = int(y[64:66], 16)
                    repack = bytearray(
                        [stx, addr, ack, data, appe, chck1, chck2, etx])  # len 66
                elif y[6:8] == '32':  # insert data
                    #print("reached data insert")
                    self_test_mode = False
                    new_message = True
                    lineno = int(y[8:10], 16)
                    lne2 = lineno-hesub
                    inser = bytes.fromhex(y[10:62]).decode('ascii')
                    chck1 = int(y[62:64], 16)
                    chck2 = int(y[64:66], 16)
                    if lne2 <= len(nortruck):
                        try:
                            del nortruck[nortruck_len - 1]
                        except:
                            error = 1
                        nortruck.insert(lne2, inser)
                        repack = bytearray(
                            [stx, addr, ack, data, insrt, chck1, chck2, etx])  # len 66
                    else:
                        repack = bytearray(
                            [stx, addr, nack, data, insrt, chck1, chck2, etx])  # len 66
                elif y[6:8] == '33':                                        # delete data
                    #print("reached data delete")
                    self_test_mode = False
                    new_message = True
                    lineno = int(y[8:10], 16)
                    lne3 = lineno-hesub
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if lne3 < len(nortruck):
                        del nortruck[lne3]
                        repack = bytearray(
                            [stx, addr, ack, data, delet, chck1, chck2, etx])  # len 16
                    else:
                        repack = bytearray(
                            [stx, addr, nack, data, delet, chck1, chck2, etx])
                elif y[6:8] == '34':  # Eraseall data
                    #print("reached data eraseall")
                    new_message = True
                    self_test_mode = False
                    intrupt = 1
                    anc_mute = 49
                    nortruck = []
                    # nortruck = ['', '', '', '', '', '',
                    #             '', '', '', '', '', '', '', '']
                    # nortruck.append("REGULAR TRUCK")
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, data, eras_all, chck1, chck2, etx])  # len 14
                elif y[6:8] == '35':  # Index
                    #print("reached data index")
                    new_message = True
                    self_test_mode = False
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    ind = int(y[8:10], 16)
                    if ind-hesub < 50 and ind-hesub > 0:
                        start_display_index = ind-hesub
                        repack = bytearray(
                            [stx, addr, ack, data, st_ind, chck1, chck2, etx])  # len 16
                    else:
                        repack = bytearray(
                            [stx, addr, nack, data, st_ind, chck1, chck2, etx])
                elif y[6:8] == '36':  # offset
                    #print("reached data offset")
                    new_message = True
                    self_test_mode = False
                    rxoffset = int(y[8:10], 16)
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if rxoffset-hesub < 15:
                        if rxoffset-hesub >= 0:
                            offset = rxoffset-hesub
                            repack = bytearray(
                                # len 16
                                [stx, addr, ack, data, off_val, chck1, chck2, etx])
                        else:
                            repack = bytearray(
                                # len 16
                                [stx, addr, nack, data, off_val, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            # len 16
                            [stx, addr, nack, data, off_val, chck1, chck2, etx])
                elif y[6:8] == '37':  # Anc_options
                    #print("reached data anc_options")
                    self_test_mode = False
                    check_anc_option_range(0, int.from_bytes(
                        bytes.fromhex(y[8:10]), "big"))
                    check_anc_option_range(1, int.from_bytes(
                        bytes.fromhex(y[10:12]), "big"))
                    check_anc_option_range(2, int.from_bytes(
                        bytes.fromhex(y[12:14]), "big"))
                    check_anc_option_range(3, int.from_bytes(
                        bytes.fromhex(y[14:16]), "big"))
                    check_anc_option_range(4, int.from_bytes(
                        bytes.fromhex(y[16:18]), "big"))
                    check_anc_option_range(5, int.from_bytes(
                        bytes.fromhex(y[18:20]), "big"))
                    check_anc_option_range(6, int.from_bytes(
                        bytes.fromhex(y[20:22]), "big"))
                    check_anc_option_range(7, int.from_bytes(
                        bytes.fromhex(y[22:24]), "big"))
                    check_anc_option_range(8, int.from_bytes(
                        bytes.fromhex(y[24:26]), "big"))
                    check_anc_option_range(9, int.from_bytes(
                        bytes.fromhex(y[26:28]), "big"))

                    # Convert chck1 and chck2 to integers
                    chck1 = int.from_bytes(bytes.fromhex(y[28:30]), "big")
                    chck2 = int.from_bytes(bytes.fromhex(y[30:32]), "big")

                    # Ensure all elements in bytearray are integers
                    repack = bytearray(
                        [stx, addr, ack, data, ancoption, chck1, chck2, etx])

                elif y[6:8] == '38':  # Scan_Delay
                    #print("reached data scan_delay")
                    self_test_mode = False
                    scanc = int(y[8:10], 16)
                    #print(f"scanc = {scanc}")
                    scand = scanc-hesub
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if scand <= 99 and scand >= 5:
                        repack = bytearray(
                            # len 16
                            [stx, addr, ack, data, scan_delay, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            # len 16
                            [stx, addr, nack, data, scan_delay, chck1, chck2, etx])
                elif y[6:8] == '39':  # Ancdelay
                    #print("reached data anc_delay")
                    self_test_mode = False
                    lineno8 = int(y[8:10], 16)
                    lne8 = lineno8-hesub
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if lne8 <= 99 and lne8 >= 1:
                        announce_delay = lne8
                        repack = bytearray(
                            [stx, addr, ack, data, anc_delay, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            [stx, addr, nack, data, anc_delay, chck1, chck2, etx])
                # brightness ---No operation juz replyng ack
                elif y[6:8] == '3a':
                    #print("reached data brightness")
                    self_test_mode = False
                    b_lineno = int(y[8:10], 16)
                    bright = b_lineno-hesub
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if bright <= 10 and bright >= 1:
                        repack = bytearray(
                            # len16
                            [stx, addr, ack, data, brightness, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            [stx, addr, nack, data, brightness, chck1, chck2, etx])
                rep_ack(repack)
               # noroutpt =""
                # for normaldata in nortruck:
                #  noroutpt = noroutpt + normaldata+"\r\n"

                # return noroutpt    #text =  len(nortruck)
            elif y[4:6] == '54':  # TIME COMMAND
                #print("reached data time")
                text = "TimeoutCommand"
                # new(replace)
                if y[6:8] == '30':
                    self_test_mode = False
                    tlineno = int(y[8:10], 16)
                    tlne4 = tlineno-hesub
                    tminus1 = tlne4-tme_out_minus
                    tnewline = bytes.fromhex(y[10:62]).decode('ascii')
                    chcksum1 = int(y[62:64], 16)
                    chcksum2 = int(y[64:66], 16)
                    if tminus1 > len(tmeoutruck):
                        repack = bytearray(
                            # len 66
                            [stx, addr, nack, tmeout, new, chcksum1, chcksum2, etx])
                    else:
                        tmeoutruckrep(tminus1, tnewline)
                        repack = bytearray(
                            # len 66
                            [stx, addr, ack, tmeout, new, chcksum1, chcksum2, etx])
                elif y[6:8] == '31':  # Append
                    #print("reached data append 31")
                    self_test_mode = False
                    new_message = True
                    tappen = bytes.fromhex(y[10:62]).decode('ascii')
                    # text =  tappend
                    tmeappen(tappen)
                    chck1 = int(y[62:64], 16)
                    chck2 = int(y[64:66], 16)
                    repack = bytearray(
                        [stx, addr, ack, tmeout, appe, chck1, chck2, etx])  # len 66
                elif y[6:8] == '32':  # ins
                    #print("reached data ins 32")
                    self_test_mode = False
                    tlineno = int(y[8:10], 16)
                    tlne5 = tlineno-hesub
                    tminus2 = tlne5-tme_out_minus
                    tinse = bytes.fromhex(y[10:62]).decode('ascii')
                    chck1 = int(y[62:64], 16)
                    chck2 = int(y[64:66], 16)
                    if tminus2 <= len(tmeoutruck):
                        try:
                            del tmeoutruck[tmeoutruck_len-1]
                        except:
                            error = 1
                        tmeoutruck.insert(tminus2, tinse)
                        repack = bytearray(
                            # len 66
                            [stx, addr, ack, tmeout, insrt, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            # len 66
                            [stx, addr, nack, tmeout, insrt, chck1, chck2, etx])
                elif y[6:8] == '33':  # del
                    #print("reached data del 33")
                    self_test_mode = False
                    tlineno = int(y[8:10], 16)
                    tlne6 = tlineno-hesub
                    tminus3 = tlne6-tme_out_minus
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if tminus3 < len(tmeoutruck):
                        del tmeoutruck[tminus3]
                        repack = bytearray(
                            # len 16
                            [stx, addr, ack, tmeout, delet, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            # len 16
                            [stx, addr, nack, tmeout, delet, chck1, chck2, etx])
                elif y[6:8] == '34':  # Erase-all
                    #print("reached data erase all 34")
                    self_test_mode = False
                    tmeoutruck = []
                    # tmeoutruck.append("TIMEOUT TRUCK")
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, tmeout, eras_all, chck1, chck2, etx])  # len 14
                rep_ack(repack)
                # tmeout = ""
                # for tmeoutdata in tmeoutruck:
                #  tmeout = tmeout + tmeoutdata+"\r\n"
                # return tmeout
            elif y[4:6] == '43':  # Control Commands
                #print("reached data control commands")
                text = "ControlCommands"
                if y[6:8] == '30':  # stop
                    #print("reached data stop 30")
                    self_test_mode = False
                    running = False
                    intrupt = 1
                    anc_mute = 49
                    display_index = 0
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, cmd, stop_scan, chck1, chck2, etx])  # len 14
                elif y[6:8] == '31':  # start
                    #print("reached data start 31")
                    # self_test_mode = False
                    running = True
                    starting_index = 0
                    start_display_index = 0
                    time_out_index = 0
                    display_index = 0
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, cmd, strt_scan, chck1, chck2, etx])  # len 14
                elif y[6:8] == '32':  # pause
                    #print("reached data pause 32")
                    self_test_mode = False
                    running = False
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, cmd, pause_scan, chck1, chck2, etx])  # len 14
                elif y[6:8] == '33':  # contine
                    #print("reached data contine 33")
                    self_test_mode = False
                    anc_stop = 0
                    running = True
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, cmd, cont_scan, chck1, chck2, etx])  # len 14
                # cleardisp-----------------------------------------
                elif y[6:8] == '35':
                    #print("reached data clear display 35")
                    self_test_mode = False
                    intrupt = 1
                    anc_mute = 49
                    clrdisp = 'clear'
                    running = False
                    display_index = 0
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    #print("status of :", running, self_test_mode, clrdisp)
                    repack = bytearray(
                        [stx, addr, ack, cmd, clr_disp, chck1, chck2, etx])  # len 14
                elif y[6:8] == '36':  # default
                    #print("reached data default 36")
                    self_test_mode = False
                    try:
                        display_index = 0
                        starting_index = 0
                        offset = 15
                        scand = 10
                        announce_delay = 3
                        announce_option[0] = 0x45
                        announce_option[1] = 0x48
                        announce_option[2] = 0x52
                        announce_option[3] = 0x20
                        announce_option[4] = 0x20
                        announce_option[5] = 0x20
                        announce_option[6] = 0x20
                        announce_option[7] = 0x20
                        announce_option[8] = 0x20
                        announce_option[9] = 0x20
                        enable_feedbck = feedbackoff
                        anc_mute = muteoff
                        running = False
                        chck1 = int(y[8:10], 16)
                        chck2 = int(y[10:12], 16)
                        repack = bytearray(
                            [stx, addr, ack, cmd, dflt, chck1, chck2, etx])
                    except:
                        b = 0
                elif y[6:8] == '37':  # Read-all
                    #print("reached data read-all 37")
                    self_test_mode = False
                    repack = respone_readarec(100)
                    # rep_ack(respone_readarec(100))
                elif y[6:8] == '38':  # self-test
                    #print("reached data self-test 38")
                    if self_test_mode == True:
                        self_test_mode = False
                        #print("if working ")
                    else:
                        intrupt = 1
                        anc_mute = 49
                        self_test_mode = True
                        running = True
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, cmd, sft, chck1, chck2, etx])  # len 14
                elif y[6:8] == '39':  # Anc
                    #print("reached data anc 39")
                    self_test_mode = False
                    lineno = int(y[8:10], 16)
                    anc_recno = lineno-hesub
                    anc_lng = bytes.fromhex(y[10:62]).decode('ascii')
                    anc_intrupt = 1
                    chck1 = int(y[12:14], 16)
                    chck2 = int(y[14:16], 16)
                    repack = bytearray(
                        [stx, addr, ack, cmd, anc, chck1, chck2, etx])
                elif y[6:8] == '3a':  # anc mute
                    #print("reached data anc mute 3a")
                    self_test_mode = False
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if y[8:10] == '31':
                        anc_mute = muteon
                        repack = bytearray(
                            # check 1
                            [stx, addr, ack, cmd, ancmute, chck1, chck2, etx])
                    elif y[8:10] == '30':
                        anc_mute = muteoff
                        repack = bytearray(
                            [stx, addr, ack, cmd, ancmute, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            [stx, addr, nack, cmd, ancmute, chck1, chck2, etx])

                elif y[6:8] == '3b':  # update system
                    #print("reached data update system 3b")
                    self_test_mode = False
                    chck1 = (y[8:10], 16)
                    chck2 = (y[10:12], 16)
                    # repack = bytearray([stx,addr,ack,cmd,up_stat,chck1,chck2,etx])#len 14
                    repack = bytearray([stx, addr, nack, etx])
                elif y[6:8] == '3c':  # enablefeedbck
                    #print("reached data enable feedbck 3c")
                    self_test_mode = False
                    chck1 = int(y[10:12], 16)
                    chck2 = int(y[12:14], 16)
                    if y[8:10] == '31':
                        enable_feedbck = feedbackon
                        repack = bytearray(
                            [stx, addr, ack, cmd, enab_fedbck, chck1, chck2, etx])
                    elif y[8:10] == '30':
                        enable_feedbck = feedbackoff
                        repack = bytearray(
                            [stx, addr, ack, cmd, enab_fedbck, chck1, chck2, etx])
                    else:
                        repack = bytearray(
                            [stx, addr, nack, cmd, enab_fedbck, chck1, chck2, etx])
                elif y[6:8] == '3d':  # stop-anc-------------ly cs given
                    #print("reached data stop anc 3d")
                    self_test_mode = False
                    anc_stop = 1
                    #print("anc stopped")
                    chck1 = int(y[8:10], 16)
                    chck2 = int(y[10:12], 16)
                    repack = bytearray(
                        [stx, addr, ack, cmd, stpanc, chck1, chck2, etx])  # len 14
                elif y[6:8] == '3e':  # Read_arec
                    #print("reached data read arec 3e")
                    self_test_mode = False
                    lineno = int(y[8:10], 16)
                    lne3 = lineno-hesub
                    norlen = len(nortruck)
                    #print(f"line number is {lne3} and lineno is {lineno}")
                    if lne3 <= 65:
                        #print("if working ")
                        repack = respone_readarec(lne3)
                        # rep_ack(respone_readarec(lne3))
                    else:
                        #print("else working ")
                        chck1 = (y[10:12], 16)
                        chck2 = (y[12:14], 16)
                        repack = bytearray(
                            [stx, addr, nack, cmd, read_arec, chck1, chck2, etx])
                elif y[6:8] == '3f':
                    #print("reached data read arec all 3f")
                    self_test_mode = False
                    repack = get_status()

                rep_ack(repack)
        else:
            text = "IncorrectAddr"
    else:
        text = ""


decode = " "
rstx = 0o2    # starting index
retx = 0o3    # Ending index
stxset = False  # setting a boolean to check stx 02
recvdata = []  # initzng array fr recvng data
k = ''
'''
def count_check(datalen):
    #print datalen
    if datalen < 35:    
'''


def getdata():
    global text, decode, recvdata, stxset, k, anc_stop
    while 1:
        time.sleep(0.01)
        if ser.inWaiting():
            q = ord(ser.read())
            if q == rstx:
                stxset = True
                rcount = 0
                recvdata = []
            if stxset == True:
                recvdata.append(q)
                rcount = rcount + 1
                if rcount > 34:
                    stxset = False
                    rcount = 0
                    recvdata = []
                elif q == retx and rcount <= 34:
                    # #print ("retx value",rcount)
                    k = bytearray(recvdata)
                    del recvdata[-1]
                    hex_array = [hex(x)[2:] for x in recvdata]
                    t = "0" + ''.join(str(e) for e in hex_array)
                    t = t + "03"
                    recvdata = []
                    p = len(t)
                    istbyte = t[0:2]
                    lastbyte = t[p - 2:p]
                    rxadr = t[2:4]
                    recvcount = rcount * 2
                    inpt_cs1 = '0x' + t[recvcount - 6:recvcount - 4]
                    # #print inpt_cs1
                    rcks1 = t[recvcount - 6:recvcount - 4]
                    inpt_cs2 = '0x' + t[recvcount - 4:recvcount - 2]
                    # #print inpt_cs1
                    rcks2 = t[recvcount - 4:recvcount - 2]

                    view1 = inpt_cs1
                    if p > 0:
                        try:
                            csdata = ['30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
                                      '3a', '3b', '3c', '3d', '3e', '3f',
                                      '3A', '3B', '3C', '3D', '3E', '3F']
                            if istbyte == '02' and lastbyte == '03' and rxadr == addr_chck and t[4:6] != '41' and rcks1 in csdata and rcks2 in csdata:
                                # if istbyte == '02' and lastbyte == '03' and rxadr == addr_chck and t[4:6] != '41':
                                chcks = 0
                                for y in range(1, len(k) - 3):
                                    chcks ^= k[y]
                                cs1 = ((chcks & 0xF0) >> 4) + 0x30
                                cs2 = (chcks & 0x0F) + 0x30

                                # Verify checksum and decode data if valid
                                if inpt_cs1 == str(hex(cs1)) and inpt_cs2 == str(hex(cs2)):
                                    #print(
                                        #'-----------------------------------------------')
                                    data_bytes = bytes.fromhex(t)
                                    stx = data_bytes[0]
                                    addr = data_bytes[1]
                                    ack = data_bytes[2]
                                    cmd = data_bytes[3]
                                    ancoption = data_bytes[4]
                                    # Adjust length based on actual format
                                    data_section = data_bytes[5:15]
                                    chck1 = data_bytes[-3]
                                    chck2 = data_bytes[-2]
                                    etx = data_bytes[-1]

                                    # #print out each part in a human-readable format
                                    # print(f"STX: {stx} (0x{stx:02X})")
                                    # print(f"Address: {addr} (0x{addr:02X})")
                                    # print(f"ACK: {ack} (0x{ack:02X})")
                                    # print(f"Command: {cmd} (0x{cmd:02X})")
                                    # print(f"Check1: {chck1} (0x{chck1:02X})")
                                    # print(f"Check2: {chck2} (0x{chck2:02X})")
                                    # print(f"ETX: {etx} (0x{etx:02X})")
                                    # print(
                                    #     "-----------------------------------------------")
                                    decodeserialdata(t)
                                    rcount = 0
                                    stxset = False
                                else:
                                    nackval = '4e'
                                    ackval = '41'
                                    # If `nackval` or `ackval` do not match, prepare for retransmission
                                    if t[4:6] != nackval and t[4:6] != ackval:
                                        # print("nack loop" + t[4:6])
                                        repack = bytearray(
                                            [stx, addr, nack, etx])
                                        rep_ack(repack)
                        except Exception as e:
                            error = 1
                            # Get the traceback object
                            tb = traceback.extract_tb(e.__traceback__)
                            # Extract the filename and line number from the last frame
                            filename, line_number, _, _ = tb[-1]
                            print(e)


if faulty_serialport == 0:
    threading.Thread(target=getdata).start()


def blit_text(text=None):
    global no_of_line, to_no_of_line, py_display_font, py_display_char_color
    # words = [word.split(';') for word in text.splitlines()]
    if faulty_serialport == 1:
        text = "Hardware Error. \r\n Com port missing !!! "
        graphics.DrawText(matrix, font, 0, 72, textColor, text)
        return
    if text == None:
        matrix.Clear()
        print("No text to display")
        return
    #print("text data is",text)
    if len(text) > 1:
        words = [line.split(';') for line in text.splitlines()]
        word = [item for sublist in words for item in sublist]  # Flatten the list
    matrix.Clear()
    z = 0
    if word[0]:
        graphics.DrawText(matrix, font, z, 8, textColor, word[0])
    if word[1]:
        graphics.DrawText(matrix, font, z, 16, textColor, word[1])
    if word[2]:
        graphics.DrawText(matrix, font, z, 24, textColor, word[2])
    if word[3]:
        graphics.DrawText(matrix, font, z, 32, textColor, word[3])
    if word[4]:
        graphics.DrawText(matrix, font, z, 40, textColor, word[4])
    if word[5]:
        graphics.DrawText(matrix, font, z, 48, textColor, word[5])
    if word[6]:
        graphics.DrawText(matrix, font, z, 56, textColor, word[6])
    if word[7]:
        graphics.DrawText(matrix, font, z, 64, textColor, word[7])
    if word[8]:
        graphics.DrawText(matrix, font, z, 72, textColor, word[8])
    if word[9]:
        graphics.DrawText(matrix, font, z, 80, textColor, word[9])
    if word[10]:
        graphics.DrawText(matrix, font, z, 88, textColor, word[10])
    if word[11]:
        graphics.DrawText(matrix, font, z, 96, textColor, word[11])
    if word[12]:
        graphics.DrawText(matrix, font, z, 104, textColor, word[12])
    if word[13]:
        graphics.DrawText(matrix, font, z, 112, textColor, word[13])
    if word[14]:
        graphics.DrawText(matrix, font, z, 120, textColor, word[14])
    #print("--------")
    time.sleep(5)
# # ------------------------------------------------------------------------------------------------------
# def displaydata(word, display_flag):
#     z = 1
#     if display_flag:
#         matrix.Clear()
#         print("working is displaydata", word, len(word))
#         if word[0]:
#             graphics.DrawText(matrix, font, z, 8, textColor, word[0])
#         if word[1]:
#             graphics.DrawText(matrix, font, z, 16, textColor, word[1])
#         if word[2]:
#             graphics.DrawText(matrix, font, z, 24, textColor, word[2])
#         if word[3]:
#             graphics.DrawText(matrix, font, z, 32, textColor, word[3])
#         if word[4]:
#             graphics.DrawText(matrix, font, z, 40, textColor, word[4])
#         if word[5]:
#             graphics.DrawText(matrix, font, z, 48, textColor, word[5])
#         if word[6]:
#             graphics.DrawText(matrix, font, z, 56, textColor, word[6])
#         if word[7]:
#             graphics.DrawText(matrix, font, z, 64, textColor, word[7])
#         if word[8]:
#             graphics.DrawText(matrix, font, z, 72, textColor, word[8])
#         if word[9]:
#             graphics.DrawText(matrix, font, z, 80, textColor, word[9])
#         if word[10]:
#             graphics.DrawText(matrix, font, z, 88, textColor, word[10])
#         if word[11]:
#             graphics.DrawText(matrix, font, z, 96, textColor, word[11])
#         if word[12]:
#             graphics.DrawText(matrix, font, z, 104, textColor, word[12])
#         if word[13]:
#             graphics.DrawText(matrix, font, z, 112, textColor, word[13])
#         if word[14]:
#             graphics.DrawText(matrix, font, z, 120, textColor, word[14])
#         return True


# def blit_text(text=None):
#     global new_message, self_test_new_message
#     if text == None:
#         print("No text to display")
#         return
#     words = [line.split(';') for line in text.splitlines()]
#     word = [item for sublist in words for item in sublist]  # Flatten the list
#     if new_message:
#         print("split data is ", words, word)
#         check = displaydata(word, True)
#         if check:
#             print("working done ")
#             new_message = False
#             self_test_new_message = True
#             return
#     else:
#         print("esle is wokring in blit funtion")
#         if self_test_mode:
#             z = 1
#             print("self test is wokring ")
#             matrix.Clear()
#             if word[0]:
#                 graphics.DrawText(matrix, font, z, 8, textColor, word[0])
#             if word[1]:
#                 graphics.DrawText(matrix, font, z, 16, textColor, word[1])
#             if word[2]:
#                 graphics.DrawText(matrix, font, z, 24, textColor, word[2])
#             if word[3]:
#                 graphics.DrawText(matrix, font, z, 32, textColor, word[3])
#             if word[4]:
#                 graphics.DrawText(matrix, font, z, 40, textColor, word[4])
#             if word[5]:
#                 graphics.DrawText(matrix, font, z, 48, textColor, word[5])
#             if word[6]:
#                 graphics.DrawText(matrix, font, z, 56, textColor, word[6])
#             if word[7]:
#                 graphics.DrawText(matrix, font, z, 64, textColor, word[7])
#             if word[8]:
#                 graphics.DrawText(matrix, font, z, 72, textColor, word[8])
#             if word[9]:
#                 graphics.DrawText(matrix, font, z, 80, textColor, word[9])
#             if word[10]:
#                 graphics.DrawText(matrix, font, z, 88, textColor, word[10])
#             if word[11]:
#                 graphics.DrawText(matrix, font, z, 96, textColor, word[11])
#             if word[12]:
#                 graphics.DrawText(matrix, font, z, 104, textColor, word[12])
#             if word[13]:
#                 graphics.DrawText(matrix, font, z, 112, textColor, word[13])
#             if word[14]:
#                 graphics.DrawText(matrix, font, z, 120, textColor, word[14])
#             print("--------")
#             time.sleep(10)
# ------------------------------------------------------------------------------------------------------


text = ""
to_startindex = 0
sftst = [
    "   MAGDYN HDMI CONVERTOR    ",
    "    FOR TAS VDU DISPLAY     ",
    " MODEL:TND-HDMI-DB-1601429  ",
    "  INTERFACED TO VDU MODEL   ",
    "   TND-LED-115-256HV12-A    ",
    "     Doc.Ref #1601429       ",
    "         VER DB-1.0         ",
    "         REV 2.02           ",
    "         HDMI VER 0         ",
    "         REL.05-17          ",
    "   FIRMWARE CS 0xFE459D     ",
    " MAGNETO DYNAMICS PVT LTD.  ",
    " 7,8,9 VENKATESHWARA NAGAR  ",
    "     PERUNGUDI,CHENNAI      ",
    "     PIN: 600096 . INDIA    ",
    "  email: info @ magdyn.com  ",
    " =========================  "
]


while 1:  # main loop

    time.sleep(0.001)
    norl=0
    tol=0
    if intrupt == 1:
        intrupt = 0
    if running == True:
        noroutpt = ""  # +str(addr_chck)
        a_string = []  # +str(addr_chck)
        if self_test_mode == True:
            sft_lines = 15
            disp = starting_index
            offset1 = 1
            sft_arr = len(sftst)
            for i in range(0, sft_lines):
                if i < sft_arr and disp < sft_arr:
                    noroutpt = noroutpt + sftst[disp]+"\r\n"
                if disp == sft_arr-1:
                    disp = 0
                else:
                    disp = disp + 1

            starting_index = offset1 + starting_index

            if starting_index >= sft_arr or sft_lines >= sft_arr:
                starting_index = 0
            blit_text(noroutpt)
        else:
            arrlen = len(nortruck)  # len initlze
            display_index = starting_index
            #print("else is working ", "arrlen ",arrlen, "display index",display_index,
                  #"start_display_index",starting_index, "nortruck", nortruck, "noroutpt", noroutpt)
            for i in range(0, no_of_line):
                if i < arrlen  and display_index < arrlen+1:
                    if arrlen == display_index:
                        display_index = 0
                        starting_index = 0
                    noroutpt = noroutpt + \
                        nortruck[display_index][:-1]+"\r\n"
                    a_string.append(nortruck[display_index])
                    #print(f"display index is {display_index} and array length is {arrlen}")
                    if display_index == arrlen-1:
                        display_index = 0
                    else:
                        display_index = display_index + 1
                else:
                    noroutpt = noroutpt + "\r\n"
            #print("noroutpt1", noroutpt)
            arrlen_tmeout = len(tmeoutruck)  # len initlze
            time_out_index = to_startindex
            #print(arrlen_tmeout,"alen timeout")
            #print("time out index", time_out_index,
                  #"to_startindex", to_startindex)
        
            for i in range(0, to_no_of_line):
                if i < arrlen_tmeout and time_out_index < arrlen_tmeout+1:
                    if arrlen_tmeout == time_out_index:
                        #print("timeout truck if condition")
                        time_out_index = 0
                        to_startindex = 0
                    noroutpt = noroutpt + \
                        tmeoutruck[time_out_index][:-1]+"\r\n"
                    a_string.append(tmeoutruck[time_out_index])
                    if time_out_index == arrlen_tmeout-1:
                        time_out_index = 0
                    else:
                        time_out_index = time_out_index + 1
                else:
                    #print("timeout truck else condition")
                    noroutpt = noroutpt + "\r\n"
            starting_index = offset + starting_index
            to_startindex = 1 + to_startindex
            #print(f"starting index is {starting_index} and array length is {arrlen} and no_of_lin {no_of_line} and arrlen_tmeout {arrlen_tmeout} and to_startindex {to_startindex}")
            if starting_index >= arrlen+1 or no_of_line >= arrlen:
                starting_index = 0
            if to_startindex >= arrlen_tmeout+1 or to_no_of_line >= arrlen_tmeout+1:
                to_startindex = 0
            #print(f"blit text {noroutpt} and {a_string}")
            blit_text(noroutpt)

    elif clrdisp == 'clear':
        #print("clear is working")
        matrix.Clear()
        clrdisp = ""
