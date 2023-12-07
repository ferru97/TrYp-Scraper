from src.model.Author import Author

class Review:

    def __init__(self):
        DEFAULT_VALUE = "--"

        user = DEFAULT_VALUE
        restaurant = DEFAULT_VALUE
        title = DEFAULT_VALUE
        date = DEFAULT_VALUE
        starsValue = DEFAULT_VALUE
        text = DEFAULT_VALUE
        restaurnat = DEFAULT_VALUE
        

    def getCsvRecord(self):
        authorData = self._author.__dict__
        renamedAuthorData = dict()
        for key in authorData:
            renamedAuthorData["author_"+key] = authorData[key]

        reviewData = self.__dict__
        reviewData.pop("_author", None)

        return reviewData | renamedAuthorData




        