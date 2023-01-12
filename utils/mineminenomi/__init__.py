from uuid import UUID

from mcrcon import MCRcon, MCRconException


class NBTParser:
    @classmethod
    def parse(cls, data):
        return cls.parse_nbt(cls.convert_data_type(data))

    @classmethod
    def parse_nbt(cls, data):
        if isinstance(data, list):
            for d in data:
                cls.parse_nbt(d)
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = cls.convert_data_type(value)
                cls.parse_nbt(data[key])
        return data

    @classmethod
    def datatypes(cls, datatype):
        match datatype:
            case 1:
                return bool
            case 2 | 3 | 4:
                return int
            case 5 | 6:
                return float
            case 7 | 9 | 11 | 12:
                return list
            case 8:
                return str
            case 10:
                return dict

    @classmethod
    def convert_data_type(cls, data):
        return cls.datatypes(data.get("type_id"))(data["value"])


def int_array_to_uuid(int_array: list) -> UUID:
    return UUID(
        "".join(
            [str(hex(i + (2**32 if i < 0 else 0)))[2:].zfill(8) for i in int_array]
        )
    )


def run_rcon_command(bot, command):
    if not getattr(bot, "server_status", False):
        return
    config = bot.config.mineminenomi.rcon
    try:
        with MCRcon(
            host=config.host, port=config.port, password=config.password, timeout=2
        ) as rcon:
            if isinstance(command, str):
                if not command.startswith("/"):
                    command = f"/{command}"
                result = rcon.command(command) or "Command successfully executed."
                bot.logger.debug(f"Executed command on server: {command}")
                return result
            if isinstance(command, list):
                command = [
                    cmd if cmd.startswith("/") else f"/{cmd}" for cmd in command
                ]
                results = [
                    rcon.command(cmd) or "Command successfully executed"
                    for cmd in command
                ]
                return results
    except (TimeoutError, ConnectionRefusedError) as err:
        bot.logger.error(
            f"Network: Failed executing command on server | {err}: {command}"
        )
        return
    except MCRconException as err:
        bot.logger.error(
            f"Exception: Failed executing command on server | {err}: {command}"
        )
        return
