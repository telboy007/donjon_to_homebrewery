""" Dict to hold details of donjon corridor features """

NEWLINE = "\n"


def create_donjon_corridor_features(data):
    """Corridor features"""
    corridor_features = {}
    feature_list = []

    corridor_features["features"] = False
    # populate details if available
    if "corridor_features" in data:
        corridor_features["features"] = True
        # add and format features to list
        for key, val in data["corridor_features"].items():
            feature_list.append({val["key"]: val["detail"].replace(NEWLINE, " ")})
        corridor_features["feature_list"] = feature_list

    return corridor_features
