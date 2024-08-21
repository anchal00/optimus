class ByteArrayIterator:
    def __init__(self, data: bytearray) -> None:
        self.__data = data
        self.__ptr = 0

    def seek_ptr_pos(self, pos: int) -> None:
        self.__ptr = pos

    def get_cur_ptr_pos(self) -> int:
        return self.__ptr

    def get_n_bytes(self, n: int) -> bytearray:
        cur_ptr_pos = self.get_cur_ptr_pos()
        return self.__data[cur_ptr_pos : cur_ptr_pos + n]

    def get_n_bytes_and_move(self, n: int) -> bytearray:
        data = self.get_n_bytes(n)
        self.seek_ptr_pos(self.get_cur_ptr_pos() + n)
        return data
