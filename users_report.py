import logging
import requests
import csv

from duckbot.kdb import make_connection

logging.basicConfig(level=logging.INFO)

from duckbot.config import TOKEN

KDB_HOST='192.168.1.245'
KDB_PORT=5000

GUILD_ID = "926349549734354954"  # Melbourne Meetup

MIN_MESSAGE_COUNT = 5 # Number of messages to consider as "active", since cutoff date
CUTOFF_DATE = '2023.01.01'


def get_members(guild_id) -> list[dict]:
    all_members = []

    per_page=1000
    after=0

    while True:
        print(f"{guild_id} after: {after}")
        url = f"https://discord.com/api/v10/guilds/{guild_id}/members"

        result = requests.get(
            url,
            params=dict(limit=per_page, after=after),
            headers={
                'Authorization': f'Bot {TOKEN}',
                'Content-Type': 'application/json',
            }, 
        )
        if result.ok:
            uu = result.json()
            uu.sort(key=lambda x: int(x['user']['id']))
            if uu:
                all_members.extend(uu)
                after=uu[-1]['user']['id']
            else:
                break
        else:
            break
    
    return all_members


# This is the ENTIRE member list of the server (guild)
all_members = get_members(guild_id=GUILD_ID)

# Connect to kdb+
c = make_connection(host=KDB_HOST, port=KDB_PORT)
c.open()

# Determine active users
report_query = """
{[guild_id;cutoff_date;min_message_count]
  cutoff_date: "Z"$cutoff_date;
  
  guild_channels: exec channelid from channels where guildid=guild_id;
  recent_messages: select from (select from messages where timestamp >= cutoff_date) where channelid in guild_channels;
  user_message_count: select count messageid by userid from recent_messages;
  active_users: exec userid from () xkey user_message_count where messageid >= min_message_count;

  active_users
}
""".strip()
active_users_ids = c(report_query, int(GUILD_ID), CUTOFF_DATE, MIN_MESSAGE_COUNT)  # Users which have messaged at least once, but have not messaged since the cutoff date

active_user_ids = set([str(x) for x in active_users_ids])
all_user_ids = set([u['user']['id'] for u in all_members])

inactive_user_ids = all_user_ids - active_user_ids

print("Total users:", len(all_user_ids))
print("Active users:", len(active_user_ids))
print("Inactive users:", len(inactive_user_ids))

with open('active_users.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', dialect='excel')
    writer.writerow(['uid', 'username'])

    for u in all_members:
        uid = u['user']['id']
        if uid in active_user_ids:
            name = u['user']['username'] + "#" + u['user']['discriminator']
            row = [uid, name]
            writer.writerow(row)


with open('inactive_users.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', dialect='excel')
    writer.writerow(['uid', 'username'])

    for u in all_members:
        uid = u['user']['id']
        if uid in inactive_user_ids:
            name = u['user']['username'] + "#" + u['user']['discriminator']
            row = [uid, name]
            writer.writerow(row)
