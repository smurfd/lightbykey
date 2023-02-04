# lightkey
Can we handle a Yubico key from C & Python?

Install LibUSB
```
$ brew install libusb1
or
$ pkgin install libusb1
```
From a shell run this to verify that python can find the library
```
python3 -c "import ctypes.util; print(ctypes.util.find_library('usb'))"
```
If you are on a mac it should point you to a .dylib
if on linux/bsd you should see the path to a .so file

```
$ sudo python3 lightkey.py
```
```
$ sudo ./build.sh
```
<br>
Now C & Python can read/write from this model :<br>
YubiKey 5C NFC<br>
