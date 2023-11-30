sudo apt-get update
sudo apt-get install docker.io
sudo docker build -t my-app .
sudo docker run -d -p 8080:8080 my-app
