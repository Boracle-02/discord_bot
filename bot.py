import discord
import os
import random
import requests
import genshinstats as gs
from dotenv import load_dotenv
import json
from json.decoder import JSONDecodeError

# need intents since repl.it uses a different version of discord.py
# intents = discord.Intents(messages=True, guilds=True, reactions = True)
# intents.reactions = True
# intents.members = True
# reactions, members, guilds, and messages should be the only intents I need but it causes error so all 
intents = discord.Intents.all()
client = discord.Client(intents=intents)

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]
starter_encouragements = [
  "Cheer up!",
  "Hang in there.",
  "You are a great person / bot!"
]
user_to_UID = {}

# send instructions on making your account public
def instructions_hoyo_public():
  embed = discord.Embed()
  embed.description = "[You can make your account public by going to the Hoyolab website](https://www.hoyolab.com/).\n"
  embed.description = embed.description + ("After making sure you are logged in...\n")
  embed.description = embed.description + ("Go to your profile by clicking on your profile icon near the top right...\n")
  embed.description = embed.description + ("Then scroll down until you see a tab labeled Genshin Impact on the right...\n")
  embed.description = embed.description + ("Click anywhere on it. This should take you to your Battle Chronicle where a lot of your player statistics are located...\n")
  embed.description = embed.description + ("Then click the settings icon near the top...\n")
  embed.description = embed.description + ("You should see three toggleable settings...\n")
  embed.description = embed.description + ("Toggle the last setting labeled:\n> Do you want to enable your \"Real-Time Notes\" to view your in-game data?\n")
  return embed

# checks if user is on a lower level of spiral abyss
def check_lower_level_spiral(curr_floor):
  for x in range(1, 10):
    # should go 1-9 inclusive
    if curr_floor.startswith(str(x)+"-"):
      return True
  return False

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)
  
def get_char():
  list_char = [
    'Albedo',
    'Aloy',
    'Arataki Itto',
    'Barbara',
    'Beidou',
    'Bennett',
    'Chongyun',
    'Diluc',
    'Diona',
    'Eula',
    'Fischl',
    'Ganyu',
    'Gorou',
    'Hu Tao'
  ]
  # hmm use genshinstats ;-;

@client.event
async def on_ready():
  global user_to_UID
  print('We have logged in as {0.user}'.format(client))
  # grab UID info from this or smth
  gs.set_cookie_auto()
  
  # error since vs was in personal_projects dir
  # not the folder where this is stored
  # cd genshinstat_figure_out
  with open("uid.json") as openfile:
 
    # Reading from json file
    # user_to_UID should now hold all previous UIDs
    # since it may be empty, do try/except
    try:
      user_to_UID = json.load(openfile)
    except JSONDecodeError:
        pass

  print("finished setting up")

@client.event
async def on_message(message):
  # print("message received")
  # note bot will pick up on its own messages!
  if message.author == client.user:
      # so we don't check the bot's own messages
      return
  msg = message.content
  if msg.startswith('$inspire'):

    quote = get_quote()
    await message.channel.send(quote)
    await message.channel.send(message.author)

      
  elif msg.startswith("$gstore"):
    if msg.startswith("$gstore "):
      uid = msg[msg.index(" ") + 1::]
      # await message.channel.send(uid)
      # check if uid is valid

      # remove any instance of leading space like: 
      # $gstore    1239    blah
      uid.strip()
      if ( uid.isdigit() and len(uid) == 9):
        # valid

        if str(message.author) in user_to_UID:
          await message.channel.send("You already stored your UID, but I have overriden it")

        # now just add to dict and then add to the json file
        user_to_UID[str(message.author)] = int(uid)
        with open("uid.json", "w") as outfile:
          json.dump(user_to_UID, outfile)
        await message.channel.send("UID stored")
      else:
        await message.channel.send("Invalid UID. try again")
    else:
      await message.channel.send("Please format as $gstore \{uid\}")
      await message.channel.send("Don't include the curly braces!")
      # 9 digits doesn't have leading 0s but first digit is 1-9 

  elif msg.startswith("$gdaily"):
    # claim daily achievement
    await message.channel.send("Please note that since I am only using the cookie data from Boracle, this will not work for you.")
    await message.channel.send("If you would like this to work for you, you need to provide private cookie data that may risk your account.")
    await message.channel.send("Therefore it is not worth the risk to have me automatically claim for you!")
    # can claim for others by passing in cookie param
    # claim_daily_rewards(cookie={'ltuid': ..., 'ltoken': ...})
    reward = gs.claim_daily_reward()
    if reward != None:
      await message.channel.send("Your claimed daily reward is {} {}.".format(reward["cnt"], reward["name"]))
    else:
      await message.channel.send("Could not claim a daily reward.")

  elif msg.startswith("$gnotes"):
    # get notes of user aka:
    # current resin, expeditions, daily commissions and similar.
    
    # check if user has uid stored
    if str(message.author) in user_to_UID:
      # what to do if uid meets the valid criteria but DNE?
      # can do a try/except block 
      # so error handle for wrong uids and not public for this
      try:
        notes = gs.get_notes(user_to_UID[str(message.author)])
        await message.channel.send("Hello {} you currently have {} resin.".format(str(message.author), notes["resin"] ))
        try:
          # until_resin_limit should be a string so cast to int
          # try/except in case of errors

          # this will be in seconds
          time_resin_max = int(notes["until_resin_limit"])
          # python 3+ so / gives float
          await message.channel.send("It will be maxed in {:0.2f} minutes or {:0.2f} hours".format(time_resin_max/60, time_resin_max/60/60 ))
        except:
          pass
        if ( notes["resin"] > 140 ):
          await message.channel.send("Your resin is almost full, I recommend using it soon")

        # now give information about commissions
        # error having everything on one line so use a string var to get them
        comms_message = "You also have {} commissions completed out of {}".format(notes["completed_commissions"], notes["total_commissions"] )
        
        if notes["claimed_commission_reward"]:
          comms_message += " and you have claimed your commission reward!"
          
        else:
          # make sure they have all their commissions done before telling them to claim
          # else tell them to complete then claim
          # can check by doing complete//total == 1 since if 3//4 -> 0 ( they are also ints )
          
          
          if notes["completed_commissions"] // notes["total_commissions"] == 1:
            comms_message += " and you have not claimed your commission reward!"
          else:
            if notes["total_commissions"] - notes["completed_commissions"] == 1:
              comms_message += " and once you finish your last commission, don't forget to claim your reward!"
            else:
              comms_message += " and once you finish your {} commissions, don't forget to claim your reward!".format(notes["total_commissions"] - notes["completed_commissions"])
        
        # also decreases the number of sends I perform ( by 1 but still )
        print(notes)
        await message.channel.send(comms_message)
      except (gs.AccountNotFound, gs.DataNotPublic) as error:

        # here errors will either be uid DNE/is not valid or their profile is not public
        # is not valid should rarely occur since I do UID checking
        # print(error)
        
        if error.__class__.__name__ == "AccountNotFound":
          # ok perfect can get name of error this way
          # could also write multiple excepts
          """
          various ways to get the name of exception:
            type(exception).__name__
            exception.__class__.__name__
            exception.__class__.__qualname__
          """
          await message.channel.send("Your uid is invalid, please try storing your uid again using the $gstore \{uid\} command.")
          await message.channel.send("Don't include the curly braces as well!")
        else:
          # that means the only other exception is the datanotpublic
          print("in other except")
          await message.channel.send("{}, the uid associated with your account is not public.".format(str(message.author)))
          # embed = discord.Embed()
          # embed.description = "[You can make your account public by going to the Hoyolab website](https://www.hoyolab.com/)."
          # await message.channel.send(embed = embed)
          # await message.channel.send("After making sure you are logged in...")
          # await message.channel.send("Go to your profile by clicking on your profile icon near the top right...")
          # await message.channel.send("Then scroll down until you see a tab labeled Genshin Impact on the right...")
          # await message.channel.send("Click anywhere on it. This should take you to your Battle Chronicle where a lot of your player statistics are located...")
          # await message.channel.send("Then click the settings icon near the top...")
          # await message.channel.send("You should see three toggleable settings...")
          # await message.channel.send("Toggle the last setting labeled:\n> Do you want to enable your \"Real-Time Notes\" to view your in-game data?")
          # await message.channel.send("Finally try using the $gnotes command again :)")

          # above code prints the first line as imbeded and the rest as normal comments
          # but after testing, I like the part where the entire text is part of the embeded text
          # keep for future reference
          # new method removes the use $gnotes line -> so add into new thing 
          embed = instructions_hoyo_public()
          embed.description = embed.description + "\nFinally try using the $gnotes command again :)"
          await message.channel.send( embed = embed )
          


        
    else:
      await message.channel.send("Please store a UID first as $gstore \{uid\} before calling $gnotes")
      await message.channel.send("Don't include the curly braces!")

  elif msg.startswith("$guid"):
    if str(message.author) in user_to_UID:
      # send the uid as a hidden message
      await message.channel.send("Your uid is: ||{}||".format(user_to_UID[str(message.author)]) )
    else:
      await message.channel.send("You have no uid stored here. You can store one by using the $gstore \{uid\} command.")
      await message.channel.send("Don't include the curly braces as well!")
  elif msg.startswith("gspiral"):
    try:
      if str(message.author) in user_to_UID:
        data = gs.get_spiral_abyss(user_to_UID[str(message.author)])
        msg = ""
        if data["total_battles"] < 6 and ( data["max_floor"].startswith("10") or  data["max_floor"].startswith("9")):
          # can just do same chamber over and over ;-; to bypass this
          # hence check for max 
          # lowest is 1-1 i believe for someone who has never atempted so check that the two char is less than 10
          
          msg = "I suggest completing more chambers for this spiral abyss cycle for me to have enough data."
          msg += "You have attempted {} chambers".format(data["total_battles"])
        elif check_lower_level_spiral(data["max_floor"]):
          msg = "Please reach the Abyssal Moon Spire ( floors 9-12 ) before retrieving spiral abyss information"
        else:
          msg = "For the {} season of spiral abyss spanning from {} to {}...\n".format(data["season"], data["season_start_time"], data["season_end_time"])
          msg += "Your highest floor is {} with the total starts received being {}.\n".format(data["max_floor"], data["total_stars"])
          

          if data["max_floor"] == "12-3" and data["total_stars"] >= 36:
            # maybe start floor 8 or smth so 9 + 36 total stars
            msg += "Congrats! You have been successful with this season's spiral abyss!"
          elif data["max_floor"] == "12-3" and data["total_stars"] != 36:
            msg += "I see you need some slight work to get all the stars.\nYou can always have a team designated to tackle a specific chamber to get the max stars possible"
          else:
            # hard to see if no stars floor 12 since you can intentionally get no stars previous floors but 9 star 12 and you can't tell from the provided data
            # hence the else will offer suggestions like builds, rotations, and team building
            # how to account for no attempts - look at total_battles and total_wins
            msg += "If you are having troubles, I would suggest you look at team suggestions and better rotations for each floor."
            msg += "\nArtifact luck is a whole other side part, but increasing talents and levels if you haven't is also beneficial."
          
          # complete floor 1-12 at once
          # 9 * 12 total stars
          if data["total_stars"] == 9 * 12:
            msg += "\nWOW! Finished all chambers in one go...\nImpressive!"
        await message.channel.send(msg)
      else:
        await message.channel.send("You do not have a uid on storage, therefore I cannot fetch your spiral abyss data.")
    except Exception as e :
      # should only happen on wrong uid and incorrect permissions
      # print(e)
      await message.channel.send("Failed to grab spiral abyss information. Check to make sure you uid is stored properly and that your account is public.")
      await message.channel.send(embed = instructions_hoyo_public())
  elif msg.startswith('$grecord'):
    # get data from temp.json
    # also see what the rest of the grecond says
    # new record
    # have dict for each user ( user to list of lists of records?)
    # boracle : [[raiden, pryo, burst, 10000]]
    pass
    
  if any(word in msg for word in sad_words):
    await message.channel.send(random.choice(starter_encouragements))



load_dotenv()
client.run(os.getenv("TOKEN"))
