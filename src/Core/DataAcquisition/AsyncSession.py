def GetAsyncSession():
    try:
        from curl_cffi.requests import AsyncSession  # fast HTTP with Chrome's fingerprint
        return AsyncSession

    except ImportError:  # still works without it, only slower (every page goes through the browser)
        return None