# Thread Head Fred
A Mastodon bot that will present a quieter view of your busy main account.

## Why?
Are you the kind of Mastodon user that posts long threads by replying to yourself? Do you wish that you could provide your audience with a way to follow you but only see the first toot in a thread in their timeline? Well, Thread Head Fred is for you. Just create a second account, give its credentials to this bot, and point the bot at your main account, and BOOM it will boost just your initial posts and not the replies!

Before anyone says it: no, setting your main account's replies to "unlisted" does not hide them from the timelines of your followers.

If Mastodon ever implements thread-collapsing, this bot will become obsolete and there will be much rejoicing.

## How to install
1. pip install Mastodon.py
2. create (or copy from example) config.local and populate it with sections for the bot/target account pairs that you have
3. create and fill in <sectionname>.token.secret  files with the access tokens for the bot accounts (see below for how to get these)
4. optionally, create and fill in <sectionname>.lastseen.id with a post ID from the past where you want the bot to start (if none is provided, it will start in the present and continue on from there)

## How to run
python threadheadfred.py

This will fetch up to <toot_fetch_limit> toots from immediately after the stored last-seen toot ID, and boost any that are not replies. Each time you run it it records the last seen ID so that next time it continues where it left off last time.

You will need to run this somewhat regularly (cron job / systemd timer unit / egg timer hooked up to your commodore 64?) on a computer that can access the internet and is at least running whenever you're likely to make posts.


# setting up a bot account
Find an instance that doesn't mind bots that do this kind of thing. This is left entirely up to you, if your bot account gets banned and deleted that's on you!

It doesn't have to be on the same instance as your main account.

Create an account, and when it's set up, create an application - go to preferences and click Development. Set an application name, which can be anything but you might as well call it Thread Head Fred. Hit save, then click on the name of the application.

Copy the access token, and paste it into token.secret - making sure that there are no extraeneous spaces at the start or end. Don't give this key to anyone else! Set good permissions on this file!

Optionally set the account's name and avatar etc. to bear some resemblance to your main account.

# references
https://shkspr.mobi/blog/2018/08/easy-guide-to-building-mastodon-bots/

https://pluralistic.net/2023/04/16/how-to-make-the-least-worst-mastodon-threads/
