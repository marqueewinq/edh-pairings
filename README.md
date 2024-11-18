# edh-pairings

4-player tournament organizer. https://edh.marqueewinq.xyz/

## Stack

 - Django v2 + Django-Rest-Framework
 - jQuery + Bootstrap
 - Docker for local development
 - Heroku

## Development

 1. Check out the project
 2. Install pre-commit hooks:

```
pip install pre-commit
pre-commit install
```

 3. Run service: `docker-compose up --build`

Tests can be run in docker-compose by `docker-compose up test --abort-on-container-exit`
 or inside `web`/home/marqueewinq/code/synthesized/access-tmp container by `python3 manage.py test`.

## Deployment

Gitlab CI is configured to deploy to https://edh-pairings.herokuapp.com/ through Heroku.
