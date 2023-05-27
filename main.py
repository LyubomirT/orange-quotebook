import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from keep_alive import keep_alive
import os
import random
import json
import yaml
import xml.etree.ElementTree as ET
import csv

bot = commands.Bot(prefix="!", intents=discord.Intents().all())
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"bot connected as {bot.user}")

quotebook = {}

def save_quotebook():
    with open("data.txt", "w") as file:
        json.dump(quotebook, file)

def load_quotebook():
    global quotebook
    if os.path.isfile("data.txt"):
        with open("data.txt", "r") as file:
            loaded_data = json.load(file)
            quotebook = {int(key): value for key, value in loaded_data.items()}
        print(quotebook)

@bot.slash_command(name="save", description="Save a quote to the quotebook!")
async def save(ctx, quote: str):
    user_id = ctx.author.id
    if user_id not in quotebook:
        quotebook[user_id] = []  # Create an empty list for the user if it doesn't exist
    quotebook[user_id].append(quote)  # Add the quote to the user's list of quotes
    save_quotebook()  # Save the quotebook to the file
    await ctx.respond(f"Saved quote '{quote}' from user {ctx.author.mention}!")

@bot.slash_command(name="quotebook", description="Show a specific member's quotebook")
async def show_quotebook(ctx, user: discord.Member):
    user_id = user.id
    if user_id in quotebook:
        quotes = quotebook[user_id]
        page_size = 5
        num_pages = (len(quotes) + page_size - 1) // page_size

        async def update_page(page_num):
            start_index = page_num * page_size
            end_index = min(start_index + page_size, len(quotes))
            embed = discord.Embed(title=f"Quotebook of {user.name}", description=f"Page {page_num+1} of {num_pages}")
            for i in range(start_index, end_index):
                thing = quotes[i].replace("\n", " ")
                numerator = (str(i+1)).replace("\n", "")
                embed.add_field(name=f"{numerator}.", value=f"*'{thing}'*", inline=False)
            return embed

        current_page = 0
        view = discord.ui.View()
        if num_pages > 1:
            class QuotebookView(discord.ui.View):
                @discord.ui.button(label="<-", style=discord.ButtonStyle.primary)
                async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
                    nonlocal current_page
                    current_page -= 1
                    if current_page < 0:
                        current_page = num_pages - 1
                    await interaction.response.edit_message(embed=await update_page(current_page))

                @discord.ui.button(label="->", style=discord.ButtonStyle.primary)
                async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
                    nonlocal current_page
                    current_page += 1
                    if current_page >= num_pages:
                        current_page = 0
                    await interaction.response.edit_message(embed=await update_page(current_page))

            view = QuotebookView()

        await ctx.respond(embed=await update_page(current_page), view=view)
    else:
        response = f"No quotebook found for {user.mention}."
        await ctx.respond(response)

@bot.slash_command(name="remove", description="Remove a quote from the quotebook!")
async def remove_quote(ctx, quote_number: int):
    user_id = ctx.author.id
    if user_id in quotebook and len(quotebook[user_id]) >= quote_number:
        value = quotebook[user_id][quote_number - 1]
        quotebook[user_id].pop(quote_number - 1)
        save_quotebook()  # Save the quotebook to the file
        await ctx.respond(f"Removed quote number {quote_number} (*'{value}'*) from {ctx.author.mention}'s quotebook!")
    else:
        await ctx.respond(f"No quote with number {quote_number} found in {ctx.author.mention}'s quotebook.")

@bot.slash_command(name="search", description="Search for a quote in a user's quotebook")
async def search_quotebook(ctx, user: discord.Member, query: str):
    user_id = user.id
    if user_id in quotebook:
        quotes = quotebook[user_id]
        search_results = [quote for quote in quotes if query.lower() in quote.lower()]

        if search_results:
            page_size = 5
            num_pages = (len(search_results) + page_size - 1) // page_size

            async def update_page(page_num):
              start_index = page_num * page_size
              end_index = min(start_index + page_size, len(search_results))
              embed = discord.Embed(title=f"Search Results for '{query}' in {user.name}'s Quotebook",
                                    description=f"Page {page_num+1} of {num_pages}")
              for i in range(start_index, end_index):
                  thing = search_results[i].replace("\n", " ")
                  numerator = (str(i+1)).replace("\n", "")
                  highlighted_quote = thing.replace(query, f"**__{query}__**")
                  embed.add_field(name=f"{numerator}.", value=f"*'{highlighted_quote}'*", inline=False)
              return embed

            current_page = 0
            view = discord.ui.View()
            if num_pages > 1:
                class SearchResultsView(discord.ui.View):
                    @discord.ui.button(label="<-", style=discord.ButtonStyle.primary)
                    async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
                        nonlocal current_page
                        current_page -= 1
                        if current_page < 0:
                            current_page = num_pages - 1
                        await interaction.response.edit_message(embed=await update_page(current_page))

                    @discord.ui.button(label="->", style=discord.ButtonStyle.primary)
                    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
                        nonlocal current_page
                        current_page += 1
                        if current_page >= num_pages:
                            current_page = 0
                        await interaction.response.edit_message(embed=await update_page(current_page))

                view = SearchResultsView()

            await ctx.respond(embed=await update_page(current_page), view=view)
        else:
            response = f"No quotes found in {user.mention}'s quotebook that match the search query '{query}'."
            await ctx.respond(response)
    else:
        response = f"No quotebook found for {user.mention}."
        await ctx.respond(response)

@bot.message_command(name="Save Quote") # create a message command for the supplied guilds
async def save_quote(ctx, message: discord.Message): # message commands return the message
    user_id = ctx.author.id # get the user id of the command executioner
    if user_id == message.author.id: # check if the message is sent by the command executioner
        if user_id not in quotebook:
            quotebook[user_id] = []  # Create an empty list for the user if it doesn't exist
        quotebook[user_id].append(message.content)  # Add the message content to the user's list of quotes
        save_quotebook()  # Save the quotebook to the file
        await ctx.respond(f"Saved quote '{message.content}' from user {ctx.author.mention}!")
    else:
        await ctx.respond("You can only save your own messages as quotes.")

@bot.user_command(name="Show Quotebook") # create a user command for the supplied guilds
async def show_quotebook_context(ctx, user: discord.Member): # user commands return the member
    user_id = user.id # get the user id of the targeted member
    if user_id in quotebook:
        quotes = quotebook[user_id]
        page_size = 5
        num_pages = (len(quotes) + page_size - 1) // page_size

        async def update_page(page_num):
            start_index = page_num * page_size
            end_index = min(start_index + page_size, len(quotes))
            embed = discord.Embed(title=f"Quotebook of {user.name}", description=f"Page {page_num+1} of {num_pages}")
            for i in range(start_index, end_index):
                thing = quotes[i].replace("\n", " ")
                numerator = (str(i+1)).replace("\n", "")
                embed.add_field(name=f"{numerator}.", value=f"*'{thing}'*", inline=False)
            return embed

        current_page = 0
        view = discord.ui.View()
        if num_pages > 1:
            class QuotebookView(discord.ui.View):
                @discord.ui.button(label="<-", style=discord.ButtonStyle.primary)
                async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
                    nonlocal current_page
                    current_page -= 1
                    if current_page < 0:
                        current_page = num_pages - 1
                    await interaction.response.edit_message(embed=await update_page(current_page))

                @discord.ui.button(label="->", style=discord.ButtonStyle.primary)
                async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
                    nonlocal current_page
                    current_page += 1
                    if current_page >= num_pages:
                        current_page = 0
                    await interaction.response.edit_message(embed=await update_page(current_page))

            view = QuotebookView()

        await ctx.respond(embed=await update_page(current_page), view=view)
    else:
        response = f"No quotebook found for {user.mention}."
        await ctx.respond(response)

@bot.slash_command(name="random_quote", description="Find a random quote in any quotebook")
async def random_quote(ctx):
    # Get a random user from the quotebook
    random_user = random.choice(list(quotebook.keys()))

    if random_user in quotebook:
        quotes = quotebook[random_user]
        random_quote = random.choice(quotes)
        author = bot.get_user(random_user)

        response = f"{random_quote} - {author.name}"
        await ctx.respond(response)
    else:
        await ctx.respond("No quotes found.")


@bot.slash_command(name="help", description="Get help about how to use the bot!")
async def hellp(ctx):
    embed = discord.Embed(title="Support", description="How to use the bot?", color=discord.Colour.random())
    embed.add_field(name="How to add my quote to the quotebook?", value="Use `/save <your_quote>`, or right-click a message (hold on mobile), select `Apps`, and use `Save Quote` option of Orange QuoteBook", inline=False)
    embed.add_field(name="How to view my/other user's quotebook?", value="Right-click a user (hold on mobile), select `Apps`, and choose the `Show Quotebook` option of Orange QuoteBook. You can also use `/quotebook <user>`", inline=False)
    embed.add_field(name="I don't like my quote. How to remove it?", value="Use `/remove <quote_number>`. The number is the number it's ordered with in your QuoteBook.", inline=False)
    embed.add_field(name="How to find a quote in someone's quotebook?", value="You can try using `/search <user> <query>`. This will allow you to find quotes that match your search query in the quotebook of that user.", inline=False)
    embed.add_field(name="How can I find a random quote in any quotebook?", value="You can use `/random_quote`. It will find a random quote across all the quotebooks, and will showcase it to you.", inline=False)
    embed.add_field(name="I want to store my quotebook on my machine. How can I do that?", value="You can use the `/export <user> <format>` command. It will allow you to get the quotebook of the user you want to get it from, and then it will be sent to you as a CSV/JSON/XML/YAML file.", inline=False)
    embed.add_field(name="I don't like my quots. How to get rid of all of them?", value="At first, it's recommended to first /export your quotebook, just to ensure you will not lose it forever. For deleting all your quotes, simply use the `/delete_all` command.", inline=False)
    embed.add_field(name="How to import my quotebook from I file I got with /export?", value="To do this, send an empty message to any place you want. Then, right-click that message (not the file) and select Apps. After that, click on 'Import Quotebook' from Orange QuoteBook. If the file is in appropriate format, you will be able to get the quotes from the file in your quotebook.", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name="export", description="Export a quotebook as CSV/JSON/XML/YAML")
async def export_quotebook(ctx, user: discord.Member, format: Option(str, choices=["csv", "json", "xml", "yaml"]) = "json"):
    user_id = user.id
    if user_id in quotebook:
        quotes = quotebook[user_id]

        if format.lower() == "csv":
            filename = f"{user.name}_quotebook.csv"
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Quotes"])
                writer.writerows([[quote] for quote in quotes])

        elif format.lower() == "json":
            filename = f"{user.name}_quotebook.json"
            with open(filename, "w") as file:
                json.dump({user_id: quotes}, file, indent=4)  # Wrap the quotebook in curly brackets

        elif format.lower() == "xml":
            root = ET.Element("quotebook")
            for quote in quotes:
                quote_element = ET.SubElement(root, "quote")
                quote_element.text = quote
            tree = ET.ElementTree(root)
            filename = f"{user.name}_quotebook.xml"
            tree.write(filename)

        elif format.lower() == "yaml":
            filename = f"{user.name}_quotebook.yaml"
            with open(filename, "w") as file:
                yaml.dump(quotes, file)

        else:
            await ctx.respond("Invalid format. Please choose CSV, JSON, XML, or YAML.")
            return

        await ctx.respond(f"Quotebook exported as {format.upper()} for {user.name}.", file=discord.File(filename))
        os.remove(filename)

    else:
        response = f"No quotebook found for {user.mention}."
        await ctx.respond(response)


@bot.slash_command(name="delete_all", description="Delete all quotes in your quotebook")
async def delete_all_quotes(ctx):
    user_id = ctx.author.id
    if user_id in quotebook:
        quotebook[user_id] = []  # Clear the user's list of quotes
        save_quotebook()  # Save the updated quotebook to the file
        await ctx.respond(f"All quotes have been deleted from your quotebook, {ctx.author.mention}!")
    else:
        await ctx.respond(f"No quotebook found for {ctx.author.mention}.")


@bot.message_command(name="Import Quotebook")  # create a message command for importing the quotebook
async def import_quotebook(ctx, message: discord.Message):  # message commands return the message
    user_id = ctx.author.id  # get the user id of the command executioner
    if user_id == message.author.id:  # check if the message is sent by the command executioner
        attachments = message.attachments # get the first attachment from the message
        if len(attachments) == 0:
          await ctx.respond("There aren't any files attached to the target message.")
          return
        else:
          attachment = attachments[0]
        filename = attachment.filename.lower()  # get the lowercase filename
        valid_formats = ["json", "xml", "yaml", "csv"]  # valid file formats
        if any(filename.endswith("." + format) for format in valid_formats):
            # download the file
            await attachment.save(filename)
            # import the quotebook based on the file format
            if filename.endswith(".json"):
                with open(filename, "r") as file:
                    quotebook_data = json.load(file)
                # validate the imported data if necessary
                # ...
            elif filename.endswith(".xml"):
                tree = ET.parse(filename)
                root = tree.getroot()
                quotebook_data = []
                for quote_element in root.findall("quote"):
                    quotebook_data.append(quote_element.text)
                # validate the imported data if necessary
                # ...
            elif filename.endswith(".yaml"):
                with open(filename, "r") as file:
                    quotebook_data = yaml.safe_load(file)
                # validate the imported data if necessary
                # ...
            elif filename.endswith(".csv"):
                with open(filename, "r") as file:
                    reader = csv.reader(file)
                    quotebook_data = [row[0] for row in reader]
                # validate the imported data if necessary
                # ...
            else:
                await ctx.respond("Invalid file format. Please upload a JSON, XML, YAML, or CSV file.")
                return

            # update the quotebook with the imported data
            if user_id not in quotebook:
              quotebook[user_id] = quotebook_data
            else:
              quotebook[user_id].extend(quotebook_data)
            save_quotebook()  # Save the quotebook to the file
            await ctx.respond(f"Quotebook imported from file '{filename}' for user {ctx.author.mention}!")
            os.remove(filename)  # remove the temporary file
        else:
            await ctx.respond("Invalid file format. Please upload a JSON, XML, YAML, or CSV file.")
    else:
        await ctx.respond("You can only import your own quotebook.")





load_quotebook()  # Load the quotebook from the file
keep_alive()
bot.run(os.environ["DONOTEVENTOUCH"])
