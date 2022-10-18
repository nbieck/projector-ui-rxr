# Docker for ROS2

A repository to setup a very basic environment of ROS2

## Requirements 
- docker 
- docker-compose (https://docs.docker.com/compose/install/)
## How to use 

1. Clone this repository
```
git clone git@github.com:nbieck/projector-ui-rxr.git
```
2. Run an example `docker-compose`, which runs a talker and a listener program on separated containers
```
docker-compose build # This command automatically builds an image if there's no image
```
3. Build the program in ./workspace/src/
```
docker-compose up colcon
```

4. After building the program, you can run program under ./workspace/src/, like
   
```
# sample program
docker-compose up sample
```

```
# basic pub-sub program 
# terminal 1
docker-compose up pub

# terminal 2
docker-compose up sub
```


trying realsense
```
docker-compose up realsense
```


## TODO

- Add setting for GUI applications
