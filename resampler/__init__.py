def resample(series, step):
    def column_get(name, series, typeconv=None):
        ans = []
        for s in series:
            if typeconv:
                ans.append(typeconv(s[name]))
            else:
                ans.append(s[name])
        return ans

    data_lf = []
    for i in range(0, len(series), step):
        hf = series[i:i + step]
        candle_new = {}

        timestamps = column_get("timestamp", hf)
        opens = column_get("open", hf, float)
        highs = column_get("high", hf, float)
        lows = column_get("low", hf, float)
        closes = column_get("close", hf, float)
        volumes = column_get("volume", hf, float)

        candle_new["timestamp"] = timestamps[0]
        candle_new["open"] = opens[0]
        candle_new["high"] = max(highs)
        candle_new["low"] = min(lows)
        candle_new["close"] = closes[-1]
        candle_new["volume"] = sum(volumes)

        data_lf.append(candle_new)

    return data_lf
