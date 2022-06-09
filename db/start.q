// Table Definitions

users: ( [] userid:`long$(); `$name:() )
users: `userid xkey users

guilds: ([] guildid:`long$(); `$name:() )
guilds: `guildid xkey guilds

channels: ([] channelid:`long$(); `$name:(); `long$guildid:() )
channels: `channelid xkey channels

userwords: ([] userid:`long$(); `$wordclass:(); words:(); wordcounts:() )
userwords: `userid`wordclass xkey userwords

messages: ([] messageid:`long$(); channelid:`long$(); userid:`long$(); timestamp:() )


// Load tables from disk (if persisted)

loadtables: {
    if[`users in key `:. ;    load `users]
    if[`guilds in key `:.;    load `guilds]
    if[`channels in key `:.;  load `channels]
    if[`userwords in key `:.; load `userwords]
    if[`messages in key `:.;  load `messages]
 }

savetables: {
    save `users;
    save `guilds;
    save `channels;
    save `userwords;
    save `messages;
 }


// Insert functions

adduser: {[userid;username]
    // Adds a user if they don't exist
    `users upsert (userid;`$username)
 }

addguild: {[guildid;name]
    // Adds a guild if it doesn't exist
    `guilds upsert (guildid;`$name)
 }

addchannel: {[channelid;name;guildid]
    // Adds a channel if it doesn't exist
    `channels upsert (channelid;`$name;guildid)
 }

addmessage: {[messageid;channelid;userid;timestamp]
    // NOTE: No checks on uniqueness as table is NOT keyed
    if[10h=type timestamp; timestamp: "Z"$timestamp];
    `messages insert (messageid;channelid;userid;timestamp)
 }


// Stats

adduserwords: {[userid;wordclass;words]
    words: `$ lower each words;

    data: userwords[(userid; `$wordclass)];
    uwords: data`words;
    uwc: data`wordcounts;

    newwords: words except uwords; // Newly seen
    exiswords: words inter uwords; // Seen before

    // Existing words
    wc: count each group uwords,exiswords;
    uwords: key wc;
    counts: (-1 + raze wc) + uwc;

    // New words
    wc: count each group newwords;
    nwords: key wc;
    ncounts: raze wc;

    // Combine
    wdata: uwords,nwords;
    wcounts: counts,ncounts;

    // Order by frequency
    wct: `counts xdesc ([] words: wdata; counts: wcounts);

    `userwords upsert (userid; `$wordclass; wct`words; wct`counts)
 }


// Timer

timerfunc: { savetables[] }

setuptimer: {
    .z.ts:: { timerfunc[]; };
    system "t 60000";
 }


// Queries

ignorewords: asc `$ " " vs "a as and be by do for i is in it n't of on 's the to to you"; // Adapted from https://en.wikipedia.org/wiki/Most_common_words_in_English

top_wordcounts_by_user: {
    (`wordcounts xdesc select userid, {sum x} each wordcounts from userwords where wordclass = `all) lj (users)
 }

total_word_count_of_user: {
    sum first exec wordcounts from userwords where userid = x
 }

top_words_of_user_ex: {[num_to_show; user_id]
    subl: {x sublist y}[num_to_show;];
    select wordclass, subl each words, subl each wordcounts from () xkey select from userwords where userid = user_id
 }

top_words_of_user: { top_words_of_user_ex[10] x }

get_userid_by_name: {
    if[10h=type x; x:`$x];
    first exec userid from users where name = x
 }


// Reports

user_stats: {[userid]
    total_words: total_word_count_of_user userid;
    top_words: top_words_of_user userid;
    top_verbs: first exec words from top_words where wordclass = `verb;
    top_nouns: first exec words from top_words where wordclass = `noun;
    top_adjs:  first exec words from top_words where wordclass = `adj;
    (`total`verbs`nouns`adjs)!(total_words; top_verbs; top_nouns; top_adjs)
 }

channel_stats: {[chid]
    total_messages: first exec count messageid from messages where channelid = chid;

    top_users: (10 sublist `messageid xdesc select count messageid by userid from messages where channelid = chid) lj (users);
    top_users: select messageid, name from top_users;

    (`total`topusers)!(total_messages; top_users)
 }

guild_stats: {[gid]
    guild_channels: exec channelid from channels where guildid = gid;
    guild_messages: select from messages where channelid in guild_channels;
    seen_users: exec distinct userid from guild_messages;

    channel_msgs: (`messages xdesc select messages: count messageid by channelid from guild_messages) lj (channels);
    channel_msgs: select messages, name from channel_msgs;

    user_msgs: (`messages xdesc select messages: count messageid by userid from guild_messages) lj (users);
    user_msgs: select messages, name from user_msgs;

    user_wordcounts: select wordcounts, name from top_wordcounts_by_user[] where userid in seen_users;

    (`$ " " vs "total_channels total_messages seen_users channel_messages user_messages user_word_counts")!(count guild_channels; count guild_messages; count seen_users; channel_msgs; 20 sublist user_msgs; 20 sublist user_wordcounts)
 }


// Init

loadtables[];
setuptimer[];
