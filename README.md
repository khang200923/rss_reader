# rss_reader
Reader for your favorite RSS feeds

How to use this repo:
- Fill in the feeds (URL) and their associated score in the rssFeeds.txt file (higher score = more priority). For example:
  ```
  https://example.org/rss1.xml 2
  https://example.org/rss2.xml 3
  https://example.org/rss3.xml 10
  ```
- Run reader.py.
- You're done - the program creates output.html and opens it in the browser.
  The program also updates output.html every 20 minutes.
