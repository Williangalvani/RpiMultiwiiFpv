file=./file.sh
process=0
cp running.sh file.sh
while [ 1 ]; do
  if [ -f "$file" ]; then

    if [ ! $process = 0 ]; then
        kill -9 $process
        pkill  -9 raspivid
    fi
    cp $file running.sh
    sh ./running.sh&
    process=$!
    rm $file
  else
    sleep 1s
  fi

done
#raspivid -n -w 1920 -h 1080 -b 1200000 -fps 30 -t 5000 -o - 
#raspivid -n -w 1024 -h 768 -b 1200000 -fps 30 -t 5000 -o -

