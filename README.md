# LinguaScreen API

API backend for LinguaScreen app written in Python using FastAPI.

LinguaScreen is a language learning app which allows you to learn from reading books in languages you want to learn. It provides an overlay which provides translation and AI powered explanation for why a sentence is structured in a way or why a word is used in a context.

## Running

Install dependencies, we recommend using [uv](https://github.com/astral-sh/uv):

```sh
uv venv && uv sync
```

Ensure `.env` file is populated, example is in [.env.example](https://github.com/MMADUs/linguascreen-api/blob/main/.env.example)

Run the server:

```sh
uv run main.py
```

## OpenAPI Docs

FastAPI auto generates OpenAPI docs. When the server is running it can be found at `/docs` path.


## Contributors

- @MMADUs
- @KrisNathan (Kristopher N.)
