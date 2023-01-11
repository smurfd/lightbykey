import sys
import usb.core
import usb.util

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

dev = get_lightbykey_dev()
if dev:
  print(dev)
  print(hex(dev.idVendor), hex(dev.idProduct))
  print(hex(get_lightbykey_item(dev.idVendor)), hex(get_lightbykey_item(dev.idProduct)))
  print(hex(get_lightbykey_ven(dev)), hex(get_lightbykey_pro(dev)))

  #dev1 = usb.core.find(idVendor=0x1050, idProduct=0x402)
  #print(dev1)
  try:
    usb.util.claim_interface(dev, 0)
  except usb.core.USBError:
    print("Access denied") #this should work, issue on mac with libusb
