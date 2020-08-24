class Helper:

    @staticmethod
    def tagsToTable(tag_dict, headline=False):
        def g_l(len, sep="-"):
            v = ""
            v += "+"
            v += sep * len
            v += "+"
            v += sep * len
            v += "+"
            return v

        key_max_length = 0
        val  = ""
        for item in tag_dict:
            for k,v in item.items():
                if key_max_length < len(k):
                    key_max_length = len(k)
                if key_max_length < len(v):
                    key_max_length = len(v)

        key_max_length += 2

        val += g_l(key_max_length)+"\n"
        for item in tag_dict:

            for k, v in item.items():
                val += "|"
                if headline:
                    val += " {} ".format(k).ljust(key_max_length)
                else:
                    val += " {} ".format(v).ljust(key_max_length)
            val += "| \n"

            if headline:
                val += g_l(key_max_length, sep="=")+"\n"
                headline = False
            else:
                val += g_l(key_max_length)+"\n"
        return val