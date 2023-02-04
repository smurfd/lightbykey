mkdir build
cd build
gcc  -flat_namespace -I/opt/pkg/include/libusb-1.0/ -L/opt/pkg/lib/ -lusb-1.0 ../lightkey.c -o lightkey
DYLD_FORCE_FLAT_NAMESPACE=1 ./lightkey
cd ..
rm -rf build
