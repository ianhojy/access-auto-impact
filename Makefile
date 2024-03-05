# Define variables for Docker commands
IMAGE_NAME = access_impact_image
CONTAINER_NAME = access_impact_container
PORT = 8501
TAG = latest

default: all
all: build run cleanup

build:
	docker build -t $(IMAGE_NAME):$(TAG) .

run:
	-docker run --rm -it --name $(CONTAINER_NAME) -p $(PORT):$(PORT) $(IMAGE_NAME):$(TAG)

cleanup:
	docker rmi $(IMAGE_NAME):$(TAG)
	docker image prune -f
	docker container prune -f
	docker volume prune -f