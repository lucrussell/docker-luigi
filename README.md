## Readme
This project sets up a data engineering pipeline for harvesting top author data from Medium. It demonstrates some features of [Luigi](https://github.com/spotify/luigi):

- parallel processing
- running inside Docker
- unit testing Luigi tasks

There is a full write up [here](https://towardsdatascience.com/build-a-pipeline-for-harvesting-medium-top-author-data-c4d7ed73729f).

## Quickstart
Start the services with:

    docker-compose up -d

This will start the Luigi workflow service and the `example` service.

![luigi_at_work_harvesting_medium_data](luigi_at_work.png)
