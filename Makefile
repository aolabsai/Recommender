build:
	export DOCKER_BUILDKIT=1
	docker build --secret id=env,src=.env --platform linux/amd64 -t "ao_recommender_app" .
	docker tag ao_recommender_app aolabs/recommender

run:
	docker run -p 8501:8501 aolabs/recommender:latest

push:
	docker push aolabs/recommender:latest
