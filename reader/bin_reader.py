
class BinReader:
    def __init__(self, bin_data: bytearray) -> None:
        self.__bin_data_block = bin_data
        self.__ptr = 0

    def increment_ptr(self, steps: int) -> None:
        self.__ptr += steps

    def seek_ptr_pos(self, pos: int) -> None:
        self.__ptr = pos

    def get_cur_ptr_pos(self) -> int:
        return self.__ptr

    def parse_bytes(self, bytes_to_parse: int) -> int:
        to_be_read_data_block = self.__bin_data_block[self.__ptr:]
        data = 0
        for x in to_be_read_data_block[:bytes_to_parse]:
            data = data << 8 | x
        return data

    def parse_bytes_and_move_ahead(self, bytes_to_parse: int) -> int:
        to_be_read_data_block = self.__bin_data_block[self.__ptr:]
        data = 0
        for x in to_be_read_data_block[:bytes_to_parse]:
            data = data << 8 | x
            self.increment_ptr(1)
        return data