import sys, time, struct
import usb.core, usb.util

def key_device():
  dev = usb.core.find(find_all=True) # find all usb devices
  for d in dev: # Look specificly for Yubico keys
    if usb.util.get_string(d, d.iManufacturer) == "Yubico": return d
  return None

def key_claim(dev, ifnr = 0, reattach = False):
  dev.detach_kernel_driver(ifnr)
  if not reattach:
    if dev.is_kernel_driver_active(ifnr):
      if not dev.is_kernel_driver_active(ifnr): reattach = True
  try: usb.util.claim_interface(dev, ifnr)
  except usb.core.USBError: print("Access denied")
  dev.set_configuration()
  return reattach

def key_close(dev, reattach):
  usb.util.dispose_resources(dev)
  if reattach:
    try: dev.close()
    except AttributeError as e: print("ignore first close")
  else: dev.attach_kernel_driver(2)

def key_endpoint(dev, type):
  cfg = dev.get_active_configuration()
  ifnr = cfg[(2,0)].bInterfaceNumber
  alt = usb.control.get_interface(dev, ifnr)
  intf = usb.util.find_descriptor(cfg, bInterfaceNumber = ifnr,
    bAlternateSetting = alt)
  return usb.util.find_descriptor(intf, custom_match = lambda e:
    usb.util.endpoint_direction(e.bEndpointAddress) == type)

def key_write(dev):
  ep = key_endpoint(dev, usb.util.ENDPOINT_OUT)
  data = b"\x06\x00\x00"
  ep.write(struct.pack("II", len(data), 3), timeout=6000)

def key_read(dev):
  ep = key_endpoint(dev, usb.util.ENDPOINT_IN)
  try: return ep.read(0x40, timeout=6000)
  except usb.core.USBTimeoutError as e: print("Error reading response:", e.args)
  return 0

def key_type(type):
  return usb.util.build_request_type(
    type, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)

def key_getreport(dev):
  return dev.ctrl_transfer(key_type(usb.util.CTRL_IN), 9, 0x300, 0, 64)

def key_setreport(dev):
  dev.ctrl_transfer(
    key_type(usb.util.CTRL_OUT), 9, 0x300, 0, (0xff, 1, 0, 0, 0, 0, 0, 0))

def main():
  dev = key_device()
  if dev:
    reattach = key_claim(dev, ifnr = 2)
    key_write(dev)
    print(key_read(dev))
    print(key_getreport(dev))
    key_close(dev, reattach)
    print("OK")
  else: print("Ruhroh!")

if __name__=="__main__": main()
