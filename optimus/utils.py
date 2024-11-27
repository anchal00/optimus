class SingletonMeta(type):
    __INSTANCE: dict[str, object] = dict()

    def __new__(cls, cls_name, cls_bases, cls_attrs):
        if cls_name not in cls.__INSTANCE:
            cls.__INSTANCE[cls_name] = type(cls_name, cls_bases, cls_attrs)
        return cls.__INSTANCE[cls_name]


def to_n_bytes(data: int, n: int) -> bytearray:
    """Given an integer, converts it to a bytearray of size n"""
    ret = bytearray()
    mask = 0xFF
    for i in range(n):
        right_shift_by_bits = 8 * i
        temp = (data >> right_shift_by_bits) & mask
        ret.append(temp)
    ret.reverse()
    return ret
