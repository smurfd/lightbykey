import sys
import time
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
  if not reattach:
    dev.set_configuration()
    if dev.is_kernel_driver_active(0):
      dev.detach_kernel_driver(0)
      if not dev.is_kernel_driver_active(0): reattach = True
  try: usb.util.claim_interface(dev, 0)
  except usb.core.USBError: print("Access denied")
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
  try: return ep.read(1, timeout=6000)
  except usb.core.USBTimeoutError as e: print("Error reading response:", e.args)
  return 0

def key_r(dev):
  rt = (0x01 << 5) | 0x1 | 0x84
  val = 0x03 << 8
  r = dev.ctrl_transfer(hex(rt), 0x3, 8, 0, timeout = 2000)
  co = 1

def key_rr(dev):
  data = b"\x06\x00\x00"
  ep = key_endpoint(dev, usb.util.ENDPOINT_OUT)
  er = key_endpoint(dev, usb.util.ENDPOINT_IN)
  s = ep.write(data, timeout=6000)
  if s % 64 == 0: p.write(b"", timeout=6000)
  try: return bytes(er.read(0xFFFF, timeout=6000))
  except usb.core.USBTimeoutError as e: print("Error reading response:", e.args)
  return 0

def key_await(dev):
  done = False
  sleep = 0.1
  wait = (2 * 2) - 1 + 6
  while not done:
    time.sleep(sleep)
    done = True

def main():
  dev = key_device()
  if dev:
    reattach = key_claim(dev)
    key_write(dev)
    ret = key_rr(dev)
    #time.sleep(3)
    #key_r(dev)
    #key_read(dev) # times out!? i need to poke it in special spot?
    key_close(dev, reattach)
    if ret != 0: print("OK")
    else: print("Nah")
  else:
    print("Ruhroh!")

if __name__=="__main__": main()
