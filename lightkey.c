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
  if (r != 0) {printf("Cant %s dev\n", s); return -1;} return 0;
}

int initdev() {return error("initialize", libusb_init(NULL));}

int opendev(usbdev **dev) {
  (*dev) = libusb_open_device_with_vid_pid(NULL, KEY[3], KEY[4]);
  if (!dev) {return error("open", -1);} else return 0;
}

int claimdev(usbdev *dev) {
  libusb_detach_kernel_driver(dev, KEY[0]);
  return error("open", libusb_claim_interface(dev, KEY[0]));
}

int resetdev(usbdev *dev, int ret) {
  ret |= libusb_reset_device(dev);
  ret |= libusb_clear_halt(dev, KEY[2]);
  ret |= libusb_clear_halt(dev, KEY[1]);
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

void printdev(int wrtnr, char *d) {
  printf("data: %d : %x : %x\n", wrtnr, d[0], d[1]);
  for (int i=0; i < 64; i++) {printf("0x%x ", d[i]);} printf("\n");
}

int main() {
  char wrt[128] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x8f}, rd[128] = {0};
  int ret = 0, wrtnr;
  usbdev *dev = NULL;

  ret |= initdev();
  ret |= opendev(&dev);
  ret |= claimdev(dev);
  ret |= resetdev(dev, ret);
  ret |= writedev(dev, wrt, &wrtnr);
  ret |= readdev(dev, rd, &wrtnr);
  ret |= releasedev(dev);
  printdev(wrtnr, rd);

  if (!ret) {printf("OK\n");} else {printf("ruhroh!\n");}
}
