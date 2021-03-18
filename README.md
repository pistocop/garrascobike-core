# garrascobike-core

> Core of the Garrascobike recommendation system

## Entities extraction

- Store the entities in `parquet` for better compatibility with future
  uses [source](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)

# 💤 TODO

- [ ] Code refactory
- [ ] Use library for pandas CPU parallelism
- [ ] We should improve the text parsing?
    - Manage both parsing and entities extraction in one script could be a risk
- [ ] How manage the connection between models and requirements.txt?
- [ ] Support multiple languages
    - [ ] We need to manage multiple installation for multiple models
- [ x ] Log if GPU is attached
- [ ] Log running stats

# Links

- Garrascobike architecture [image](https://drive.google.com/file/d/16gCF_4xx8jsC3uX5PJDrvgndPnNJ6_3p/view?usp=sharing)
- Python Elasticsearch `search` [API](https://elasticsearch-py.readthedocs.io/en/v7.11.0/api.html#elasticsearch.Elasticsearch.search)
- Pandas I/O formats comparison [website](https://pandas-docs.github.io/pandas-docs-travis/user_guide/io.html#performance-considerations)
