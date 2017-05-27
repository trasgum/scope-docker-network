# Scope docker network Plugin

The docker network plugin is a Python application that asks docker for the attached docker network for each container, providing **container-level** name in the [Weave Scope](https://github.com/weaveworks/scope) UI.

## How to Run Scope Volume Count Plugin

* Using a pre-built Docker image

If you want to make sure of running the latest available version of the plugin, you pull the image from docker hub.

```
docker pull trasgum/scope-docker-network:latest
```

To run the Scope Volume Count plugin you just need to run the following command.

```
docker run --rm -ti \
	--net=host \
	-v /var/run/scope/plugins:/var/run/scope/plugins \
        -v /var/run/docker.sock:/var/run/docker.sock \
	--name scope-docker-network trasgum/scope-docker-network:latest
```

* Recompiling an image

```
git clone git@github.com:trasgum/scope-docker-network.git
cd scope-docker-network; docker build -t trasgum/scope-docker-network .;
```

**Note** If Scope docker network plugin has been registered by Scope, you will see it in the list of `PLUGINS` in the bottom right of the UI (see the rectangle in the above figure).
The measured value is showed in the *STATUS* section (see the circle in the above figure).
