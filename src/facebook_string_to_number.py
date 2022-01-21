class FacebookStringToNumber:
    def convertStringToNumber(self, text):
        text_clean = text
        text_clean = text_clean.replace("\xa0", "")
        text_clean = text_clean.replace("personas", "")
        text_clean = text_clean.replace("persona", "")

        if "mill." in text_clean:
            text_clean = text_clean.replace("mill.", "")
            text_clean = text_clean.replace(",", "")
            number = float(text_clean) * 1000000
            return int(number)

        if "mil" in text_clean:
            text_clean = text_clean.replace("mil", "")
            text_clean = text_clean.replace(",", ".")
            number = float(text_clean) * 1000
            return int(number)

        return int(float(text_clean.replace(".", "")))
