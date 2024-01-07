class Author:

    def __init__(self):
        DEFAULT_VALUE = "--"

        self.link = DEFAULT_VALUE
        self.name = DEFAULT_VALUE
        self.level = DEFAULT_VALUE
        self.memberSince = DEFAULT_VALUE
        self.city = DEFAULT_VALUE
        self.contributions = DEFAULT_VALUE
        self.helpful = DEFAULT_VALUE
        self.cites = DEFAULT_VALUE
        self.photos = DEFAULT_VALUE
        #self.tag = DEFAULT_VALUE
        self.distributionExcellent = DEFAULT_VALUE
        self.distributionVeryGood = DEFAULT_VALUE
        self.distributionAverage = DEFAULT_VALUE
        self.distributionPoor = DEFAULT_VALUE
        self.distributionTerrible = DEFAULT_VALUE

        #Added for Yelp
        self.friends = DEFAULT_VALUE
        self.photos = DEFAULT_VALUE
        self.reviews = DEFAULT_VALUE
        self.tagsReviewMap = dict()
        self.tagsComplimentMap = dict()
        
    def getCsvRecord(self):
        authorData = self.__dict__
        extraData = dict()
        for key in authorData:
            if type(authorData[key]) is dict:
                dictValues = authorData[key]
                for k, v in dictValues.items():
                    extraData[k] = v
            else:
                authorData[key] = authorData[key].replace(";", " ")
        return {**authorData, **extraData}