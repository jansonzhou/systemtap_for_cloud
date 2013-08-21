#define _GNU_SOURCE /* for O_DIRECT */

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <err.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>

static unsigned long measure_read_latency(int fd, size_t alignment, size_t size, unsigned int n)
{
	void *buf;
	unsigned int i;
	ssize_t nread;
	struct timespec start;
	struct timespec finish;
	unsigned long latency;

	if (posix_memalign(&buf, alignment, size) != 0) {
		errx(1, "posix_memalign failed");
	}

	if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) {
		err(1, NULL);
	}

	for (i = 0; i < n; i++) {
		nread = read(fd, buf, size);
		if (nread != size) {
			err(1, NULL);
		}
	}

	if (clock_gettime(CLOCK_MONOTONIC, &finish) != 0) {
		err(1, NULL);
	}

	latency = ((finish.tv_sec - start.tv_sec) * 1000000000LL + finish.tv_nsec - start.tv_nsec) / n;

	free(buf);

	return latency;
}

static void usage(char *progname)
{
	fprintf(stderr, "usage: %s <path> <read-operations>\n", progname);
	exit(1);
}

int main(int argc, char **argv)
{
	const char *device;
	int fd;
	unsigned int n;
	unsigned long latency_ns;

	if (argc != 3) {
		usage(argv[0]);
	}
	device = argv[1];
	n = atoi(argv[2]);

	fd = open(device, O_RDONLY | O_DIRECT);
	if (fd < 0) {
		err(1, NULL);
	}

	latency_ns = measure_read_latency(fd, 4096, 4096, n);
	printf("latency (ns) = %lu\n", latency_ns);

	close(fd);
	return 0;
}
feedly mini