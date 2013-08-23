__author__ = 'gigimon'

import re
import logging

import tweepy
from tweepy.streaming import Stream, StreamListener

import config
from base import BasePlugin


LOG = logging.getLogger("irc_twi_stream")


class StreamerToIrc(StreamListener):
    def __init__(self, parent, *args, **kwargs):
        self._parent = parent
        super(StreamerToIrc, self).__init__(*args, **kwargs)

    def on_status(self, status):
        for chan in self.parent._channels:
            LOG.debug("Send message to %s %s" % (chan, status.text))
            tweet_text = self._parent.colorize("%s @%s" % (status.user.name, status.user.screen_name),
                                               status.text.replace('\n', ' '))
            self.parent._connection.privmsg(chan, tweet_text)
        return


class IRCPlugin(BasePlugin):
    name = "twitter_stream"
    enabled = True

    def _validate(self, event):
        return False

    def stop(self):
        if self._stream:
            self._stream.disconnect()

    def run(self):
        try:
            auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(config.TWITTER_ACCESS_KEY, config.TWITTER_ACCESS_SECRET)
            self._stream = Stream(auth, StreamerToIrc(self))
            LOG.info("Twitter stream successfully initializing")
        except Exception as e:
            LOG.error("Twitter stream authorization failed: %s" % e)
            return
        self._stream.filter(config.TWITTER_FOLLOW_IDS)
