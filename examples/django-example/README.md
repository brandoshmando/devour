# Devour Example App

This app is an example app built using the [devour](https://github.com/brandoshmando/devour) python package. It is meant to
serve as a simple example of how devour can help you integrate kafka data streams into your python project.


### Setup

The most difficult task is setting up a kafka environment locally. For this, we are going to use [docker](https://www.docker.com/)
and [Spotify's kafka/zookeeper docker container](https://github.com/spotify/docker-kafka). So we'll do the easy stuff first...

Clone devour and cd into `devour/examples/django-example`. Create your virtualenv and install dependencies with:

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
You'll want two differrent topics for the example app: `test` and `math`. Run the following:

`kafka-topics.sh --create --zookeeper $ZOOKEEPER --replication-factor 1 --partitions 1 --topic test`

`kafka-topics.sh --create --zookeeper $ZOOKEEPER --replication-factor 1 --partitions 1 --topic math`

Now we can start the web server.

In one of the tabs, from the root of the project, fire up the web server:

```python
python manage.py runserver localhost:5000
```


#### Simple message

The "simple message" kafka flow is simply an interface to create a `str` message and observing how said
message is produced automatically by devour and consumed by your consumer.

To fire up the consumer, run the following in your remaining shell tab:


```
./python manage.py consume simple_message
```


Now visit http://localhost:5000/message/simple/

Enter any message you like and POST. You'll see that it's contents are printed to the consumer's shell tab.

Visit http://localhost:5000/message/simple/<simple message id>/

PUT/PATCH to your existing message and you'll see that the updated message is printed to the consumer's shell tab.



#### Math

The "problems" kafka flow adds slightly more complexity. You'll create a `Problem` with a list of integers.
The consumer will then take those integers and find the least common multiple of the set, storing them in a
`Solution` record.

Fire up the consumer, with the following:


```
python manage.py consume problems
```

Visit http://localhost:5000/problems/

Enter a comma separated set of integers and POST. You'll see the least common multiple and the event printed
to your consumer tab

Visit http://localhost:5000/problems/<problem id>/

Change the values in your existing `Problem`, and PUT/PATCH. You'll see a the new lease common multiple and the
event printed to your consumer tab.


Wahoo! Devour was designed to provide you with a set of flexible tools that enable you to quickly create kafka
workflows. There is no "standard" way to use it. Play around. Bend these tools to your will. Break things. Submit issues. All
of this will help improve devour for everyone!
