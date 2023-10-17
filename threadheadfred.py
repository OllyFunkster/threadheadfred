# Thread Head Fred - A Mastodon Bot
# Copyright (C) 2023 Funkster (funkster.org)
# 
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>

from mastodon import Mastodon;

# The maximum number of toots to try to fetch from the target user's feed at once. If the target is a rapid-fire poster, and we are only called infrequently,
# this will need to be increased in order to keep up. Your instance may cap this limit!
toot_fetch_limit = 4;

# Set up Mastodon.py for our bot's account
mastodon = Mastodon(
    access_token = 'token.secret',
    api_base_url = 'https://mas.to/'
);

verbose = False

# if we have no record of last-seen status ID, default to starting in the present (more or less)
lastseenstatusid = None;
# try to load the last seen status ID from the file
lastseenfile = open("lastseen.id", "r");
if (lastseenfile != None):
    lastseenstatusid = lastseenfile.read()
lastseenfile.close()

# look up the target account so as to be able to get its ID (from our server's perspective)
targetacct = None;
targetacctfile = open("target.account", "r");
if (targetacctfile != None):
    targetacct = targetacctfile.read()
targetacctfile.close()
sourceacctdict = mastodon.account_lookup(targetacct);
if (sourceacctdict == None):
    print(f"Error, no source account dict returned for account \"{targetacct}\"");
    exit(2);

print(f"Found account, username {sourceacctdict.acct}, id is {sourceacctdict.id}");

# get <toot_fetch_limit> toots for this account, starting at the loaded last seen status ID (if we are being run for the first time this will return the most recent <toot_fetch_limit> toots, that match the exclusions set.
status_dicts_list = mastodon.account_statuses(id = sourceacctdict.id, exclude_replies = True, exclude_reblogs = True, min_id = lastseenstatusid, limit = toot_fetch_limit)

# make sure that worked...
if (status_dicts_list == None):
    print("Error, no status_dicts_list");
    exit(4);

# count 'em
numtoots = len(status_dicts_list)
print(f"Got {numtoots} toots");

if (numtoots == 0):
    print("Nothing to do");
    exit(0);

# newest toots are first in the list, it seems, so start at the end and work backwards.
for i in range(numtoots - 1, -1, -1):
    # oddly, despite setting exclude_replies = True in the call to account_statuses, it does in fact return replies (but not all of them!)
    # so, check to see if in_reply_to_id is set, and if it is, skip over it.
    if (status_dicts_list[i].in_reply_to_id != None):
        print(f"Toot {i}, id {status_dicts_list[i].id}, created at {status_dicts_list[i].created_at}, is a reply to {status_dicts_list[i].in_reply_to_id}");
        if (verbose):
            print(f"\tcontent: {status_dicts_list[i].content}");
        continue;
    #if (status_dicts_list[i].pinned == True):
    #    print(f"Toot {i}, id {status_dicts_list[i].id} is a pinned toot");
    #    continue;
    print(f"Toot {i}, id {status_dicts_list[i].id}, created at {status_dicts_list[i].created_at}, will retoot.");
    if (verbose):
        print(f"\tcontent: {status_dicts_list[i].content}");
    # boost it!
    boost_dict = mastodon.status_reblog(id = status_dicts_list[i].id, visibility = "unlisted");
    if (boost_dict == None):
        print("Error, no boost_dict returned by status_reblog");
        exit(8);
    print(f"Boosted with boost ID {boost_dict.id}");

print(f"Last seen toot id is {status_dicts_list[0].id}")
# record the most recent seen status ID so that we can use that as a starting point next time we are run.
lastseenfile = open("lastseen.id", "w");
lastseenfile.write(f"{status_dicts_list[0].id}")
lastseenfile.close()

exit(0);