import math
import statistics
import re

from src.Core import Settings
from src.Core.DataAnalysis import RelevanceAnalysis as RA
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


# ------------------------------------------------------------------ price clusters
# Accessories and unrelated products usually sit far away from the real
# product's price, so they form their own small clusters. The scoring below
# is anchored to the dominant cluster instead of the whole mixed set.
# The cluster factors live in Settings.py and can be overridden from the
# command line (-c / --cluster, --minFactor, --maxFactor).

# ------------------------------------------------------------------ value score
# A continuous "best value" score instead of coarse buckets:
#   value = quality / priceRatio
# quality is a Wilson lower bound of the star rating (a 5.0 with 1 review
# never beats a 4.7 with 5000 reviews), priceRatio is the price divided by
# the cheapest price of the main cluster. Unrated products get a quality
# floor so they still rank sensibly (by price) when no store exposes ratings.
QUALITY_FLOOR = 0.5        # value given to products without any rating
REVIEW_PENALTY_FACTOR = 0.05  # subtracted per average review severity (0..3)


def WilsonLowerBound(rating, count):
  """Lower bound of the Wilson score interval for a 0-5 star rating with
  'count' ratings, at 95% confidence. This is the standard way to rank rated
  items: it punishes ratings backed by very few reviews."""
  try:
    ratingVal = float(rating)
  except (ValueError, TypeError):
    return 0.0
  if ratingVal <= 0:
    return 0.0

  try:
    countVal = int(float(count))
  except (ValueError, TypeError):
    countVal = 0
  if countVal <= 0:
    return 0.0

  p = max(0.0, min(1.0, ratingVal / 5.0))
  n = countVal
  z = 1.96  # 95% confidence
  return (p + z * z / (2 * n) - z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / (1 + z * z / n)


def PriceClusters(prices):
  """Splits sorted prices into clusters separated by large jumps."""
  prices = sorted(prices)
  clusters = [[prices[0]]]
  for price in prices[1:]:
    if price > clusters[-1][-1] * Settings.CLUSTER_GAP_FACTOR:
      clusters.append([price])
    else:
      clusters[-1].append(price)
  return clusters


def KeepDominantSubgroup(familyItems):
  """Keeps only the family items that share the family's dominant extra word.

  When the query's accessory word matches nothing (English "cover" vs Turkish
  "kılıf"), the best-matching family can mix several accessory types with
  similar prices - covers AND screen protectors. The word that appears in
  more than half of the family's names defines what the user almost
  certainly meant, so items without it are marked with familyMember = False
  and later removed by AssignPoints. Works in any language, with no word
  lists."""
  names = [" ".join(RA.NormalizeRuns(item.get("productName") or item.get("pageTitle") or ""))
           for item, _ in familyItems]

  candidates = set()
  for name in names:
    for run in name.split():
      if len(run) >= 2 and not run.isdigit():
        candidates.add(run)

  if not candidates:
    return familyItems

  total = len(familyItems)
  dominantTokens = [token for token in candidates
                    if sum(1 for name in names if token in name) > total / 2]
  if not dominantTokens:
    return familyItems

  kept = []
  for index, (item, val) in enumerate(familyItems):
    if all(token in names[index] for token in dominantTokens):
      kept.append((item, val))
    else:
      item["familyMember"] = False  # removed later by AssignPoints
  return kept


def DominantPriceCluster(parsedData):
  """Returns the price list of the product family the user searched for.

  Among the clusters that contain the best name-match (the "relevance" key
  set by RelevanceAnalysis.FilterProducts):
    - clusters clearly cheaper than the priciest best matches are treated as
      accessories of the product and ignored,
    - among the remaining (top price band) clusters, the tightest one wins
      (the same product costs similar money everywhere, while junk is
      scattered), ties broken by the higher price,
    - the family is every best-match offer within a wide band around that
      anchor, so ALL variants of the product (storage sizes, plus/ultra
      models, different sellers) survive together.
  When the query has words that NO product matched, the user is most likely
  looking for a related accessory (whose local name differs from the query's
  word), so the largest family wins instead of the priciest.
  Falls back to the largest cluster (when it is big enough to trust) and
  returns None when prices look uniform or ambiguous."""

  prices = [val for _, val in parsedData]
  if len(prices) < 2:
    return None

  clusters = PriceClusters(prices)
  if len(clusters) < 2:
    return None  # one uniform cluster: nothing to separate

  def ClusterTightness(cluster):
    return min(cluster) / max(cluster) if len(cluster) >= 2 else 0.0

  hasRelevance = any("relevance" in item for item, _ in parsedData)
  if hasRelevance:
    bestRel = max((item.get("relevance", 0.6) for item, _ in parsedData), default=0.6)
    candidates = []
    for cluster in clusters:
      clusterValues = set(cluster)
      if any(item.get("relevance", 0.6) == bestRel for item, val in parsedData if val in clusterValues):
        candidates.append(cluster)

    if candidates:
      # accessories of the product are (much) cheaper than the product itself:
      # the anchor must come from the top price band of the best matches
      multi = [c for c in candidates if len(c) >= 2]
      priciest = max(multi, key=lambda c: statistics.median(c)) if multi else \
                 max(candidates, key=lambda c: statistics.median(c))
      priciestMedian = statistics.median(priciest)
      topBand = [c for c in candidates if statistics.median(c) >= 0.3 * priciestMedian]

      # If the query contains words that NO product matched (bestRel < 1),
      # the user is most likely looking for a RELATED item - an accessory
      # like "cover", whose local name (Turkish "kılıf") is different from
      # the query's word. In that case the expensive base product ties with
      # the accessory on relevance, and the accessory family is usually the
      # largest one in the results - so the largest family wins instead of
      # the priciest. Fully matched queries (bestRel == 1) keep the normal
      # top-price-band behavior.
      if bestRel < 1.0:
        topBand = [max(candidates, key=len)]

      anchor = max(topBand, key=lambda c: (ClusterTightness(c), statistics.median(c)))
      anchorMedian = statistics.median(anchor)

      # the family: every best-match offer close to the anchor - this keeps
      # all variants of the product alive while excluding the cheap
      # accessories around it
      familyItems = [(item, val) for item, val in parsedData
                     if item.get("relevance", 0.6) == bestRel
                     and anchorMedian * 0.3 <= val <= anchorMedian * 3.3]

      # When the query had unmatched words, the family can mix several
      # accessory types with similar prices (covers AND screen protectors).
      # The dominant word of the names defines what the user meant.
      if bestRel < 1.0 and len(familyItems) >= 3:
        familyItems = KeepDominantSubgroup(familyItems)

      if familyItems:
        return sorted(val for _, val in familyItems)
      return None

  # fallback: no relevance stamps -> the largest cluster, when it is big
  # enough to trust
  bySize = max(clusters, key=len)
  if len(bySize) >= 3 and len(bySize) >= 0.4 * len(prices):
    return bySize
  return None


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

  n = len(parsedData)
  if n == 0:
    return storeList

  # 2. When one price cluster clearly dominates, it represents the product the
  #    user actually searched for. The value score below is anchored to THAT
  #    cluster, so cheap accessories (or crazy bundles) can no longer shift the
  #    results. Items in far-away clusters are removed entirely, nearby
  #    clusters (other variants, storage sizes...) stay but get a price penalty.
  mainCluster = DominantPriceCluster(parsedData)

  if mainCluster is not None:
    mainMedian = statistics.median(mainCluster)
    keepMin, keepMax = mainMedian * Settings.KEEP_MIN_FACTOR, mainMedian * Settings.KEEP_MAX_FACTOR
    parsedData = [(item, val) for item, val in parsedData if keepMin <= val <= keepMax]
    # remove items that did not share the family's dominant word
    # (marked by DominantPriceCluster / KeepDominantSubgroup)
    parsedData = [(item, val) for item, val in parsedData if item.get("familyMember", True)]
    storeList = [item for item, _ in parsedData]
    sortedPrices = sorted(mainCluster)
  else:
    sortedPrices = sorted(val for _, val in parsedData)

  if not sortedPrices:
    return storeList

  mainValues = set(mainCluster) if mainCluster is not None else None
  clusterMin = sortedPrices[0]

  # 3. Value score: continuous blend of price position and rating quality.
  #    A higher value score = better deal. The best deal becomes gold, the
  #    cheapest stays blue, and the lowest scores become red.
  for item, priceVal in parsedData:
    # --- Price ratio (1.0 = cheapest in the main cluster) ---
    if mainValues is not None and priceVal not in mainValues:
      priceRatio = 2.0    # nearby cluster (another variant): treat as twice the price
    elif clusterMin > 0:
      priceRatio = max(1.0, priceVal / clusterMin)
    else:
      priceRatio = 1.0

    # --- Quality: Wilson lower bound of the rating (0..1) ---
    qualityScore = WilsonLowerBound(item.get("rating"), item.get("ratingAmount"))
    qualityScore = max(qualityScore, QUALITY_FLOOR)

    # --- Review sentiment penalty (0 positive .. 3 severely negative) ---
    reviewList = item.get("review", item.get("reviews", []))
    reviewPenalty = 0.0
    if isinstance(reviewList, list) and reviewList:
      try:
        translated = T.translate_reviews_to_english(reviewList)
        severities = [SA.evaluate_review(text) for text in translated
                      if isinstance(text, str) and text.strip()]
        if severities:
          reviewPenalty = REVIEW_PENALTY_FACTOR * (sum(severities) / len(severities))
      except Exception:
        reviewPenalty = 0.0

    # --- Total value ---
    valueScore = qualityScore / priceRatio - reviewPenalty

    # --- Update 'points' Key ---
    if "points" in item:
      item["points"] += valueScore
    else:
      item["points"] = valueScore

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

  # 1. Find the item with the most points (Gold) and the cheapest (Blue) -
  #    every product is then ordered strictly by its points, so the cheapest
  #    keeps the position its points earned instead of always being second.
  goldItem = max(items, key=GetPoints)
  cheapestItem = min(items, key=GetPriceVal)

  # 2. Identify the 5 items with the least points (Red), tracked by id()
  sortedByPointsAsc = sorted(items, key=GetPoints)
  redIds = {id(it) for it in sortedByPointsAsc[:5]}

  # 3. Order everything strictly by points, best to worst
  orderedList = sorted(items, key=GetPoints, reverse=True)

  # 4. Assign colors (Gold > Blue > Red > White)
  for item in orderedList:
    if item is goldItem:
      item["color"] = "gold"
    elif item is cheapestItem:
      item["color"] = "blue"
    elif id(item) in redIds:
      item["color"] = "red"
    else:
      item["color"] = "white"

  return orderedList