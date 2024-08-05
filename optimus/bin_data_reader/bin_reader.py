class BinReader:
    def __init__(self, bin_data: bytearray) -> None:
        self.__bin_data_block = bin_data
        self.__ptr = 0

    def seek_ptr_pos(self, pos: int) -> None:
        self.__ptr = pos

    def get_cur_ptr_pos(self) -> int:
        return self.__ptr

    def read_bytes_and_move(self, bytes_to_read) -> bytearray:
        cur_ptr_pos = self.get_cur_ptr_pos()
        return self.__bin_data_block[cur_ptr_pos : cur_ptr_pos + bytes_to_read]

    def parse_bytes_to_int(self, bytes_to_parse: int) -> int:
        cur_ptr_pos = self.get_cur_ptr_pos()
        to_be_read_data_block = self.__bin_data_block[
            cur_ptr_pos : cur_ptr_pos + bytes_to_parse
        ]
        data = 0
        for x in to_be_read_data_block:
            data = data << 8 | x
        return data

    def parse_bytes_to_int_and_move(self, bytes_to_parse: int) -> int:
        data = self.parse_bytes_to_int(bytes_to_parse)
        self.seek_ptr_pos(self.get_cur_ptr_pos() + bytes_to_parse)
        return data
