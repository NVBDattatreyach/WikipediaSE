# WikipediaSE
- link to dump `https://dumps.wikimedia.org/enwiki/20210720/enwiki-20210720-pages-articles-multistream.xml.bz2`
- After extracting the data size is around 85 GB at the time of implementation
### Run
- indexing : python3 parse.py
- searching: python3 search.py
### Details
- `parse.py` parses the dump file and created inverted index
- Inverted index is a list of posting lists
- Resulting index size 11 GB
- Implemented Ranked retrieval using tf-idf. documents with similar title as given query are given importance.
- Support for field queries.
