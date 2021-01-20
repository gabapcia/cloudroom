#!/bin/bash


get_rabbitmq_logs()
{
    echo $(docker logs rabbitmq | grep -ios "server startup complete")
}

while [ -z "$(get_rabbitmq_logs)" ]; do
    sleep 0.5
done

echo "RabbitMQ started"
