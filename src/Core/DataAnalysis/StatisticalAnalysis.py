import statistics
import re

from src.Core.DataAnalysis import SentimentAnalysis as SA
from src.Core.DataAnalysis import Translator as T

# Keep your existing imports for these two modules, for example:
# import Translator as T
# import SentimentAnalyzer as SA


def HasValidPrice(item):
  priceStr = str(item.get("price", "")).strip()
  match = re.search(r"[-+]?\d*\.\d+|\d+", priceStr)
  if not match:
    return False  # "N/A", "", None, no digits
  if re.match(r"\D*-\s*\.?\d", priceStr):
    return False  # negative price
  return float(match.group()) > 0  # removes 0 / 0.00


def AssignPoints(storeList):
  if not storeList:
    return storeList

  # 0. Remove products with no price, 0, negative, or N/A
  storeList = [item for item in storeList if HasValidPrice(item)]

  # 1. Parse numerical prices and pair them with original dicts
  parsedData = []
  for item in storeList:
    priceStr = str(item.get("price", "0"))
    match = re.search(r"[-+]?\d*\.\d+|\d+", priceStr)
    priceVal = float(match.group()) if match else 0.0
    parsedData.append((item, priceVal))

  # 2. Extract values and sort them
  prices = [val for _, val in parsedData]
  sortedPrices = sorted(prices)
  n = len(sortedPrices)

  if n == 0:
    return storeList

  # 3. Calculate Quartiles and IQR
  q2 = statistics.median(sortedPrices)

  mid = n // 2
  if n % 2 == 0:
    lowerHalf = sortedPrices[:mid]
    upperHalf = sortedPrices[mid:]
  else:
    lowerHalf = sortedPrices[:mid]
    upperHalf = sortedPrices[mid + 1 :]

  q1 = statistics.median(lowerHalf) if lowerHalf else q2
  q3 = statistics.median(upperHalf) if upperHalf else q2

  iqr = q3 - q1
  lowerBound = q1 - 1.5 * iqr
  upperBound = q3 + 1.5 * iqr

  # 4. Evaluate price, rating, rating amount, and reviews for each item
  for item, priceVal in parsedData:
    # --- Price Points Calculation ---
    if priceVal < lowerBound or priceVal > upperBound:
      pricePoints = 0  # Outlier
    elif priceVal <= q1:
      pricePoints = 3  # Quartile 1
    elif priceVal <= q2:
      pricePoints = 2  # Quartile 2
    elif priceVal <= q3:
      pricePoints = 1  # Quartile 3
    else:
      pricePoints = 0  # Quartile 4

    # --- Rating Points Calculation ---
    try:
      ratingVal = float(item.get("rating", 0.0))
    except (ValueError, TypeError):
      ratingVal = 0.0

    if ratingVal > 4.0:
      ratingPoints = 3
    elif ratingVal > 3.5:
      ratingPoints = 2
    elif ratingVal > 3.0:
      ratingPoints = 1
    else:
      ratingPoints = 0

    # --- Rating Amount Points Calculation ---
    try:
      ratingAmountVal = int(float(item.get("ratingAmount", 0)))
    except (ValueError, TypeError):
      ratingAmountVal = 0

    if ratingAmountVal > 1000:
      ratingAmountPoints = 3
    elif ratingAmountVal > 500:
      ratingAmountPoints = 2
    elif ratingAmountVal > 100:
      ratingAmountPoints = 1
    else:
      ratingAmountPoints = 0

    # --- Review Points Calculation ---
    reviewList = item.get("review", [])
    reviewPoints = 0
    if isinstance(reviewList, list):
      for reviewText in reviewList:
        # Calls your evaluate_review function for each review string
        text = T.translate_reviews_to_english(reviewText)
        reviewScore = SA.evaluate_review(text)
        reviewPoints += reviewScore

    # Total points combined from all metrics
    totalPoints = (
        pricePoints + ratingPoints + ratingAmountPoints + reviewPoints
    )

    # --- Update 'points' Key ---
    if "points" in item:
      item["points"] += totalPoints
    else:
      item["points"] = totalPoints

  return storeList


def SortAndColorStores(storeList):
  if not storeList:
    return []

  # Helper function to extract numerical price
  def GetPriceVal(item):
    priceStr = str(item.get("price", "0"))
    match = re.search(r"[-+]?\d*\.\d+|\d+", priceStr)
    return float(match.group()) if match else 0.0

  # Helper function to get points
  def GetPoints(item):
    return item.get("points", 0)

  items = list(storeList)
  if not items:
    return items

  # 1. Find the item with the most points (Gold / Index 0)
  goldItem = max(items, key=GetPoints)

  # 2. Find the cheapest item (Blue / Index 1)
  remainingForCheapest = [it for it in items if it != goldItem]
  if remainingForCheapest:
    cheapestItem = min(remainingForCheapest, key=GetPriceVal)
  else:
    cheapestItem = goldItem

  # 3. Identify the 5 items with the least points (Red)
  sortedByPointsAsc = sorted(items, key=GetPoints)
  redItems = set(sortedByPointsAsc[:5])

  # 4. Build the ordered list
  middleItems = [it for it in items if it != goldItem and it != cheapestItem]
  middleItems.sort(key=GetPoints, reverse=True)

  orderedList = [goldItem, cheapestItem] + middleItems

  # 5. Assign colors (Gold > Blue > Red > White)
  for item in orderedList:
    if item == goldItem:
      item["color"] = "gold"
    elif item == cheapestItem:
      item["color"] = "blue"
    elif item in redItems:
      item["color"] = "red"
    else:
      item["color"] = "white"

  return orderedList