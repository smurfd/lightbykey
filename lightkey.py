import sys
import time
import usb.core
import usb.util

def key_get():
  # find all usb devices
  dev = usb.core.find(find_all=True)
  for d in dev:
    # Look specificly for Yubico keys
    if usb.util.get_string(d, d.iManufacturer) == "Yubico":
      return d
  return None

def key_claim(dev):
  reattach = False
  dev.set_configuration()
  if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)
    print(dev.is_kernel_driver_active(0))
    reattach = True
  try:
    usb.util.claim_interface(dev, 0)
  except usb.core.USBError:
    print("Access denied")
  return reattach

def key_close(dev, reattach):
  usb.util.dispose_resources(dev)
  if reattach:
    dev.attach_kernel_driver(0)
    dev.close()

def key_endpoint(dev, type):
  cfg = dev.get_active_configuration()
  ifnr = cfg[(0,0)].bInterfaceNumber
  alt = usb.control.get_interface(dev, ifnr)
  intf = usb.util.find_descriptor(cfg, bInterfaceNumber = ifnr,
    bAlternateSetting = alt)
  ep = usb.util.find_descriptor(intf, custom_match = lambda e:
    usb.util.endpoint_direction(e.bEndpointAddress) == type)
  return ep

def key_write(dev):
  ep = key_endpoint(dev, usb.util.ENDPOINT_OUT)
  ep.write("test")

def key_read(dev):
  ep = key_endpoint(dev, usb.util.ENDPOINT_IN)
  try:
    r = ep.read(1, timeout=6000)
    print("READ", r)
  except usb.core.USBError as e:
    print ("Error reading response: {}".format(e.args))

dev = key_get()
if dev:
  reattach = key_claim(dev)
  key_write(dev)
  time.sleep(3)
  key_read(dev) # times out!? i need to poke it in special spot?
  key_close(dev, reattach)
  print("OK")
else:
  print("Ruhroh!")
