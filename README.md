# garrascobike-core

> Core of the Garrascobike recommendation system

## Intro

- Use this package to create the recommendation model used for the garrascobike project.<br>
- Folders structure:
    - `./garrascobike/` - folder there are all the python scripts that you should run consequentially.
    - `./notebooks/` - Jupyter notebooks used to explore the data, validate the hypothesis or test ML models

## Functionalities

### Entities extraction

- Store the entities in `parquet` for better compatibility with future uses
    - [source](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)

### Correlation extraction

- Optimize memory usage limiting the number of fields retrieved from elasticsearch with `_source`:
    - size products_list no _source: `289805320`
    - size products_list with _source: `29423384` (89% memory saved)
    - Memory size measured
      with [this approach](https://stackoverflow.com/questions/13530762/how-to-know-bytes-size-of-python-object-like-arrays-and-dictionaries-the-simp))

# 💤 TODO

- [ ] Can we speed up entities extractions with batch approach?
- [ ] How manage the connection between spacy models and requirements.txt?
    - [ ] Support multiple languages
    - [ ] We need to manage multiple installation for multiple models
- [  ] Report the Elasticsearch indexes creation sources
    - [  ] Use ES templates
- [ ] Store dataset info, both _subreddit-dl_ and _entities_extraction.py_
- [ x ] "03_matrix_builder.py" Fetch and store only entities required from elasticsearch
- [ x ] Reorder /core/ scripts under different folders
- [ x ] Use library for pandas CPU parallelism
- [ x ] Log if GPU is attached
- [ x ] We should improve the text parsing?
    - [ x] Refactory: manage both parsing and entities extraction in one file script could be a risk
- [ x ] Info logging system: print the main 3 phases [init / processing / storing]
    - [ x ] Log running stats
    - Not required: preprocessing is already really fast

# Links

- Garrascobike architecture [image](https://drive.google.com/file/d/16gCF_4xx8jsC3uX5PJDrvgndPnNJ6_3p/view?usp=sharing)
- Python Elasticsearch `search` [API](https://elasticsearch-py.readthedocs.io/en/v7.11.0/api.html#elasticsearch.Elasticsearch.search)
- Pandas I/O formats comparison [website](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)
