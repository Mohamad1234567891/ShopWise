from src.Operations import StringOperations

def ConvertValueToMaxOf5(value, strMaxValue=None):
    """Converts a value to a scale between 0 and 5 based on the maximum value. if a maximum value is not provided and the value was a string it tries to analyze that string and infer
       the maximum value from it.

    value: A string, int, or a float value representing the value we want to do the operation on.
    strMaxValue: An optional string including the maximum scale.


    Examples:
        strMaxValue = "100"
        value = 50
        output -> 2.5
        ----------------------
        strMaxValue = "10"
        value = 5
        output -> 2.5
        ----------------------
        strMaxValue = None
        value = "5/10"
        output -> 2.5
        ----------------------
        strMaxValue = None
        value = "50%"
        output -> 2.5
    """


    if value is None or isinstance(value, bool) or value == "":
        return None

    nums = [float(value)] if isinstance(value, (int, float)) else StringOperations.ExtractNumbersFromText(value)

    if not nums:
        return None

    maxValues = StringOperations.ExtractNumbersFromText(strMaxValue) if strMaxValue not in (None, "") else []

    maxValue = maxValues[0] if maxValues else None

    pair = nums[:2]

    if maxValue:
        rawValue = min(pair) if len(pair) == 2 and max(pair) == maxValue else nums[0]

    elif len(pair) == 2 and max(pair) in (5, 10, 100):
        rawValue, maxValue = min(pair), max(pair)

    else:
        rawValue = nums[0]
        maxValue = 5 if rawValue <= 5 else 10 if rawValue <= 10 else 100 if rawValue <= 100 else None

    if not maxValue or rawValue < 0:
        return None

    result = round(rawValue / maxValue * 5, 2) if maxValue != 5 else round(rawValue, 2)

    return result if result <= 5 else None