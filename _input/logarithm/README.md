
Logarithm
=========

###### *Started March 15, 2005*

Logarithm is a (not so) simple perl-based IRC bot.  It was originally
written as the logging bot for a single small channel and has since
grown into a fully-featured bot with extensible commands and plugins.
It's primary function is to log the channel activity to text files, which can
be accessed via the web.  It also has some advanced features such as a
polling/voting system, a trivia game and an image cache which keeps a backup
of all image links posted.  Logarithm also provides useful commands to users
of the channel, such as a calculator, decision maker and 8ball game.  It has
been in use since 2002.

Running
-------

```
tar -xvzf logarithm.tar.gz
cd logarithm
./logarithm start
```

Make sure to edit the files in etc/ with the required settings before running.  The most pertinent
settings are the bot's nick, the server to connect to, and the channels to join once connected.

Logarithm can also be started automatically by adding the following line to your user crontab:
```
*/5 * * * *     cd /home/logarithm && ./logarithm.chk
```

News
----

##### Version 0.9 Released!
*April 24, 2010*
It's... been a lot longer than I thought it had been.  I can't exactly remember everything that's changed since the
last release but it has been a fair bit.  The git logs should have a record of most of it.  The plugins system is now
more robust and a number of bugs have been fixed.  Importantly, logarithm is now able to run as a daemon and has a
script to use for starting and stopping logarithm easily. Enjoy!
{: .entry }

##### Version 0.8 Released!
*February 04, 2007*
Version 0.8 has now been released.  The whole thing has been re-written in a more object-oriented style and the plugin
system has been made more robust and easy to use.  Logging has been moved entirely into a plugin and many of the
groups of commands have been made into plugins as well in order to make it easier to enable and disable them.  Enjoy!
{: .entry }

##### Version 0.7 Released!
*March 18, 2006*
Version 0.7 has now been released after a long time.  The directory structure has been reorganized and a plugin system
has been added.  Many minor changes have been made to the running copy as the issues arose.  Enjoy!
{: .entry }

