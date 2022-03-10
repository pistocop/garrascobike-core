# garrascobike-core

> Core of the Garrascobike recommendation system

## Intro

- Use this package to create the recommendation model used for the garrascobike project.<br>
- Folders structure:
    - `./garrascobike/` - folder with all the python scripts that you should run consequentially to analyze the text and build a recommendation model
      - Python version: `python 3.8.5`
    - `./notebooks/` - Jupyter notebooks used to explore the data, validate the hypothesis or test ML models

## Architecture

### Entities extraction

<img src="https://user-images.githubusercontent.com/31094729/157610564-d257875d-a57d-4a78-9631-4ca9abd36446.jpg" width="60%" height="60%">

**Functionalities**

- Take the subreddit comments in input
- Extract the entities using unsupervised ML model with the [Spacy](https://spacy.io/) library
  - Is suggested to run this code on [Colab](https://colab.research.google.com/) to speed up the ML process using GPU
- Store the comment's entities on parquet file
- Load the entities from parquet file to Elasticsearch (ES) instance
  - How run ES locally: docker setup [guide](https://www.pistocop.dev/posts/es_engineer_exam_notes/#run-es-locally-docker-setup)

### Recommendation builder

<img src="https://user-images.githubusercontent.com/31094729/157610572-93f75519-fc93-4e59-95dd-e252d78b3b1a.jpg" width="60%" height="60%">

**Functionalities**
- Take the entities of type `PRODUCT` from ES
- Group the entities by `submission_id` (the Reddit thread to which the comment belong)
- Build a matrix of dimension `len(threads_unique) x len(products_unique)`
- Train a `NearestNeighbors` model to make the recommendations
- Store the ML model

------------------

## Technologies insights 

### Entities extraction

- Store the entities in `parquet` for better compatibility with future uses - [source](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)

### Correlation extraction

- Optimize memory usage limiting the number of fields retrieved from elasticsearch with `_source`:
    - size `products_list` no `_source`: `289805320`
    - size `products_list` with `_source`: `29423384` (89% memory saved)
    - Memory size measured with [this approach](https://stackoverflow.com/questions/13530762/how-to-know-bytes-size-of-python-object-like-arrays-and-dictionaries-the-simp)


## 💤 TODO
- [ ] 🔥 Automatically store the `brands.csv` file
- [ ] Can we speed up entities extractions with batch approach?
- [ ] How manage the correlation between spacy models and requirements.txt?
    - [ ] Support multiple languages
    - [ ] We need to manage multiple installation for multiple models
- [ ] Report the Elasticsearch indexes creation sources
- [ ] Store dataset info, both _subreddit-dl_ and _entities_extraction.py_


## Links

- Python Elasticsearch `search` [API](https://elasticsearch-py.readthedocs.io/en/v7.11.0/api.html#elasticsearch.Elasticsearch.search)
- Pandas I/O formats comparison [website](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)
