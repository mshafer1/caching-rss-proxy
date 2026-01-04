# caching-rss

A lightweight docker container that provides:
- cached queries to an RSS feed (only permitted URI's per server to prevent abuse)
  - Data is cached long term (so where an RSS feed likely shows most recent 10 or 15, over time, this server will contain a longer history)
  - A max size may be specified to set a limit
- responses in xml or json
- upstream queries are throttled to 1/hr (to prevent overloading source and to be a good net citizen)
