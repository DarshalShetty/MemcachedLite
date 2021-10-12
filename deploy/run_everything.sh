#!/usr/bin/env bash

# this script will only work when current working directory is the
# deploy directory of this project

# load config
source config.sh

#: <<'END'
# network setup
gcloud compute networks create mclite-network

gcloud compute firewall-rules create mclite-service --network mclite-network --allow tcp:9889 --source-ranges 0.0.0.0/0 --target-tags server
gcloud compute firewall-rules create mclite-allow-ssh --network mclite-network --allow tcp:22 --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create mclite-allow-icmp --network mclite-network --allow icmp --source-ranges 0.0.0.0/0

# create instances
gcloud compute instances create mclite-server --zone="$ZONE" --image-family="$IMAGE_FAMILY" --image-project="$IMAGE_PROJECT" --machine-type="$MACHINE_TYPE" --network=mclite-network --tags=server
gcloud compute instances create mclite-client --zone="$ZONE" --image-family="$IMAGE_FAMILY" --image-project="$IMAGE_PROJECT" --machine-type="$MACHINE_TYPE" --network=mclite-network --tags=client
#END

#: <<'END'
# common instance setup
for SERVER_NAME in $(gcloud compute instances list --format 'get(name)')
do
gcloud compute scp --zone="$ZONE" --compress ./instance_setup.sh "$GCLOUD_USERNAME"@"$SERVER_NAME":~
gcloud compute ssh "$GCLOUD_USERNAME"@"$SERVER_NAME" --zone="$ZONE" --command "bash instance_setup.sh"
gcloud compute scp --zone="$ZONE" --compress ../*.py "$GCLOUD_USERNAME"@"$SERVER_NAME":~
done
#END

# Run MemcachedLite server
gcloud compute scp --zone="$ZONE" --compress ./server_startup.sh "$GCLOUD_USERNAME"@mclite-server:~
gcloud compute ssh "$GCLOUD_USERNAME"@mclite-server --zone="$ZONE" --command "bash server_startup.sh"

# fetch external IP of MemcachedLite server
SERVER_IP=$(gcloud compute instances describe mclite-server --zone="$ZONE" --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

# wait until MemcachedLite port is open (this check adds a lot lines to server log)
MAX_RETRIES=60
while ! nc "$SERVER_IP" 9889 -w 1 -z ; do
    if [ $MAX_RETRIES -eq 0 ]; then
      echo "Max retries exceeded. MemcachedLite service is unavailable for too long"
      exit 1
    fi
    sleep 1
    echo "MemcachedLite server not ready. Retrying after a second"
    MAX_RETRIES=$((MAX_RETRIES-1))
done

# Run benchmarking scripts on client
gcloud compute scp --zone="$ZONE" --compress ../tests/test_*.py "$GCLOUD_USERNAME"@mclite-client:~
gcloud compute scp --zone="$ZONE" --compress ./benchmark.sh "$GCLOUD_USERNAME"@mclite-client:~
gcloud compute ssh "$GCLOUD_USERNAME"@mclite-client --zone="$ZONE" --command "SERVER_HOST=$SERVER_IP bash benchmark.sh"

# Fetch log files from client and server before terminating them
rm -rf ../logs
mkdir ../logs
gcloud compute scp --zone="$ZONE" --compress "$GCLOUD_USERNAME"'@mclite-client:~/*.log' ../logs
gcloud compute scp --zone="$ZONE" --compress "$GCLOUD_USERNAME"'@mclite-server:~/*.log' ../logs

: <<'END'
# Resource cleanup
gcloud compute instances stop $(gcloud compute instances list --format 'get(name)') --zone=$ZONE
gcloud compute instances delete $(gcloud compute instances list --format 'get (name)') --zone=$ZONE -q
gcloud compute firewall-rules delete $(gcloud compute firewall-rules list --format 'value(name)') -q
gcloud compute networks delete mclite-network -q
END