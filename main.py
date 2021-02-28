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

def get_table(json_file):
    data_file = open(json_file, "r", encoding="utf-8")
    table = json.load(data_file)
    data_file.close()
    return table

def write_table(json_file, json_data):
    with open(json_file, "w") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

def print_help():
    return """```\n$help - shows this\n\n$show - shows the leaderboard\n\n$top [positive_integer : x] - shows top 'x' leading members\ne.g: $top 3 - shows top 3\n\n$update [leaderboard_name] [member_id] [points_to_be_added] - adds the given points to the member\ne.g: $update [leaderboard_name] 812334480801923142 10\n\n$refresh - refreshes the leaderboard\n\n$list - lists the members with all ping and puzzle crackers roles\n\n$dump - dumps JSON data\n\n$create [leaderboard_name]: creates new leaderboard\n\n$show [leaderboard_name]: shows the leaderboard_name\n\n$delete [leaderboard_name]: deletes the leaderboard_name\n\n$ls: lists the set of leaderboards\n\nNote: If leaderboard_name is not given the main leaderboard gets modified by default.```"""

def is_json(filename):
    if filename[-5:] != ".json":
        return False
    return True

def is_exists_json(filename):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f == filename:
            return True
    return False

# WARNING: $remove and $delete are dangerous functions give permissions rightly
# the main leaderboard is table.json

@client.event
async def on_message(message):
    # add admin id if needed 
    # only trieumfer and Ransom 
    admin = {650774885316165662, 319618402903916544}
    # TODO : change role ID
    roles_list = {807016594352898098, 807286699101126686}

    # TODO : Handling members based on their unique ID
    if message.content.startswith('$list'):
        lst = message.content.rsplit(' ')
        res = "List:\n"
        if len(lst) != 1 or lst[0] != "$list":
            res = "Invalid command! Use $help to check out the commands"
        else:
            for guild in client.guilds:
                for member in guild.members:
                    for role in member.roles: 
                        # TODO: change role id
                        if(role.id in roles_list):
                            res += member.nick if member.nick != None else member.name 
                            res += "\n"
                            break
        
        await message.channel.send(res)
        return
   
    # only allow admin to query 'update' 
    #$update [leaderboard_name] [member_id] [points]
    if message.content.startswith('$update'):
        lst = message.content.rsplit(' ')
        res = ""
        if (len(lst) != 3 and len(lst) != 4) or lst[0] != "$update" or RepresentsInt(lst[len(lst) - 1]) == False:
            res = "Invalid command! Use $help to check out the commands"
        else: 
            if message.author.id not in admin:
                await message.channel.send("Trying to cheat, uh? :smirk:")
                return
            name = ""
            ind = 1
            filename = "table.json"
            if len(lst) == 4:
                if not is_exists_json(str(lst[1] + ".json")):
                    await message.channel.send("leaderboard doesn't exist!")
                    return 
                ind = 2
                filename = lst[1] + ".json"

            points = lst[len(lst) - 1]
            ok = 0
            member_id = lst[ind]
            member_name = ""

            for guild in client.guilds:
                for member in guild.members:
                    if(str(member.id) == member_id):
                        member_name = member.nick if member.nick != None else member.name 
                        ok = 1
        
            if (ok == 0): 
                await message.channel.send("Member not in server")
                return

            table = get_table(filename)

            if member_id not in table :
                table[member_id] = 0
        
            table[member_id] = table[member_id] + int(points)

            write_table(filename, table)
            res = "Successfully updated! :sunglasses:\nAdded " + points + " points to " + member_name + "!"

        await message.channel.send(res)
        return

    if message.content.startswith('$show'):
        lst = message.content.rsplit(' ')
        res = ""
        if (len(lst) != 1 and len(lst) != 2) or lst[0] != "$show":
            res = "Invalid command! Use $help to check out the commands"
        else: 
            filename = "table.json"
            if len(lst) == 2:
                if not is_exists_json(str(lst[1] + ".json")):
                    await message.channel.send("leaderboard doesn't exist!")
                    return 
                filename = lst[1] + ".json"
            table = get_table(filename)
            # sort table
            table = sorted(table.items(), key=lambda item: item[1], reverse=True)
            table = dict(table)

            counter = 1
            res = "```\n"
            for member_id in table :
                member_name = ""
                for guild in client.guilds:
                    for member in guild.members:
                        if(str(member.id) == member_id):
                            member_name = member.nick if member.nick != None else member.name 

                res += str(counter) + ". " + member_name + " :" + str(table[member_id]) + "\n"
                counter += 1
            res += "```"
        
        await message.channel.send(res)
        return 
    
    if message.content.startswith('$refresh'):
        lst = message.content.rsplit(' ')
        res = ""
        if len(lst) != 1 or lst[0] != "$refresh":
            res = "Invalid command! Use $help to check out the commands"
        else: 
            table = get_table("table.json")
            for guild in client.guilds:
                for member in guild.members:
                    for role in member.roles: 
                        if(role.id in roles_list):
                            if str(member.id) not in table:
                                table[member.id] = 0
        
            write_table("table.json", table)
            res = "Refreshed!"

        await message.channel.send(res)
        return 

    if message.content.startswith('$help'):
        await message.channel.send(print_help()) 
        return 

    if message.content.startswith('$dump'):
        lst = message.content.rsplit(' ')
        res = ""
        if (len(lst) != 2 and len(lst) != 1) or lst[0] != "$dump":
            res = "Invalid command! Use $help to check out the commands"
        else:
            if message.author.id not in admin:
                await message.channel.send("Dev/Admin only!")
                return
            filename = "table.json"
            if len(lst) == 2:
                if not is_exists_json(str(lst[1] + ".json")):
                    await message.channel.send("leaderboard doesn't exist!")
                    return 
                filename = lst[1] + ".json"
            
            table = get_table(filename)
            res = table
        
        await message.channel.send(res)
        return    
    
    if message.content.startswith('$top'):
        lst = message.content.rsplit(' ')
        res = ""
        if len(lst) != 2 and len(lst) != 3:
            res = "Invalid number of arguments!"
        elif lst[0] != "$top":
            res = "Invalid command! Use $help to check out the commands"
        else:
            filename = "table.json"
            if len(lst) == 3:
                if not is_exists_json(str(lst[1] + ".json")):
                    await message.channel.send("leaderboard doesn't exist!")
                    return 
                filename = lst[1] + ".json"
            
            table = get_table(filename)
            if RepresentsInt(lst[len(lst) - 1]): 
                lim = int(lst[len(lst) - 1])
                if lim > 0:
                    lim = min(lim, len(table))

                    table = sorted(table.items(), key=lambda item: item[1], reverse=True)
                    table = dict(table)

                    counter = 1
                    res = "```\n"
                    for member_id in table :
                        if counter > lim:
                            break
                        member_name = ""
                        for guild in client.guilds:
                            for member in guild.members:
                                if(str(member.id) == member_id):
                                    member_name = member.nick if member.nick != None else member.name

                        res += str(counter) + ". " + member_name + " :" + str(table[member_id]) + "\n"
                        counter += 1
                    res += "```"
                else: 
                    res = "Invalid argument! Enter a positive integer"
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
            table = get_table("table.json")
            del table[member_id]
            res = "Successfully deleted!"

            write_table("table.json", table)
        await message.channel.send(res)
        return


    # creation and deletion of json files aka tables
    if message.content.startswith('$create'):
        if message.author.id not in admin :
            res = "Dev/Admin only!"
        else:
            # $create [table_name]
            lst = message.content.rsplit(' ')
            if len(lst) != 2 or lst[0] != "$create":
                res = "Invalid format!"
            else:
                if not os.path.isfile(lst[1] + ".json"):
                    write_table(lst[1] + ".json", {})
                res = lst[1] + ".json created!" 
            
        await message.channel.send(res)

    if message.content.startswith('$delete'):
        if message.author.id not in admin :
            res = "Dev/Admin only!"
        else:
            # $remove [table_name]
            lst = message.content.rsplit(' ')
            if len(lst) != 2 or lst[0] != "$delete":
                res = "Invalid format!"
            else:
                if not os.path.isfile(lst[1] + ".json"):
                    res = "leaderboard doesn't exist!"
                else:
                    os.remove(lst[1] + ".json")
                res = lst[1] + ".json removed!" 
            
        await message.channel.send(res)

    if message.content.startswith('$ls'):
        if message.content != "$ls":
            res = "Invalid command! Use $help to check out the commands"
        else:
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            res = "```\n"
            for f in files:
                if f.endswith('.json'):
                    res += f[:-5] + "\n"
            res += "```"

        await message.channel.send(res)

client.run(os.environ.get('LEADERBOARD_BOT_TOKEN'))