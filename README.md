# Orange QuoteBook

Orange QuoteBook is a Discord bot that allows users to save and manage quotes within a quotebook. The bot provides commands for saving quotes, viewing quotebooks, removing quotes, searching for quotes, and more. This repository contains the source code for the Orange QuoteBook Discord bot.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Contributing](#contributing)
- [License](#license)

## Installation

To use Orange QuoteBook, you need to follow these steps:

1. Clone this repository to your local machine or download the source code as a ZIP file.
2. Install the required dependencies by running the following command:

```
pip install py-cord pyyaml flask
```
3. Set up a Discord bot on the Discord Developer Portal and obtain the bot token.
4. Create a file named `.env` in the root directory of the project and add the following line to it:

```
DISCORD_TOKEN=your_bot_token
```
Replace `your_bot_token` with the actual bot token you obtained in the previous step.
6. Run the bot using the following command:

```
python bot.py
```

Make sure you have Python 3.7 or above installed on your machine.

## Usage

Once the bot is running and connected to your Discord server, you can interact with it using various commands. The bot's command prefix is `!` by default.

To save a quote to your quotebook, use the `/save` command followed by the quote you want to save:

```
/save This is an example quote.
```


To view your quotebook or someone else's quotebook, use the `/quotebook` command followed by the user's mention:

```
/quotebook @username
```


To remove a quote from your quotebook, use the `/remove` command followed by the quote number:

```
/remove 2
```


To search for a quote in a user's quotebook, use the `/search` command followed by the user's mention and the search query:

```
/search @username example
```


For more information about available commands and how to use them, you can use the `/help` command.

## Commands

Orange QuoteBook provides the following commands:

- `/save <quote>`: Save a quote to the quotebook.
- `/quotebook <user>`: Show a specific member's quotebook.
- `/remove <quote_number>`: Remove a quote from the quotebook.
- `/search <user> <query>`: Search for a quote in a user's quotebook.
- `/random_quote`: Find a random quote in any quotebook.
- `/help`: Get help about how to use the bot.
- `/export <user> <format>`: Export a quotebook as CSV, JSON, XML, or YAML.
- `/delete_all`: Delete all quotes in your quotebook.

## Contributing

Contributions to Orange QuoteBook are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
