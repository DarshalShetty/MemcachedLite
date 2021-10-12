# Deploying to cloud (GCP)

## Properties stored in ```config.sh```
These properties are made available in the current shell by running
```bash
source config.sh
```
- ```ZONE``` -  The regional zone in which gcloud compute instances would be
  spawned in.
- ```IMAGE_FAMILY``` and ```IMAGE_PROJECT``` - Determines the operating
  system of the spawned compute instance.
- ```MACHINE_TYPE``` - Determines how many CPU cores and how much RAM the
  spawned compute instance will have.
- ```GCLOUD_USERNAME``` - The Google cloud account username. Used while running
  SCP
  and SSH commands in scripts.
  
## Steps taken to manually run things in GCP on the command line
- Install the ```gcloud``` CLI SDK by following instructions [here](https://cloud.google.com/sdk/docs/install#linux)
- Initialize the SDK with some config and authenticate our account with the 
  following command:
```bash
gcloud init
```
- Create a network using the following command:
```bash
gcloud compute networks create mclite-network
```
- Create firewall rules to allow network traffic
```bash
gcloud compute firewall-rules create mclite-service --network mclite-network --allow tcp:9889 --source-ranges 0.0.0.0/0 --target-tags server
gcloud compute firewall-rules create mclite-allow-ssh --network mclite-network --allow tcp:22 --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create mclite-allow-icmp --network mclite-network --allow icmp --source-ranges 0.0.0.0/0
```
- Create a MemcachedLite server instance
```bash
gcloud compute instances create mclite-server --zone=$ZONE --image-family=$IMAGE_FAMILY --image-project=$IMAGE_PROJECT --machine-type=$MACHINE_TYPE --network=mclite-network --tags=server
 ```
- SSH into server and setup Python. Then write the setup commands used into 
  the script called ```instance_setup.sh``` for automation later.
- Transfer source code using the following command
```bash
gcloud compute scp --zone=$ZONE --compress ../*.py $GCLOUD_USERNAME@mclite-server:~
```
- Transfer startup script using the following command and then run it on the 
  remote instance to start the server
```bash
gcloud compute scp --zone=$ZONE --compress ./server_startup.sh $GCLOUD_USERNAME@mclite-server:~
```
- Run the remote MemcachedLite server
```bash
gcloud compute ssh $GCLOUD_USERNAME@mclite-server --zone=$ZONE --command "bash server_startup.sh"
```
- Create a MemcachedLite client instance
```bash
gcloud compute instances create mclite-client --zone=$ZONE --image-family=$IMAGE_FAMILY --image-project=$IMAGE_PROJECT --machine-type=$MACHINE_TYPE --network=mclite-network --tags=client
 ```
- SSH into client and setup Python using the ```instance_setup.sh``` script 
  that was prepared while setting up the server.
```bash
gcloud compute ssh $GCLOUD_USERNAME@mclite-client --zone=$ZONE --command "bash instance_setup.sh"
```
- Transfer source code to client using the following command
```bash
gcloud compute scp --zone=$ZONE --compress ../*.py $GCLOUD_USERNAME@mclite-client:~
```
- Transfer test scripts to client for use in benchmarking
```bash
gcloud compute scp --zone=$ZONE --compress ../tests/test_*.py $GCLOUD_USERNAME@mclite-client:~
```
- Transfer ```benchmark.sh``` to client for conducting the benchmarking
```bash
gcloud compute scp --zone=$ZONE --compress ./benchmark.sh $GCLOUD_USERNAME@mclite-client:~
```
- Run the ```benchmark.sh``` on client
```bash
gcloud compute ssh $GCLOUD_USERNAME@mclite-client --zone=$ZONE --command "SERVER_HOST=34.138.210.201 bash benchmark.sh"
```
- Server external IP can be fetched with
```bash
gcloud compute instances describe mclite-server --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```
- Fetch log files from client and server before terminating them
```bash
gcloud compute scp --zone=$ZONE --compress $GCLOUD_USERNAME'@mclite-client:~/*.log' ../logs
gcloud compute scp --zone=$ZONE --compress $GCLOUD_USERNAME'@mclite-server:~/*.log' ../logs
```
- Stop all compute instances
```bash
gcloud compute instances stop $(gcloud compute instances list --format 'get(name)') --zone=$ZONE
```
- Delete all compute instances
```bash
gcloud compute instances delete $(gcloud compute instances list --format 'get (name)') --zone=$ZONE -q
```
- Delete all firewall rules
```bash
gcloud compute firewall-rules delete $(gcloud compute firewall-rules list --format 'value(name)') -q
```
- Delete network ```mclite-network```
```bash
gcloud compute networks delete mclite-network -q
```

## Creating ```run_everything.sh```

The steps performed in the previous step manually are automated by writing 
them down in the script ```run_everything.sh``` in the ```deploy``` 
directory. A wait loop was added after running the server so that when the 
client runs its benchmarking scripts, we know that the MemcachedLite service 
would be up and running to receive the client requests. This script can be 
run when current working directory is the deploy folder. After the script is 
run, the server logs, and the client benchmarking logs are stored in the 
```logs``` directory.

## Benchmarking

The script ```deploy/benchmark.sh``` runs the scripts in the ```tests``` 
directory on the remote client. Out of those scripts ```test_stress.py``` is 
the interesting one. It creates multiple connections and performs multiple 
read and write operations with each connection. The time taken to perform 
all read and write operations is then printed to stdout. The 
```deploy/benchmark.sh``` script then runs this python script with 
increasing number of connections until the python script exits with a 
non-zero exit code. The outputs of all the python scripts is written into 
log files that begin with "benchmark". The stress test can go upto 50 
connections after which the client exits because of a timeout error. I 
believe this can be fixed by increasing the timeout setting in the python 
socket client library.


