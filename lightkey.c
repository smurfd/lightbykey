// Key issue get a bulk-read/write device
// YubiKey 5C NFC works
// YubiKey C Bio does not work so far, different transfer type maby?
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <libusb.h>

typedef unsigned char uc;
typedef struct libusb_device_handle usbdev;

#define IF  0x02
#define IN  0x82
#define OUT 0x02
#define VEN 0x1050
#define PRD 0x0407

int error(char *s, int r) {
  if (r != 0) {printf("Cant %s dev\n", s); exit(0);} return 0;
}

int initdev() {return error("initialize", libusb_init(NULL));}

usbdev *opendev() {
  usbdev *dev = libusb_open_device_with_vid_pid(NULL, VEN, PRD);
  if (!dev) {error("open", -1);}
  return dev;
}

int claimdev(usbdev *dev) {
  libusb_detach_kernel_driver(dev, IF);
  return error("open", libusb_claim_interface(dev, IF));
}

int resetdev(usbdev *dev) {
  int ret = libusb_reset_device(dev);
  usleep(10000);
  ret |= libusb_clear_halt(dev, OUT);
  ret |= libusb_clear_halt(dev, IN);
  usleep(10000);
  return ret;
}

int writedev(usbdev *dev, char *wrt, int *wrtnr) {
  return error("write", libusb_bulk_transfer(dev, OUT, (uc*)wrt, 3, wrtnr, 0));
}

int readdev(usbdev *dev, char *rd, int *rdnr) {
  return error("read", libusb_bulk_transfer(dev, IN, (uc*)rd, 64, rdnr, 0));
}

int releasedev(usbdev *dev) {
  return error("release", libusb_release_interface(dev, IF));
}

int main() {
  char wrt[128] = {0}, rd[128] = {0};
  int ret = 0, wrtnr;

  ret |= initdev();
  usbdev *dev = opendev();
  ret |= claimdev(dev);
  ret |= resetdev(dev);
  ret |= writedev(dev, wrt, &wrtnr);
  ret |= readdev(dev, rd, &wrtnr);
  printf("ret = %d\n", ret);
  printf("data: %d : %x : %x\n", wrtnr, rd[0], rd[1]);
  for (int i=0; i < 64; i++) {printf("0x%x ", rd[i]);} printf("\n");
  ret |= releasedev(dev);
  if (!ret) printf("Read / Write : OK\n");
}
