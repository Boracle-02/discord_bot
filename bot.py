import discord
import os
import random
import requests
import genshinstats as gs
from dotenv import load_dotenv
import json
from json.decoder import JSONDecodeError

client = discord.Client()

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]
starter_encouragements = [
  "Cheer up!",
  "Hang in there.",
  "You are a great person / bot!"
]
user_to_UID = {}

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
  with open("uid.json") as openfile:
 
    # Reading from json file
    # user_to_UID should now hold all previous UIDs
    # since it may be empty, do try/except
    try:
      user_to_UID = json.load(openfile)
    except JSONDecodeError:
        pass

@client.event
async def on_message(message):
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

          if message.author in user_to_UID:
            await message.channel.send("You already stored your UID, but I have overriden it")

          # now just add to dict and then add to the json file
          user_to_UID[str(message.author)] = int(uid)
          with open("uid.json", "w") as outfile:
            json.dump(user_to_UID, outfile)
          await message.channel.send("UID stored")
        else:
          await message.channel.send("Invalid UID. try again")
      else:
        await message.channel.send("Please format as $gstore {uid}")
        # 9 digits doesn't have leading 0s but first digit is 1-9 

    elif msg.startswith("$gdaily"):
      # claim daily achievement
      pass

    elif msg.startswith("$gnotes"):
      # get notes of user aka:
      # current resin, expeditions, daily commissions and similar.
      
      # check if user has uid stored
      if str(message.author) in user_to_UID:
        # what to do if uid meets the valid criteria but DNE?
        # can do a try/except block 
        notes = gs.get_notes(user_to_UID[str(message.author)])
        print(notes["resin"])
        print(notes["expeditions"])
        print(notes)
      else:
        await message.channel.send("Please store a UID first as $gstore {uid} before calling $gnotes")

      
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
