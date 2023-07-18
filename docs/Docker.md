### Docker commands

##### Commands for docker image

For this project run docker and docker-compose commands from project dir

Eg for Autobots App
- docker build -t registry.gitlab.com/meetkiwi/autobots:main -f dockerfile .
- docker login registry.gitlab.com
- docker push registry.gitlab.com/meetkiwi/autobots:main
- docker pull registry.gitlab.com/meetkiwi/autobots:main
- docker run -d -p 80:80 registry.gitlab.com/meetkiwi/autobots:main

Run on Local:
- docker run -p 80:80 --name autobots --env-file .env.local registry.gitlab.com/meetkiwi/autobots:main