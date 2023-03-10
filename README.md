# Linkat

Linkat, short for 'Linux Kernel Allocation Tracer,' is a small tool that allows you to trace the allocation that yout poc makes in kernel memory on a Linux system and visualize it in a user-friendly interface. It utilizes ftrace, so you need to have it installed to use this tool. Linkat sets ftrace parameters and parses the logs to provide you with detailed information about kernel memory allocation.

![alt text](https://i.ibb.co/RjvXFyK/Capture-d-cran-2023-02-15-202702.png)



## Installation

To install Linkat, follow the steps given below:
### 1. Clone the repository

Clone the Linkat repository in your host machine using the following command:

```bash
git clone https://github.com/AntoineBlaud/linkat.git
```

### 2. Build the Docker image

After cloning the repository, go to the Linkat directory and run the docker-build.sh script to build the Docker image:

```bash
cd linkat
./docker-build.sh
```

###  3. Install Linkat on the target machine

Next, install Linkat on the target machine by cloning the repository and running the setup.py script:


```bash
git clone https://github.com/linkat/linkat.git
cd linkat
python3 setup.py install
```
## Usage

Follow the steps below to use Linkat:
###  1. Launch Linkat

Inside your target machine, launch linkat-run using the following command:
```bash
linkat-run
```
### 2. Set markers

Inside your poc call the function 'marker' at least once, which is located inside the 'helper.h' file.
###  3. Run your poc

Quickly run your poc after launching linkat-run. The longer you wait, the more time Linkat will take to parse the log.
### 4. Parse the log and fetch data

Once your poc has finished running, press enter to allow Linkat to parse the log and fetch data. If Linkat asks for it, enter the process from the ones proposed.
### 5. Copy trace.json to your host machine

Copy the trace.json file to your host machine.
### 6. Run the Docker container

After copying the trace.json file to your host machine, run the Docker container using the following command:

```bash
./docker-run.sh <your-trace.json path>
```

### 7. Enjoy

Finally, open your browser and go to localhost:3000 to enjoy using Linkat. Move the range bar to display the progress/evolution

## Further information

Rendering a large memory trace could take a few seconds (approximately 1 second per 3000 entries) when the poc makes a large amount of allocations, so please be patient.
Also, this program could easily be extended to trace any pre-compiled program, but I don't see the need for it.

## Conclusion

Linkat is a useful tool for tracing kernel memory allocation on Linux systems. By following the installation and usage steps given above, you can easily use Linkat to trace allocation made by your poc in kernel memory.
