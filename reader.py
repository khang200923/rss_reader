import re
import sys
import time
from datetime import datetime
import webbrowser
import os
import feedparser
from bs4 import BeautifulSoup
from feedparser.util import FeedParserDict

print('RSS reader.')

def formatTime(dtime: datetime) -> str:
    return dtime.strftime("%Y-%m-%d %H:%M:%S")

def getPubTime(entry):
    try:
        return entry.published_parsed
    except AttributeError:
        return entry.updated_parsed

def countWords(soup: BeautifulSoup) -> int:
    text = soup.get_text()

    filteredText = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    splitText = re.split(r'\s+', filteredText)
    return len(splitText)

def rssFetch():
    with open('rssFeeds.txt', 'r', encoding='utf-8') as f:
        feedURLs, feedScores = zip(*(feed.split(' ') for feed in f.read().splitlines()))

    with open('styles.css', 'r', encoding='utf-8') as f:
        styles = f.read()

    feedScores = tuple(float(score) for score in feedScores)

    feeds: tuple[FeedParserDict] = tuple(feedparser.parse(feedURL) for feedURL in feedURLs)
    for feed in feeds:
        if 'bozo_exception' in feed:
            print(f"Error parsing RSS feed: {feed.bozo_exception}")
            input("Press Enter to exit. ")
            sys.exit(1)

    entries = tuple(
        (
            entry,
            feed.feed.title,
            feedScore / ((2 + (datetime.now() - datetime(*getPubTime(entry)[:6])).total_seconds() / 3600 / 24) ** 1.15)
        ) for feed, feedScore in zip(feeds, feedScores)
        for entry in feed.entries
    )
    entries = sorted(entries, key=lambda x: -x[2])

    maxEntryScore = entries[0][2]

    doc = BeautifulSoup(features="html.parser")

    head = doc.new_tag("head")
    doc.append(head)
    title = doc.new_tag("title")
    title.string = "RSS reader"
    head.append(title)
    body = doc.new_tag("body")
    doc.append(body)

    cssStyles = BeautifulSoup(f'<style>{styles}</style>', features="html.parser")
    head.append(cssStyles)

    topPar = doc.new_tag("h1")
    topPar.string = \
    f"""RSS reader output. Last updated {formatTime(datetime.now())}."""
    body.append(topPar)

    entriesDiv = doc.new_tag("div")
    body.append(entriesDiv)

    for i, (entry, feedTitle, score) in enumerate(entries):
        entryDiv = doc.new_tag("div")
        entryDiv.attrs['class'] = 'entry'
        entriesDiv.append(entryDiv)

        feedTitleTag = doc.new_tag("h2")
        feedTitleTag.string = f"{feedTitle} "
        entryDiv.append(feedTitleTag)

        entryTitleTag = doc.new_tag("a")
        entryTitleTag.string = entry.title
        entryTitleTag.attrs['class'] = 'inline entryTitle'
        entryTitleTag.attrs['href'] = entry.link
        feedTitleTag.append(entryTitleTag)

        entryDiv.append(doc.new_tag('br'))

        infoReport = doc.new_tag("p")
        infoReport.string = f"Entry score: {score / maxEntryScore * 100:.2f}%"
        wordCount = countWords(BeautifulSoup(entry.description, features="html.parser"))
        if wordCount >= 100:
            infoReport.string += f"; {wordCount} words"
        entryDiv.append(infoReport)

        pubAgoTag = doc.new_tag("p")
        pubAgoTag.string = \
            f"Published {(datetime.now() - datetime(*getPubTime(entry)[:6])).total_seconds() / 3600:.2f} hours ago" + \
            f" = {(datetime.now() - datetime(*getPubTime(entry)[:6])).total_seconds() / 3600 / 24:.2f} days ago"
        entryDiv.append(pubAgoTag)

        entryDiv.append(doc.new_tag('br'))

        toggleButton = doc.new_tag("button")
        toggleButton.string = 'Open/close'
        toggleButton.attrs['onclick'] = f'document.getElementById("entry_desc_div_{i}").classList.toggle("hidden")'
        entryDiv.append(toggleButton)

        entryDiv.append(doc.new_tag('br'))

        entryDescDiv = doc.new_tag('div')
        entryDescDiv.attrs['id'] = f'entry_desc_div_{i}'
        entryDescDiv.attrs['class'] = 'hidden container'
        entryDiv.append(entryDescDiv)

        entryDesc = BeautifulSoup(entry.description, features="html.parser")
        entryDescDiv.append(entryDesc)

        entryDiv.append(doc.new_tag('br'))

        entryLinkTag = doc.new_tag("a")
        entryLinkTag.attrs['href'] = entry.link
        entryLinkTag.string = entry.link
        entryDiv.append(entryLinkTag)

    for aTag in doc.find_all('a'):
        aTag.attrs['target'] = 'pageSim'

    iFrame = doc.new_tag('iframe')
    iFrame.attrs['name'] = 'pageSim'
    iFrame.attrs['id'] = 'pageSim'
    iFrame.attrs['class'] = 'hidden'
    body.append(iFrame)

    iFrameToggler = doc.new_tag('button')
    iFrameToggler.string = 'Toggle iframe visibility'
    iFrameToggler.attrs['id'] = 'iframe_toggler'
    iFrameToggler.attrs['onClick'] = 'document.getElementById("pageSim").classList.toggle("hidden")'
    body.append(iFrameToggler)

    try: open("output.html", "x")
    except Exception: pass

    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(str(doc))

    print(f'Successfully updated. {formatTime(datetime.now())}')

rssFetch()

file = f'file://{os.path.join(os.path.dirname(os.path.abspath(__file__)), "output.html")}'
webbrowser.open(file)

while 1:
    time.sleep(60 * 20)
    rssFetch()
