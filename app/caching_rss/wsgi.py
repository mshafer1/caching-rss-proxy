import caching_rss
import logging

app = caching_rss.APP

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
