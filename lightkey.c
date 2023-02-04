// key issue get a bulk-read/write device like a YubiKey 5C NFC, YubiKey C Bio does not work so far
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <errno.h>
#include <libusb.h>
#include <unistd.h>

#define IF  0x02
#define IN  0x82
#define OUT 0x02
#define VEN 0x1050
#define PRD 0x0407
static struct libusb_device_handle *dev = NULL;

int main() {
  char wrt[128] = {0}, rd[128] = {0}; wrt[0] = 0x10; wrt[1] = 0x04; wrt[2] = 2;
  int ret = libusb_init(NULL), wrtnr;
  if (ret < 0) {printf("Cant initialize dev\n"); exit(0);}

  dev = libusb_open_device_with_vid_pid(NULL, VEN, PRD);
  if (!dev) {printf("Cant open dev\n"); exit(0);}

  libusb_detach_kernel_driver(dev, IF);
  ret = libusb_claim_interface(dev, IF);
  if (ret < 0) {printf("Cant claim dev\n"); exit(0);}

  libusb_reset_device(dev);
  usleep(10000);
  libusb_clear_halt(dev, OUT);
  libusb_clear_halt(dev, IN);
  usleep(10000);

  ret = libusb_bulk_transfer(dev, OUT, (unsigned char *)wrt, 3, &wrtnr, 0);
  if (ret != 0) {printf("Cant write to dev\n"); exit(0);}

  ret = libusb_bulk_transfer(dev, IN, (unsigned char *)rd, 64, &wrtnr, 0);
  if (ret != 0) {printf("Cant read from dev\n"); exit(0);}

  printf("data: %d : %x : %x\n", wrtnr, rd[0], rd[1]);
  for (int i=0; i < 64; i++) {printf("0x%x ", rd[i]);} printf("\n");
  libusb_release_interface(dev, IF);
}
