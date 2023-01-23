import sys
import time
import struct
import usb.core
import usb.util

def key_device():
  # find all usb devices
  dev = usb.core.find(find_all=True)
  for d in dev:
    # Look specificly for Yubico keys
    if usb.util.get_string(d, d.iManufacturer) == "Yubico": return d
  return None

def key_claim(dev, reattach = False):
  dev.detach_kernel_driver(0)
  if not reattach:
    if dev.is_kernel_driver_active(0):
      if not dev.is_kernel_driver_active(0): reattach = True
  try: usb.util.claim_interface(dev, 0)
  except usb.core.USBError: print("Access denied")
  dev.set_configuration()
  return reattach

def key_close(dev, reattach):
  usb.util.dispose_resources(dev)
  if reattach:
    try: dev.close()
    except AttributeError as e: print("ignore first close")
  else: dev.attach_kernel_driver(0)

def key_endpoint(dev, type):
  cfg = dev.get_active_configuration()
  ifnr = cfg[(0,0)].bInterfaceNumber
  alt = usb.control.get_interface(dev, ifnr)
  intf = usb.util.find_descriptor(cfg, bInterfaceNumber = ifnr,
    bAlternateSetting = alt)
  return usb.util.find_descriptor(intf, custom_match = lambda e:
    usb.util.endpoint_direction(e.bEndpointAddress) == type)

def key_write(dev):
  ep = key_endpoint(dev, usb.util.ENDPOINT_OUT)
  data = b"\x06\x00\x00"
  ep.write(data, timeout=6000)

def key_read(dev):
  ep = key_endpoint(dev, usb.util.ENDPOINT_IN)
  try: return ep.read(0x10, timeout=6000)
  except usb.core.USBTimeoutError as e: print("Error reading response:", e.args)
  return 0

def key_r(dev):
  rt = (0x01 << 5) | 0x1 | 0x84
  val = 0x03 << 8
  r = dev.ctrl_transfer(rt, 1, 0x200, 0x00, 64, timeout=2000)
  print(r)


def key_type(type):
  return usb.util.build_request_type(type, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)

def key_getreport(dev):
  return dev.ctrl_transfer(key_type(usb.util.CTRL_IN), 9, 0x300, 0, 64)

def key_setreport(dev):
  dev.ctrl_transfer(key_type(usb.util.CTRL_OUT), 9, 0x300, 0, (0xff, 1, 0, 0, 0, 0, 0, 0))

def key_rr(dev):
  data = b"\x06\x00\x00"
  eo = key_endpoint(dev, usb.util.ENDPOINT_OUT)
  ei = key_endpoint(dev, usb.util.ENDPOINT_IN)
  s = eo.write(data, timeout=6000)
  if s % 64 == 0: eo.write(b"", timeout=6000)
  try: return bytes(ei.read(0xFFFF, timeout=6000))
  except usb.core.USBTimeoutError as e: print("Error reading response:", e.args)
  return 0

def key_await(dev):
  done = False
  sleep = 0.1
  wait = (2 * 2) - 1 + 6
  while not done:
    time.sleep(sleep)
    key_r(dev)
    done = True

def main():
  dev = key_device()
  ret = 0
  if dev:
    dev.reset()
    time.sleep(0.6)
    reattach = key_claim(dev)
    key_write(dev)
    print("before set")
    key_setreport(dev)
    time.sleep(1)
    key_setreport(dev)
    print("before get")
    time.sleep(1)
    print(key_getreport(dev))
    time.sleep(1)
    print(key_getreport(dev))
    time.sleep(1)
    print("after get")
    print("ret",key_r(dev))
    #key_read(dev) # times out!? i need to poke it in special spot?
    key_close(dev, reattach)
    if ret != 0: print("OK")
    else: print("Nah")
  else: print("Ruhroh!")

if __name__=="__main__": main()

# Data from IORegistryExplorer

# PrimaryUsagePage
# 0xf1d0

# LocationID
# 0x2100000

# IOUserServerHash
# df1b771842713b880a69fa6317455b7bcc52ba7f

# kOSBundleDextUniqueIdentifier
# <b7 96 d1 5d 93 54 ea e8 26 f3 70 c7 8d a5 a6 9a 01 07 35 2f 2c 06 43 53 23 1d 0e fe c8 90 df 26>

# Report descriptor
# <06 d0 f1 09 01 a1 01 09 20 15 00 26 ff 00 75 08 95 40 81 02 09 21 15 00 26 ff 00 75 08 95 40 91 02 c0>
