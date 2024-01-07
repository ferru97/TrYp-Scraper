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

        #added for yelp
        category = DEFAULT_VALUE
        restaurantLink = DEFAULT_VALUE
        useful = DEFAULT_VALUE
        funny = DEFAULT_VALUE
        cool = DEFAULT_VALUE

    def getCsvRecord(self):
        reviewData = self.__dict__
        extraData = dict()
        for key in reviewData:
            if isinstance(reviewData[key], dict):
                dictValues = reviewData[key]
                for k, v in dictValues.items():
                    extraData[k] = v
            else:
                reviewData[key] = reviewData[key].replace(";", " ")
        return {**reviewData, **extraData}



        