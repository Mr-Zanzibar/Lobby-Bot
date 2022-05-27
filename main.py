class color:
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

try:
    import fortnitepy
    from fortnitepy.errors import *
    import BenBotAsync
    import asyncio
    import time as delay
    import datetime
    import json
    import aiohttp
    import time
    import logging
    import functools
    import sys
    import os
    import random
    from colorama import init
    init(autoreset=True)
    from colorama import Fore, Back, Style
except ModuleNotFoundError:
    print(Fore.RED + f'[BOT] [N/A] [ERROR] Failed to import modules, click "install.bat".')
    exit()

print(f'  ')
print(color.BLUE + f' Needs a better logo')
print(f'  ')

def debugOn():
    logger = logging.getLogger('fortnitepy.xmpp')
    logger.setLevel(level=logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

def getTime():
    time = datetime.datetime.now().strftime('%H:%M:%S')
    return time

with open('config.json') as f:
    data = json.load(f)
    print(f' [BOT] [{getTime()}] Config loaded.')
    
debug = 'False'
if debug == 'True':
    print(f' [BOT] [{getTime()}] Debug ON.')
    debugOn()
else:
    print(f' [BOT] [{getTime()}] Debug OFF.')

def get_device_auth_details():
    if os.path.isfile('auths.json'):
        with open('auths.json', 'r') as fp:
            return json.load(fp)
    return {}

def store_device_auth_details(email, details):
    existing = get_device_auth_details()
    existing[email] = details

    with open('auths.json', 'w') as fp:
        json.dump(existing, fp)

device_auth_details = get_device_auth_details().get(data['email'], {})
client = fortnitepy.Client(
    auth=fortnitepy.AdvancedAuth(
        email=data['email'],
        password=data['password'],
        prompt_authorization_code=True,
        delete_existing_device_auths=True,
        **device_auth_details
    ),
    status=data['status'],
    platform=fortnitepy.Platform(data['platform'])
)

@client.event
async def event_device_auth_generate(details, email):
    store_device_auth_details(email, details)

@client.event
async def event_ready():
    print(Fore.GREEN + ' [BOT] [' + getTime() + ']  {0.user.display_name} ready.'.format(client))

    member = client.party.me

    await member.edit_and_keep(
        functools.partial(
            fortnitepy.ClientPartyMember.set_outfit,
            asset=data['cid']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_backpack,
            asset=data['bid']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_pickaxe,
            asset=data['pid']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_banner,
            icon=data['banner'],
            color=data['banner_color'],
            season_level=data['level']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_battlepass_info,
            has_purchased=True,
            level=data['bp_tier']
        )
    )

@client.event
async def event_party_invite(invite):
    if data['joinoninvite'].lower() == 'true':
        if invite.sender.display_name not in data['BlockList']:
            try:
                await invite.accept()
                print(Fore.GREEN + f' [BOT] [{getTime()}] Accepted party invite from {invite.sender.display_name}')
            except Exception as e:
                pass
        elif invite.sender.display_name in data['BlockList']:
            print(Fore.GREEN + f' [BOT] [{getTime()}] Never accepted party invite from' + Fore.RED + f' {invite.sender.display_name}')
    if data['joinoninvite'].lower() == 'false':
        if invite.sender.display_name in data['FullAccess']:
            await invite.accept()
            print(Fore.GREEN + f' [BOT] [{getTime()}] Accepted party invite from {invite.sender.display_name}')
        else:
            print(Fore.GREEN + f' [BOT] [{getTime()}] Never accepted party invite from {invite.sender.display_name}')
            await invite.sender.send(f"I can't join you right now.")

@client.event
async def event_friend_request(request):
    if data['friendaccept'].lower() == 'true':
        if request.display_name not in data['BlockList']:
            try:
                await request.accept()
                print(f" [BOT] [{getTime()}] Accepted friend request from: {request.display_name}")
            except Exception as e:
                pass
        elif request.display_name in data['BlockList']:
            print(f" [BOT] [{getTime()}] Never Accepted friend reqest from: " + Fore.RED + f"{request.display_name}")
    if data['friendaccept'].lower() == 'false':
        if request.display_name in data['FullAccess']:
            try:
                await request.accept()
                print(f" [BOT] [{getTime()}] Accepted friend request from: {request.display_name}")
            except Exception as e:
                pass
        else:
            print(f" [BOT] [{getTime()}] Never accepted friend request from: {request.display_name}")

@client.event
async def event_party_member_join(member):
    if client.user.display_name != member.display_name:
        print(f" [BOT] [{getTime()}] {member.display_name} joined the lobby.")

@client.event
async def event_friend_message(message):
    args = message.content.split()
    split = args[1:]
    joinedArguments = " ".join(split)
    print(' [BOT] [' + getTime() + '] {0.author.display_name}: {0.content}'.format(message))

    if "!skin" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=joinedArguments,
                    backendType="AthenaCharacter"
                )
                await client.party.me.set_outfit(asset=cosmetic.id)
                await message.reply('Skin set to ' + f'{cosmetic.name}')
            except BenBotAsync.exceptions.NotFound:
                await message.reply(f'Could not find a skin named: {joinedArguments}')
                
        
    if "!backpack" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            if len(args) == 1:
                await client.party.me.set_backpack(asset='none')
                await message.reply('Backpack set to None')
            else:
                try:
                    cosmetic = await BenBotAsync.get_cosmetic(
                        lang="en",
                        searchLang="en",
                        matchMethod="contains",
                        name=joinedArguments,
                        backendType="AthenaBackpack"
                    )
                    await client.party.me.set_backpack(asset=cosmetic.id)
                    await message.reply('Backpack set to ' + f'{cosmetic.name}')
                except BenBotAsync.exceptions.NotFound:
                    await message.reply(f'Could not find a backpack named: {joinedArguments}')

    if "!random" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            if len(args) == 1:
                skins = await BenBotAsync.get_cosmetics(
                    lang="en",
                    searchLang="en",
                    backendType="AthenaCharacter"
                )
                skin = random.choice(skins)

                backpacks = await BenBotAsync.get_cosmetics(
                    lang="en",
                    searchLang="en",
                    backendType="AthenaBackpack"
                )
                backpack = random.choice(backpacks)

                pickaxes = await BenBotAsync.get_cosmetics(
                    lang="en",
                    searchLang="en",
                    backendType="AthenaPickaxe"
                )
                pickaxe = random.choice(pickaxes)

                await client.party.me.set_outfit(
                    asset=skin.id
                )

                await client.party.me.set_backpack(
                    asset=backpack.id
                )

                await client.party.me.set_pickaxe(
                    asset=pickaxe.id
                )

                await message.reply(f'Loadout set to: {skin.name}, {backpack.name}, {pickaxe.name}')
            if len(args) == 2:
                if args[1].lower() == 'skin':
                    skins = await BenBotAsync.get_cosmetics(
                    lang="en",
                    searchLang="en",
                    backendType="AthenaCharacter"
                    )
                    skin = random.choice(skins)

                    await client.party.me.set_outfit(
                        asset=skin.id
                    )

                    await message.reply(f"Skin set to: {skin.name}")

                if args[1].lower() == 'backpack':
                    backpacks = await BenBotAsync.get_cosmetics(
                    lang="en",
                    searchLang="en",
                    backendType="AthenaBackpack"
                    )
                    backpack = random.choice(backpacks)

                    await client.party.me.set_backpack(
                        asset=backpack.id
                    )

                    await message.reply(f"Backpack set to: {backpack.name}")

                if args[1].lower() == 'emote':
                    emotes = await BenBotAsync.get_cosmetics(
                    lang="en",
                    searchLang="en",
                    backendType="AthenaDance"
                    )
                    emote = random.choice(emotes)

                    await client.party.me.set_emote(
                        asset=emote.id
                    )

                    await message.reply(f"Emote set to: {emote.name}")

                if args[1].lower() == 'pickaxe':
                    pickaxes = await BenBotAsync.get_cosmetics(
                    lang="en",
                    searchLang="en",
                    backendType="AthenaPickaxe"
                    )
                    pickaxe = random.choice(pickaxes)

                    await client.party.me.set_pickaxe(
                        asset=pickaxe.id
                    )

                    await message.reply(f"Pickaxe set to: {pickaxe.name}")
					
    if "!ready" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            await client.party.me.set_ready(fortnitepy.ReadyState.READY)
            await message.reply('Now Ready!')

    if ("!unready" in args[0].lower()) or ("!sitin" in args[0].lower()):
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            await client.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
            await message.reply('Now Unready!')

    if "!sitout" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
            await message.reply('Now Sitting Out!')
    
    if "!bp" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            await client.party.me.set_battlepass_info(has_purchased=True, level=args[1], self_boost_xp='0', friend_boost_xp='0')
    
    if "!level" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            await client.party.me.set_banner(icon=client.party.me.banner[0], color=client.party.me.banner[1], season_level=args[1])

    if "!leave" in args[0].lower():
        if message.author.display_name in data['FullAccess']:
            await client.party.me.set_emote('EID_Snap')
            delay.sleep(2)
            await client.party.me.leave()
            await message.reply('Bye!')
            print(Fore.GREEN + f' [BOT] [{getTime()}] Left the party.')
        else:
            if message.author.display_name not in data['FullAccess']:
                await message.reply(f"You don't have access to this command.")

    if "!point" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            await client.party.me.clear_emote()
            if len(args) == 1:
                await client.party.me.set_emote(asset="/Game/Athena/Items/Cosmetics/Dances/EID_IceKing.EID_IceKing")
                await message.reply('Doing emote: Point It Out')
            else:
                if len(args) == 2:
                    if args[1].lower() == 'random':
                        pickaxes = await BenBotAsync.get_cosmetics(
                        lang="en",
                        searchLang="en",
                        backendType="AthenaPickaxe"
                        )
                        pickaxe = random.choice(pickaxes)

                        await client.party.me.set_pickaxe(
                            asset=pickaxe.id
                        )

                        await client.party.me.clear_emote()
                        await client.party.me.set_emote(asset="/Game/Athena/Items/Cosmetics/Dances/EID_IceKing.EID_IceKing")

                        await message.reply(f"Pointing with: {pickaxe.name}")
                    else:
                        try:
                            cosmetic = await BenBotAsync.get_cosmetic(
                                lang="en",
                                searchLang="en",
                                matchMethod="contains",
                                name=joinedArguments,
                                backendType="AthenaPickaxe"
                            )
                            await client.party.me.set_pickaxe(asset=cosmetic.id)
                            await client.party.me.clear_emote()
                            await client.party.me.set_emote(asset="/Game/Athena/Items/Cosmetics/Dances/EID_IceKing.EID_IceKing")
                            await message.reply('Pointing with: ' + f'{cosmetic.name}')
                        except BenBotAsync.exceptions.NotFound:
                            await message.reply(f'Could not find a pickaxe named: {joinedArguments}')

    if "!banner" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command.")
        else:
            if len(args) == 1:
                await message.reply('You need to specify which banner, color & level you want to set the banner as.')
            if len(args) == 2:
                await client.party.me.set_banner(icon=args[1], color=data['banner_color'], season_level=data['level'])
            if len(args) == 3:
                await client.party.me.set_banner(icon=args[1], color=args[2], season_level=data['level'])
            if len(args) == 4:
                await client.party.me.set_banner(icon=args[1], color=args[2], season_level=args[3])

            await message.reply(f'Banner set to; {args[1]} {args[2]} {args[3]}')
            print(f" [BOT] [{getTime()}] Banner set to; {args[1]} {args[2]} {args[3]}")

    if "!send" in args[0].lower():
        if message.author.display_name in data['FullAccess']:
            await client.party.send(joinedArguments)
            print(f' [BOT] [{getTime()}] ' + color.GREEN + 'Sent Message:' + color.END + f' {joinedArguments}')
        else:
            if message.author.display_name not in data['FullAccess']:
                await message.reply(f"You don't have access to this command.")

    if "!join" in args[0] and message.author.display_name in data['FullAccess']:
        if len(args) != 1:
            user = await client.fetch_profile(joinedArguments)
            friend = client.get_friend(user.id)
        if len(args) == 1:
            user = await client.fetch_profile(message.author.id, cache=False, raw=False)
            friend = client.get_friend(user.id)
        if friend is None:
            await message.reply(f"Unable to invite that user, are you sure the bot has them added?")
            print(Fore.RED + f" [BOT] [{getTime()}] [ERROR] Unable to join user: {joinedArguments}, are you sure the bot has them added?" + Fore.WHITE)
        if message.author.display_name not in data['FullAccess']:
            await message.reply(f"You don't have access to this command.")
        else:
            try:
                await friend.join_party()
                await message.reply(f"Joining {friend.display_name}'s party.")
            except Exception as e:
                await message.reply(f"Can not join user's party.")

    if "!admin" in args[0].lower():
        if message.author.display_name in data['FullAccess']:
            if len(args) == 1:
                await message.reply('Please specify if you want to add or remove a user from the admin list')
                print(f' [BOT] [{getTime()}] Please specify if you want to add or remove a user from the admin list, using ' + color.GREEN + '!admin add ' + color.END + 'or ' + color.GREEN + '!admin remove' + color.END)
            if len(args) == 2:
                if args[1].lower() == 'add':
                    await message.reply('You are already an admin')
                elif args[1].lower() == 'remove':
                    await message.reply('Are you sure you want to be removed as an admin?')
                    res = await client.wait_for('friend_message')
                    content = res.content.lower()
                    user = await client.fetch_profile(message.author.id, cache=False, raw=False)
                    if content == "yes":
                        data['FullAccess'].remove(user.display_name)
                        with open('config.json', 'w') as f:
                            json.dump(data, f, indent=4)
                            print(f" [BOT] [{getTime()}] Removed " + color.GREEN + f"{user.display_name}" + color.END + " as an admin")
                            await message.reply(f"You were removed as an admin.")
                    elif content == "no":
                            await message.reply(f"You were kept as an admin.")
                    else:
                        await message.reply(f'Not a correct response, try "yes" or "no"')
                else:
                    await message.reply('Invalid usage, try !admin add <username> or !admin remove <username>')
            if len(args) >= 3:
                joinedArgumentsAdmin = " ".join(args[2:])
                user = await client.fetch_profile(joinedArgumentsAdmin)
                try:
                    if args[1].lower() == 'add':
                        if user.display_name not in data['FullAccess']:
                            data['FullAccess'].append(f"{user.display_name}")
                            with open('config.json', 'w') as f:
                                json.dump(data, f, indent=4)
                                print(f" [BOT] [{getTime()}] Added " + color.GREEN + f"{user.display_name}" + color.END + " as an admin")
                                await message.reply(f"Added {user.display_name} as an admin.")
                        elif user.display_name in data['FullAccess']:               
                            print(f" [BOT] [{getTime()}]" + color.GREEN + f" {user.display_name}" + color.END + " is already an admin")
                            await message.reply(f"{user.display_name} is already an admin.")
                    elif args[1].lower() == 'remove':
                        if user.display_name in data['FullAccess']:
                            data['FullAccess'].remove(user.display_name)
                            with open('config.json', 'w') as f:
                                json.dump(data, f, indent=4)
                                print(f" [BOT] [{getTime()}] Removed " + color.GREEN + f"{user.display_name}" + color.END + " as an admin")
                                await message.reply(f"Removed {user.display_name} as an admin.")
                        elif user.display_name not in data['FullAccess']:
                            print(f" [BOT] [{getTime()}]" + color.GREEN + f" {user.display_name}" + color.END + " is not an admin")
                            await message.reply(f"{user.display_name} is not an admin.")
                except AttributeError:
                    pass
                    print(f" [BOT] [{getTime()}] Can't find user: " + color.GREEN + f"{joinedArgumentsAdmin}" + color.END)
                    await message.reply(f"I couldn't find an Epic account with the name: {joinedArgumentsAdmin}.")
        if message.author.display_name not in data['FullAccess']:
            if len(args) >= 3 and args[1].lower() == 'add':
                await message.reply(f"Password?")
                res = await client.wait_for('friend_message')
                content = res.content.lower()
                joinedArgumentsAdmin = " ".join(args[2:])
                user = await client.fetch_profile(joinedArgumentsAdmin)
                if content in data['AdminPassword']:
                    if user.display_name not in data['FullAccess']:
                        data['FullAccess'].append(f"{user.display_name}")
                        with open('config.json', 'w') as f:
                            json.dump(data, f, indent=4)
                            await message.reply(f"Correct. Added {user.display_name} as an admin.")
                            print(f" [BOT] [{getTime()}] Added " + color.GREEN + f"{user.display_name}" + color.END + " as an admin")
                    elif user.display_name in data['FullAccess']:
                        print(f" [BOT] [{getTime()}]" + color.GREEN + f" {user.display_name}" + color.END + " is already an admin")
                        await message.reply(f"{user.display_name} is already an admin.")
                else:
                    await message.reply(f"Incorrect Password")
            elif len(args) == 2 and args[1].lower() == 'add':
                await message.reply('Password?')
                res = await client.wait_for('friend_message')
                content = res.content.lower()
                user = await client.fetch_profile(message.author.id, cache=False, raw=False)
                if content in data['AdminPassword']:
                    data['FullAccess'].append(f"{user.display_name}")
                    with open('config.json', 'w') as f:
                        json.dump(data, f, indent=4)
                        await message.reply(f"Correct! You were added as an admin.")
                        print(f" [BOT] [{getTime()}] Added " + color.GREEN + f"{user.display_name}" + color.END + " as an admin")
                else:
                    await message.reply(f"Incorrect Password")
            else:
                await message.reply(f"You don't have access to this command.")


try:
    client.run()
except fortnitepy.AuthException as e:
    print(Fore.RED + f" [BOT] [{getTime()}] [ERROR] {e}")
