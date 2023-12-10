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
        fullReviewLink = DEFAULT_VALUE

    def getCsvRecord(self):
        reviewData = self.__dict__
        for key in reviewData:
            reviewData[key] = reviewData[key].replace(";", " ")
        return reviewData



        