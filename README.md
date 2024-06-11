# Similarity search web service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/similarity-webservice/badge/)](https://similarity-webservice.readthedocs.io/)
[![codecov](https://codecov.io/gh/ssciwr/similarity-webservice/branch/main/graph/badge.svg)](https://codecov.io/gh/ssciwr/similarity-webservice)

Perform similarity search against an uploaded dataset of images.

## Features

This project implements a web service that allows to:
* perform image similarity search against custom datasets
* directly link the resulting images to entries in a data repository
* work directly with data hosted on [HeidICON](https://heidicon.ub.uni-heidelberg.de), Heidelberg University's media data base

## Installation

The recommended way of setting up an instance of similarity webservice is to use Docker.

### Docker

```
git clone https://github.com/ssciwr/similarity-webservice.git
cd similarity-webservice
docker compose up
```

For customization of the deployment, you may want to look at and tweak
* `docker-compose.yml` for e.g. mounted volumes
* `./frontend/nginx.conf` for SSL setup

The page will be served to `localhost`.

### Development Installation

Required setup:

```bash
git clone https://github.com/ssciwr/similarity-webservice.git
cd similarity-webservice
```

Now, you need to start the backend:
```bash
python -m pip install ./backend
similarity_webservice
```

And separately, the frontend:
```bash
cd frontend
npm install
npm run dev
```

## Usage

### Usage as a web service

Accessing the web service through a web browser, you can upload a query image and look at the results.
In order to create new collections you should do the following:

* Click on `Collection Management`
* Enter your API key (see below for generation)
* At the bottom of the page, enter a new name for the dataset and determine whether the data is located on HeidICON.
  * If the data is located on HeidICON, provide the name of the tag that is applied to the data on HeidICON.
  * Otherwise, click the `Upload Data` button and select a CSV file. It is expected to have a row per image and two columns: One for the image URL and one for the URL to link to when clicking on the image.
* Click the `Finetune model` button (this may take a while)

### Usage via the REST API

This service can be used via a REST API. We refer to the [API documentation](https://similarity-webservice.readthedocs.io/en/latest/demo.html#)

### Creating an API key

This will typically be done by a systems administrator with command line access to the running instance.

```bash
docker exec -it <containername> bash
python -m similarity_webservice.auth --help
python -m similarity_webservice.auth create
```

The name of the running backend container can be determined using `docker ps -a`.

## License

This work is licensed under the MIT license.
