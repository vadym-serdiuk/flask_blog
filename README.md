## Starting

1. Copy and rename the `.env.example` file to `.env`
2. In this file set the http port to listen in `APP_PORT` (default: 5010) 
3. Start database service with `docker-compose up -d database`
4. Build the `app` image with `docker-compose build`
5. Create tables with `docker-compose run app bash -c "python3 -m lib.db.cli create_tables"`
6. Run the application with `docker-compose up app`
7. Use the service with http://localhost:5010

## Running tests

`docker-compose run app bash -c "python3 -m pytest"`

## Endpoints

- /posts
- /posts/:post_slug
- /posts/:post_slug/comments
- /posts/:post_slug/comments/:slug
- /users
- /users/:username
- /auth/login
- /auth/logout

## Authentication

The authentication is based on a session. Session contains the all info about user, so it's not necessary to go to database every time.
Actually in microservice architecture it's better to use external authentication service that is called from the edge (API Gateway, for instance), so the service receives the JWT token in a header. It should provide a JWT token with all the information about user 


## API Documentation

; is out of scope
