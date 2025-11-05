# Social Graphs Project

This project focuses on analyzing social graphs, specifically related to books from Project Gutenberg. It includes functionalities for fetching, processing, and analyzing book data, as well as enriching it with additional information from the Open Library API.

## Project Structure

```
social-graphs
├── notebooks
│   └── Books1.ipynb          # Jupyter notebook for data fetching, processing, and analysis
├── src
│   ├── __init__.py           # Marks the directory as a Python package
│   ├── fetch_gutendex.py     # Functions for fetching book data from the Gutendex API
│   ├── download_texts.py      # Functions for downloading book text files
│   ├── ol_enrichment.py       # Functions for enriching book data from the Open Library API
│   ├── preprocessing.py       # Functions for preprocessing downloaded text data
│   ├── vectorize_and_knn.py   # Functions for vectorizing text data and performing k-NN analysis
│   └── graph_builder.py       # Functions for constructing graphs based on processed book data
├── data
│   ├── raw                   # Directory for raw data files
│   └── processed             # Directory for processed data files
├── tests
│   └── test_fetchers.py      # Unit tests for the fetch_gutendex.py module
├── requirements.txt          # Lists Python dependencies required for the project
├── pyproject.toml            # Configuration file for the project
├── .gitignore                # Specifies files and directories to ignore by Git
└── README.md                 # Documentation for the project
```

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd social-graphs
pip install -r requirements.txt
```

## Usage

1. **Data Fetching**: Use the `fetch_gutendex` function in `fetch_gutendex.py` to retrieve book data from the Gutendex API.
2. **Downloading Texts**: Utilize the `download_texts` function to download the text files of the books.
3. **Data Enrichment**: Enrich the book data using the functions in `ol_enrichment.py` to gather additional information from the Open Library API.
4. **Preprocessing**: Clean and normalize the downloaded text data with functions in `preprocessing.py`.
5. **Analysis**: Perform vectorization and k-NN analysis using `vectorize_and_knn.py` to find similar books.
6. **Graph Construction**: Build semantic and subject-based graphs with the functions in `graph_builder.py`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.