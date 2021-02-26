import discord
import json
import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def get_table():
    data_file = open("table.json", "r", encoding="utf-8")
    table = json.load(data_file)
    data_file.close()
    return table

def write_table(table):
    with open("table.json", "w") as f:
        json.dump(table, f, ensure_ascii=False, indent=4)

def print_help():
    return """```\n$help - shows this\n\n$show - shows the leaderboard\n\n$top [positive_integer : x] - shows top 'x' leading members\ne.g: $top 3 - shows top 3\n\n$update [member_username_with_discriminator] [points_to_be_added] - adds the given points to the member\ne.g: $update trieumfer#5579 10\n\n$refresh - refreshes the leaderboard\n\n$list - lists the members with all ping and puzzle crackers roles\n\n$dump - dumps JSON data```"""

@client.event
async def on_message(message):
    # add admin id if needed 
    # only me and Ransom ofc :couplehug:
    admin = {650774885316165662, 319618402903916544}
    # TODO : change role ID
    roles_list = {807016594352898098, 807286699101126686}

    # TODO : Handling members based on their unique ID
    if message.content.startswith('$list'):
        lst = message.content.rsplit(' ')
        res = "List:\n"
        if len(lst) != 1 or lst[0] != "$list":
            res = print_help()
        else:
            for guild in client.guilds:
                for member in guild.members:
                    for role in member.roles: 
                        # TODO: change role id
                        if(role.id in roles_list):
                            res += member.name + "\n"
        
        await message.channel.send(res)
        return
   
    # only allow admin to query 'update' 
    if message.content.startswith('$update'):
        lst = message.content.rsplit(' ')
        res = ""
        if len(lst) != 3 or lst[0] != "$update" or RepresentsInt(lst[2]) == False:
            res = print_help()
        else: 
            if message.author.id not in admin:
                await message.channel.send("Trying to cheat, uh? :smirk:")
                return
            lst = message.content.rsplit(' ')
            name = ""
            for i in range(1, len(lst) - 1):
                name += lst[i]
                if(i != len(lst) - 2):
                    name += ' '
            discriminator = name[-4:]
            name = name[:-5]
            points = lst[len(lst) - 1]
            ok = 0
            member_id = ""
            for guild in client.guilds:
                for member in guild.members:
                    if(member.name == name and str(member.discriminator) == discriminator):
                        member_id = str(member.id)
                        ok = 1
        
            if (ok == 0): 
                await message.channel.send("Member not in server")
                return

            table = get_table()

            if member_id not in table :
                table[member_id] = 0
        
            table[member_id] = table[member_id] + int(points)

            write_table(table)
            res = "Successfully updated! :sunglasses:"

        await message.channel.send(res)
        return

    if message.content.startswith('$show'):
        lst = message.content.rsplit(' ')
        res = ""
        if len(lst) != 1 or lst[0] != "$show":
            res = print_help()
        else: 
            table = get_table()
            # sort table
            table = sorted(table.items(), key=lambda item: item[1], reverse=True)
            table = dict(table)

            counter = 1
            res = "```"
            for member_id in table :
                name = ""
                for guild in client.guilds:
                    for member in guild.members:
                        if(str(member.id) == member_id):
                            name = member.name
                res += str(counter) + ". " + name + " :" + str(table[member_id]) + "\n"
                counter += 1
            res += "```"
        
        await message.channel.send(res)
        return 
    
    if message.content.startswith('$refresh'):
        lst = message.content.rsplit(' ')
        res = ""
        if len(lst) != 1 or lst[0] != "$refresh":
            res = print_help()
        else: 
            table = get_table()
            for guild in client.guilds:
                for member in guild.members:
                    for role in member.roles: 
                        if(role.id in roles_list):
                            if str(member.id) not in table:
                                table[member.id] = 0
        
            write_table(table)
            res = "Refreshed!"

        await message.channel.send(res)
        return 

    if message.content.startswith('$help'):
        await message.channel.send(print_help()) 
        return 

    if message.content.startswith('$dump'):
        lst = message.content.rsplit(' ')
        res = ""
        if len(lst) != 1 or lst[0] != "$dump":
            res = print_help()
            if message.author.id != 650774885316165662:
                res = "Dev/Admin only!"
        else:
            table = get_table()
            res = table
        
        await message.channel.send(res)
        return    
    
    if message.content.startswith('$top'):
        table = get_table()

        lst = message.content.rsplit(' ')
        res = ""
        if len(lst) != 2:
            res = "Invalid number of arguments!"
        elif lst[0] != "$top":
            res = print_help()
        else:
            if RepresentsInt(lst[1]): 
                lim = int(lst[1])
                if lim > 0:
                    lim = min(lim, len(table))

                    table = sorted(table.items(), key=lambda item: item[1], reverse=True)
                    table = dict(table)

                    counter = 1
                    res = "```"
                    for member_id in table :
                        if counter > lim:
                            break
                        name = ""
                        for guild in client.guilds:
                            for member in guild.members:
                                if(str(member.id) == member_id):
                                    name = member.name

                        res += str(counter) + ". " + name + " :" + str(table[member_id]) + "\n"
                        counter += 1
                    res += "```"
                else: 
                    res = "Invalid argument! Enter a positive number"
            else:
                res = print_help()
        
        await message.channel.send(res)
        return
    
    if message.content.startswith('$remove'):
        res = ""
        if message.author.id not in admin:
            res = "Dev/Admin only!"
        else:
            lst = message.content.rsplit(' ')
            name = lst[1]
            discriminator = name[-4:]
            name = name[:-5]
            ok = 0
            member_id = ""
            for guild in client.guilds:
                for member in guild.members:
                    if(member.name == name and str(member.discriminator) == discriminator):
                        member_id = str(member.id)
                        ok = 1
        
            if (ok == 0): 
                await message.channel.send("Member not in server")
                return
            table = get_table()
            del table[member_id]
            res = "Successfully deleted!"

            write_table(table)
        await message.channel.send(res)
        return
        
client.run(os.environ.get('LEADERBOARD_BOT_TOKEN'))