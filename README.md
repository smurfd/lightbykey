# lightbykey
Can we handle a Yubico key from Python?

Install LibUSB
```
$ brew install libusb
or
$ pkgin install libusb
```
From a shell run thia to verify that python can find the library
```
python3 -c "import ctypes.util; print(ctypes.util.find_library('usb'))"
```
If you are on a mac it should point you to a .dylib
if on linux you should see the path to a .so file
