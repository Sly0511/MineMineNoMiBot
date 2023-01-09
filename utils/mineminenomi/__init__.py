from uuid import UUID


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


def int_array_to_uuid(int_array: list) -> str:
    return UUID(
        "".join(
            [str(hex(i + (2**32 if i < 0 else 0)))[2:].zfill(8) for i in int_array]
        )
    )
