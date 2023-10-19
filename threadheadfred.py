# Thread Head Fred - A Mastodon Bot
# Copyright (C) 2023 Funkster (funkster.org)
# 
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>

import configparser;
from mastodon import Mastodon;

dryrun = False;
verbose = False;
default_toot_fetch_limit = 4;
max_toot_fetch_limit = 1000;


config = configparser.ConfigParser();
configret = config.read('config.local');

if (configret == []):
    print("Error, no config");
    exit(128);
if (len(config.sections()) == 0):
    print("Error, no sections in config");
    exit(16);
print(f"Loaded config");

for configsection in config.sections():
    print(f"Processing config section \"{configsection}\"");
    thisconfig = config[configsection];
    # The maximum number of toots to try to fetch from the target user's feed at once. If the target is a rapid-fire poster, and we are only called infrequently,
    # this will need to be increased in order to keep up. Your instance may cap this limit!
    if (thisconfig['toot_fetch_limit'] == None):
        toot_fetch_limit = default_toot_fetch_limit;
    else:
        toot_fetch_limit = int(thisconfig['toot_fetch_limit']);
    
    if (toot_fetch_limit > max_toot_fetch_limit):
        toot_fetch_limit = max_toot_fetch_limit;
        
    access_token_filename = configsection + ".token.secret";
    
    if ('access_token' in thisconfig):
        print(f"Overriding default filename for access token storage");
        access_token_filename = thisconfig['access_token'];
    
    if ('api_base_url' not in thisconfig):
        print(f"Error, missing config option \"api_base_url\" in config section \"{configsection}\"");
        exit(64);
        
    if ('target_account' not in thisconfig):
        print(f"Error, missing config option \"target_account\" in config section \"{configsection}\"");
        exit(256);
    
    # config is good enough, let's do this one...
    
    # Set up Mastodon.py for our bot's account
    mastodon = Mastodon(
        access_token = access_token_filename,
        api_base_url = thisconfig['api_base_url']
    );
    
    lastseenfilename = configsection + ".lastseen.id";
    
    # if we have no record of last-seen status ID, default to starting in the present (more or less)
    lastseenstatusid = None;
    # try to load the last seen status ID from the file
    lastseenfile = open(lastseenfilename, "r");
    if (lastseenfile != None):
        lastseenstatusid = lastseenfile.read()
    lastseenfile.close()

    # look up the target account so as to be able to get its ID (from our server's perspective)
    targetacct = thisconfig['target_account'];
    sourceacctdict = mastodon.account_lookup(targetacct);
    if (sourceacctdict == None):
        print(f"Error, no source account dict returned for account \"{targetacct}\"");
        exit(2);

    print(f"\tFound account, username {sourceacctdict.acct}, id is {sourceacctdict.id}");

    # get <toot_fetch_limit> toots for this account, starting at the loaded last seen status ID (if we are being run for the first time this will return the most recent <toot_fetch_limit> toots, that match the exclusions set.
    print(f"\tRequesting up to {toot_fetch_limit} toots starting after id \"{lastseenstatusid}\"");
    status_dicts_list = mastodon.account_statuses(id = sourceacctdict.id, exclude_replies = True, exclude_reblogs = True, min_id = lastseenstatusid, limit = toot_fetch_limit)

    # make sure that worked...
    if (status_dicts_list == None):
        print("Error, no status_dicts_list");
        exit(4);

    # count 'em
    numtoots = len(status_dicts_list)
    print(f"\tGot {numtoots} toots");

    if (numtoots == 0):
        print(f"\tNothing to do for config section \"{configsection}\"");
        continue;

    # newest toots are first in the list, it seems, so start at the end and work backwards.
    for i in range(numtoots - 1, -1, -1):
        # oddly, despite setting exclude_replies = True in the call to account_statuses, it does in fact return replies (but not all of them!)
        # so, check to see if in_reply_to_id is set, and if it is, skip over it.
        if (status_dicts_list[i].in_reply_to_id != None):
            print(f"\tToot {i}, id {status_dicts_list[i].id}, created at {status_dicts_list[i].created_at}, is a reply to {status_dicts_list[i].in_reply_to_id}");
            if (verbose):
                print(f"\t\tcontent: {status_dicts_list[i].content}");
            continue;
        #if (status_dicts_list[i].pinned == True):
        #    print(f"Toot {i}, id {status_dicts_list[i].id} is a pinned toot");
        #    continue;
        print(f"\tToot {i}, id {status_dicts_list[i].id}, created at {status_dicts_list[i].created_at}, will retoot.");
        if (verbose):
            print(f"\t\tcontent: {status_dicts_list[i].content}");
        if (dryrun == False):
            # boost it!
            boost_dict = mastodon.status_reblog(id = status_dicts_list[i].id, visibility = "unlisted");
            if (boost_dict == None):
                print("Error, no boost_dict returned by status_reblog");
                exit(8);
            print(f"\tBoosted with boost ID {boost_dict.id}");
        
    print(f"\tLast seen toot id is {status_dicts_list[0].id}")
    if (dryrun == False):
        # record the most recent seen status ID so that we can use that as a starting point next time we are run.
        lastseenfile = open(lastseenfilename, "w");
        lastseenfile.write(f"{status_dicts_list[0].id}")
        lastseenfile.close()
    

exit(0);