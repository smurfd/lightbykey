import sys
import usb.core
import usb.util

# Run with : sudo python3 lightbykey.py

def get_lightbykey_dev():
  # find all usb devices
  dev = usb.core.find(find_all=True)
  for d in dev:
    # Look specificly for Yubico keys
    if usb.util.get_string(d, d.iManufacturer) == "Yubico":
      return d
  return None

def get_lightbykey_item(opt):
  return opt

def get_lightbykey_ven(dev):
  return dev.idVendor

def get_lightbykey_pro(dev):
  return dev.idProduct

def claim_lightbykey(dev):
  reattach = False
  dev.set_configuration()
  if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)
    print(dev.is_kernel_driver_active(0))
    reattach = True
  try:
    usb.util.claim_interface(dev, 0)
  except usb.core.USBError:
    print("Access denied") #this should work, issue on mac with libusb
  return reattach

def close_lightbykey(dev, reattach):
  usb.util.dispose_resources(dev)
  if reattach:
    dev.attach_kernel_driver(0)

def write_stuff(dev):
  cfg = dev.get_active_configuration()
  interface_number = cfg[(0,0)].bInterfaceNumber
  alternate_setting = usb.control.get_interface(dev, interface_number)
  intf = usb.util.find_descriptor(cfg, bInterfaceNumber = interface_number, bAlternateSetting = alternate_setting)

  ep = usb.util.find_descriptor(intf,custom_match = lambda e: \
    usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
  ep.write("test")

dev = get_lightbykey_dev()
if dev:
  print(dev)
  print(hex(get_lightbykey_ven(dev)), hex(get_lightbykey_pro(dev)))
  reattach = claim_lightbykey(dev)
  write_stuff(dev)
  close_lightbykey(dev, reattach)
  print("OK")
else:
  print("Ruhroh!")
