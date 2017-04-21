# Devour Example App

This app is an example app built using the [devour](https://github.com/brandoshmando/devour) python package. It is meant to
serve as a simple example of how devour can help you integrate kafka data streams into your python project.


### Setup

The most difficult task is setting up a kafka environment locally. For this, we are going to use [docker](https://www.docker.com/)
and [Spotify's kafka/zookeeper docker container](https://github.com/spotify/docker-kafka). So we'll do the easy stuff first...

Clone devour and cd into `devour/examples/django/django-example`. Create your virtualenv and install dependencies with:

```python
pip install -r requirements.txt
```
Whew, so easy!

Now, checkout [kafka's quickstart guide](https://kafka.apache.org/quickstart) for installation instructions.

Visit [docker's website](https://www.docker.com/products/docker#/mac) and follow instructions for installing and running
docker.

Once docker is up and running, run the following command to pull in the kafka container:

```
docker pull spotify/kafka
```

To fire up a new virtual machine, run the following:

```
docker-machine start default
```

Once the machine has started, set up the env within your shell by running the following:

```
eval $(docker-machine env)
```

You're now ready to fire up kafka and zookeeper, with the following:

```
docker run -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=`docker-machine ip \`docker-machine active\`` --env ADVERTISED_PORT=9092 spotify/kafka
```

Next, you'll set up the shell environments for the web server and consumer. Open two new shell
tabs and run the following in both:

```
eval $(docker-machine env)

export KAFKA=`docker-machine ip \`docker-machine active\``:9092
export ZOOKEEPER=`docker-machine ip \`docker-machine active\``:2181
```

For the next step, kafka's bin must be in your path. For me, it was located at `/usr/local/kafka/bin`
You'll want two differrent topics for the example app: ``:

`kafka-topics.sh --create --zookeeper $ZOOKEEPER --replication-factor 1 --partitions 1 --topic test`

Finally, we can fire up the producer and consumer. Make sure that you are in the root folder of `devour-sample-app` in
both of the previously opened tabs.

In one of the tabs, fire up the producer with:

```
python src/producer.py
```

And in the other tab, fire up the consumer with:

```
devour default
```

Wahoo! Now in the producer tab, you can send simply by typing in your desired message and hitting enter.
For the current `DefaultConsumer`, the message must be a json serializable dict with two keys, x and y, that have `int` values (Ex. `{"x":1, "y":3}`)
You should see the output of the `DefaultConsumer`'s digest message, which is adding x and y.

When you're ready, take a look at the [Devour readme](https://github.com/brandoshmando/devour) and make changes
to the default consumer's settings and digest method to get a better idea of how devour helps implement your kafka setup.
Or write your own Devour consumer!
