# virtio_queue_notify 12644.699 vdev=0x22593e0 n=0x0 vq=0x22594a0
# virtio_notify 7224.836 vdev=0x22593e0 vq=0x22594a0

{
	total_time[$1] += $2;
	if (min_time[$1] == null || $2 < min_time[$1]) {
		min_time[$1] = $2;
	}
	if (max_time[$1] == null || $2 > max_time[$1]) {
		max_time[$1] = $2;
	}
	count[$1]++;
}

END {
	for (event in total_time) {
		if (count[event] == 0) {
			avg_wait = 0;
		} else {
			avg_wait = total_time[event] / count[event];
		}
		printf("\"%s\" count=%d avg_wait=%s min_wait=%s max_wait=%s total_wait=%s\n", event, count[event], avg_wait, min_time[event], max_time[event], total_time[event]);
	}
}
feedly mini