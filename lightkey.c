// https://www.linuxjournal.com/article/8145
// https://xcellerator.github.io/posts/yubikey/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <libusb.h>

typedef unsigned char uc;
typedef struct libusb_device_handle usbdev;

// Yubikey C Bio : 0x00, 0x84, 0x04, 0x1050, 0x0402
// const static int KEY[5] = {0x00, 0x84, 0x04, 0x1050, 0x0402};
// Yubikey 5C NFC: 0x02, 0x82, 0x02, 0x1050, 0x0407 (Bulk Read & write works)
const static int KEY[5] = {0x02, 0x82, 0x02, 0x1050, 0x0407};
// IF, IN, OUT, VEN, PRD

int error(char *s, int r) {
  if (r != 0) {printf("Cant %s dev\n", s); exit(0);} return 0;
}

int initdev() {return error("initialize", libusb_init(NULL));}

usbdev *opendev() {
  usbdev *dev = libusb_open_device_with_vid_pid(NULL, KEY[3], KEY[4]);
  if (!dev) {error("open", -1);}
  return dev;
}

int claimdev(usbdev *dev) {
  libusb_detach_kernel_driver(dev, KEY[0]);
  return error("open", libusb_claim_interface(dev, KEY[0]));
}

int resetdev(usbdev *dev) {
  int ret = libusb_reset_device(dev);
  usleep(10000);
  ret |= libusb_clear_halt(dev, KEY[2]);
  ret |= libusb_clear_halt(dev, KEY[1]);
  usleep(10000);
  return ret;
}

int writedev(usbdev *dev, char *wrt, int *wrtnr) {
  return error("write", libusb_bulk_transfer(dev, KEY[2], (uc*)wrt, 8, wrtnr, 0));
}

int readdev(usbdev *dev, char *rd, int *rdnr) {
  return error("read", libusb_bulk_transfer(dev, KEY[1], (uc*)rd, 64, rdnr, 0));
}

int releasedev(usbdev *dev) {
  return error("release", libusb_release_interface(dev, KEY[0]));
}

int main() {
  char wrt[128] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x8f}, rd[128] = {0};
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
