# MineMineNoMiBot

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![Stars](https://img.shields.io/github/stars/Sly0511/MineMinenoMiBot.svg)
![Forks](https://img.shields.io/github/forks/Sly0511/MineMinenoMiBot.svg)
![Issues](https://img.shields.io/github/issues/Sly0511/MineMinenoMiBot.svg)

A Discord bot written in Python that reads data from the [Mine Mine no Mi](https://www.curseforge.com/minecraft/mc-mods/mine-mine-no-mi) minecraft mod

<hr>

### Features
- Automatic role assignment of Races, Factions and Fighting Style discord roles
- Generation of pie charts of the server population in each Race, Faction or Fighting Style

<hr>

### Installation
#### Required software
- [Python 3.11](https://www.python.org/downloads/)
- [MongoDB](https://www.mongodb.com/try/download/community) _I honestly hate SQL don't question this_

#### Required Python libraries
- Listed in [requirements.txt](/requirements.txt)
```shell
pip install -r requirements.txt
```

<hr>

### Configuration
Make to set up variables in the `config.toml`
#### Variables required
- `bot.token`         Discord Bot Token to make requests to the API and connect to the websocket
- `bot.owners`        Set at least one owner so that you can run `update` command for slash commands
- `bot.server`        Server ID of the discord server bot will be running on (required to set up slash commands)
- `mineminenomi.ftp`  SFTP client will run into errors while trying to connect
- `mineminenomi.rcon` This is required mostly for account linking and using `rcon` command

<hr>

### Developer note:
> I am not in any way responsible for the bad code presented to you in this repository, I am not even sure how the hell I landed a job in software development without a degree, don't question code, just pull request if you are bothered.

