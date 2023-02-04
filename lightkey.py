import sys, time, struct
import usb.core, usb.util

def initdev():
  dev = usb.core.find(find_all=True) # find all usb devices
  for d in dev: # Look specificly for Yubico keys
    if usb.util.get_string(d, d.iManufacturer) == "Yubico": return d
  return None

def claimdev(dev, ifnr = 0, att = False):
  dev.detach_kernel_driver(ifnr)
  if not att:
    if dev.is_kernel_driver_active(ifnr):
      if not dev.is_kernel_driver_active(ifnr): att = True
  try: usb.util.claim_interface(dev, ifnr)
  except usb.core.USBError: print("Access denied");
  dev.set_configuration()
  return att

def closedev(dev, ifnr = 0, att = False):
  usb.util.dispose_resources(dev)
  if att:
    try: dev.close()
    except AttributeError as e:
      print("ignore first close");
      return 1
  else: dev.attach_kernel_driver(ifnr); return 0;

def getdevept(dev, type):
  cfg = dev.get_active_configuration()
  ifnr = cfg[(2,0)].bInterfaceNumber
  alt = usb.control.get_interface(dev, ifnr)
  intf = usb.util.find_descriptor(cfg, bInterfaceNumber = ifnr,
    bAlternateSetting = alt)
  return usb.util.find_descriptor(intf, custom_match = lambda e:
    usb.util.endpoint_direction(e.bEndpointAddress) == type)

def writedev(dev):
  ep = getdevept(dev, usb.util.ENDPOINT_OUT)
  data = b"\x06\x00\x00"
  return ep.write(struct.pack("II", len(data), 3), timeout=6000)

def readdev(dev):
  ep = getdevept(dev, usb.util.ENDPOINT_IN)
  try: return ep.read(0x40, timeout=6000)
  except usb.core.USBTimeoutError as e: print("Error reading response:", e.args)
  return 0

def getdevtype(type):
  return usb.util.build_request_type(
    type, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)

def getreportdev(dev):
  return dev.ctrl_transfer(getdevtype(usb.util.CTRL_IN), 9, 0x300, 0, 64)

def setdevreport(dev):
  dev.ctrl_transfer(
    getdevtype(usb.util.CTRL_OUT), 9, 0x300, 0, (0xff, 1, 0, 0, 0, 0, 0, 0))

def main():
  dev = initdev()
  if dev:
    att = claimdev(dev, ifnr = 2)
    writedev(dev)
    print("read =", readdev(dev))
    print("report =", getreportdev(dev))
    closedev(dev, 2, att)
    print("OK")
  else: print("Ruhroh!")

if __name__=="__main__": main()
