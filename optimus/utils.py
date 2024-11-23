class SingletonMeta(type):
    __INSTANCE: dict[str, object] = dict()

    def __new__(cls, cls_name, cls_bases, cls_attrs):
        if cls_name not in cls.__INSTANCE:
            cls.__INSTANCE[cls_name] = type(cls_name, cls_bases, cls_attrs)
        return cls.__INSTANCE[cls_name]
