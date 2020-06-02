# Stargazer Subscriber Backend

![Publish Docker](https://github.com/suisei-cn/stargazer-subscriber-backend/workflows/Publish%20Docker/badge.svg)

Stargazer Subscriber Backend is the python backend of [Stargazer Subscriber](https://github.com/suisei-cn/stargazer-subscriber).

It communicates with MongoDB and [PyStargazer](https://github.com/suisei-cn/pystargazer),
expose a set of endpoints to the management webui, and query user info for stargazer bots.

Generally speaking, all affairs related to users are handled by this backend.

## Related Projects

[PyStargazer](https://github.com/suisei-cn/pystargazer) - PyStargazer is a flexible vtuber tracker. It's now capable of monitoring Youtube live status, new tweets, and bilibili dynamic.

[Stargazer Subscriber](https://github.com/suisei-cn/stargazer-subscriber) - Stargazer Subscriber is the universal frontend of stargazer bots.

[Stargazer Telegram](https://github.com/suisei-cn/stargazer-telegram) ([@pystargazer_bot](https://t.me/pystargazer_bot)) - the telegram frontend for [PyStargazer](https://github.com/suisei-cn/stargazer-subscriber)
and Stargazer Subscriber Backend. 

[Stargazer QQ](https://github.com/suisei-cn/stargazer-qq) (2733773638) - The QQ frontend for [PyStargazer](https://github.com/suisei-cn/pystargazer)
and Stargazer Subscriber Backend. 

## Deploy

1. Make sure that [PyStargazer](https://github.com/suisei-cn/pystargazer) is running and its restful apis are accessible.
2. Start MongoDB.
3. Generate an `M2M_TOKEN` and a `SECRET_TOKEN`, and keep them safe.
4. Set the environment variables (`M2M_TOKEN`, `SECRET_TOKEN`, `UPSTREAM_URL`, `MONGODB`, `HOST`, `PORT`, `ALLOW_CORS`)
accordingly and start the container.

> Upstream URL: The base URL of restful apis.
>
> MongoDB URL: 
> mongodb://<db_url>:<db_port>/\<database>/\<collection>
>
> Note: '/' is not allowed in database & collection name


## License

This project is licensed under MIT License - see the [LICENSE.md](LICENSE.md) file for details.
