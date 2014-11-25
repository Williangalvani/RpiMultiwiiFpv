sh rpivid.sh | \
     gst-launch-1.0 -v fdsrc !  h264parse ! rtph264pay config-interval=10 pt=96 ! \
     udpsink host=$1 port=5004
status = "streaming"

echo "status:$status" > /dev/shm/streamingstatus
