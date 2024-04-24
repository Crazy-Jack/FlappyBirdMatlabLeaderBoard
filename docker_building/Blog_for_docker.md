Problem:
(django) ➜  docker_building git:(master) ✗ sudo docker build -t flappy_1.0 .                                                                                         
[+] Building 0.2s (2/3)                                                                                                                         docker:desktop-linux 
[+] Building 0.4s (3/3) FINISHED                                                                                                                docker:desktop-linux 
 => [internal] load build definition from Dockerfile                                                                                                            0.0s 
 => => transferring dockerfile: 639B                                                                                                                            0.0s 
 => [internal] load .dockerignore                                                                                                                               0.0s 
 => => transferring context: 2B                                                                                                                                 0.0s 
 => ERROR [internal] load metadata for docker.io/library/python:3.9-slim                                                                                        0.3s 
------                                                                                                                                                               
 > [internal] load metadata for docker.io/library/python:3.9-slim:                                                                                                   
------                                                                                                                                                               
Dockerfile:2                                                                                                                                                         
--------------------                                                                                                                                                 
   1 |     # Use an official Python runtime as a parent image                                                                                                        
   2 | >>> FROM python:3.9-slim                                                                                                                                      
   3 |                                                                                                                                                               
   4 |     # Set the working directory in the container                                                                                                              
--------------------                                                                                                                                                 
ERROR: failed to solve: python:3.9-slim: error getting credentials - err: exit status 1, out: ``   

Solution:
MacOS - I just had to change the docker config file.
The “credsStore” was “desktop” and changed it to “osxkeychain”.
used nano to do it. sudo nano ~/.docker/config.json

=======

docker stop [CONTAINER_ID or NAME]
even if it stops, the container is not removed.

docker rm [CONTAINER_ID or NAME]
this will remove the container. but not the image. 

or 
docker rm -f [CONTAINER_ID or NAME]
to stop the container before removing it.

To remove images, use rmi
docker rmi -f 9544550ed7a2

====
clean up all stopped container and images 
docker system prune

to clean up all unused containers and images
docker system prune -a




==== to run the image via container

docker run -d -p 8000:8000 mydjangoapp(tag)

===== database
??

python3.12 manage.py makemigrations
python3.12 manage.py migrate

this will migrate the database with users which would be useful for later development