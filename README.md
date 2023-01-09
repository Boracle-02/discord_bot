This is a discord bot that I made that used to run on Repl.it before I moved it to a local machine

[Here is a link to the official page for the genshinstats module](https://github.com/thesadru/genshinstats)

It allows users to grab information about their genshin account without needing to login along with performing many menial tasks automatically for you.

NOTE: The code provided in the bot.py file may not work for you as your browser's may not have the proper cookies that allow genshin's private api to validate you.

Try to avoid giving your cookies out as it can lead to others gaining access to your account.
Like the official documentation for genshinstats suggests, create an alternate account and use the cookies associated with that account if you were to make them public.

To allow the program to know which discord bot to perform these actions on, make sure you have a file just called .env

Then just do:
TOKEN = {your_token}
removing the curly braces after you put your unique bot identifier - aka the token 

If you are using repl.it, you cannot create a file that is called .env so you have to go to the secrets portion and input your token information there

NOTE: If you are using discord.py v1.5 make sure that the bot has all intent permissions activated
As of testing on 1/7/2023 Repl.it does not use a version of discord.py that utilizes that, therefore if you plan to only host on repl.it that does not need to be done.

The functionality for claiming your daily log in rewards depends on the cookie data from the host's browsers. Therefore, this bot functionality is limited to the host.
You can bypass this by setting cookie parameters, but that requires the other users' cookie data which may lead to accounts being hacked.

The gnotes function will make a lot of your information public and shared into the channel in which you invoke that command. 
