class Parser:
    bin_data_block: bytearray
    ptr = 0

    def __init__(self, bin_data: bytearray):
        self.bin_data_block = bin_data
        self.ptr = 0

    def increment_ptr(self, steps: int):
        self.ptr = self.ptr + steps

    def parse_bytes_and_move_ahead(self, bytes_to_parse: int):
        to_be_read_data_block = self.bin_data_block[self.ptr:]
        data = 0
        for x in to_be_read_data_block[:bytes_to_parse]:
            data = data << 8 | x
            self.increment_ptr(1)
        return data
