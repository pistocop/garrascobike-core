# garrascobike-core

> Core of the Garrascobike recommendation system

## Entities extraction

- Store the entities in `parquet` for better compatibility with future
  uses [source](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)

# 💤 TODO

- [ ] [!] Store dataset info, both _subreddit-dl_ and _entities_extraction.py_
- [ ] Can we speed up entities extractions with batch approach?
- [ ] Reorder /core/ scripts under different folders
- [ ] Info logging system: print the main 3 phases [init / processing / storing]
    - [ ] Log running stats
    - Not required: preprocessing is already really fast
- [ ] We should improve the text parsing?
    - [ ] Refactory: manage both parsing and entities extraction in one file script could be a risk
- [ ] How manage the connection between models and requirements.txt?
    - [ ] Support multiple languages
    - [ ] We need to manage multiple installation for multiple models
- [  ] Create Elasticsearch indexes creation
    - [  ] Use ES templates
- [  ] "03_matrix_builder.py" Fetch and store only entities required from elasticsearch
- [ x ] Use library for pandas CPU parallelism
- [ x ] Log if GPU is attached

# Links

- Garrascobike architecture [image](https://drive.google.com/file/d/16gCF_4xx8jsC3uX5PJDrvgndPnNJ6_3p/view?usp=sharing)
- Python Elasticsearch `search` [API](https://elasticsearch-py.readthedocs.io/en/v7.11.0/api.html#elasticsearch.Elasticsearch.search)
- Pandas I/O formats comparison [website](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)
