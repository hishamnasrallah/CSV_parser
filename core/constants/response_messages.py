class ResponseConstants:
    # Message Keys
    RETRIEVED = "retrieved"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    # Messages
    RETRIEVED_MSG = {
        "en": "The data retrieved successfully",
        "ar": "تم الوصول للبيانات بنجاح"
    }

    CREATED_MSG = {
        "en": "The data created successfully",
        "ar": "تم تخزين البيانات بنجاح"
    }

    UPDATED_MSG = {
        "en": "The data updated successfully",
        "ar": "تم تحديث البيانات بنجاح"
    }

    DELETED_MSG = {
        "en": "The data deleted successfully",
        "ar": "تم حذف البيانات بنجاح"
    }

    @classmethod
    def messages_dict(cls):
        return {
            cls.RETRIEVED: cls.RETRIEVED_MSG,
            cls.DELETED: cls.DELETED_MSG,
            cls.UPDATED: cls.UPDATED_MSG,
            cls.CREATED: cls.CREATED_MSG,
        }

    @classmethod
    def get_message_by_key(cls, message_key):
        if message_key in cls.messages_dict():
            return cls.messages_dict()[message_key]
        else:
            return message_key
