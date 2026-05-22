import requests
import re
import json
from datetime import datetime

def fetch_worldperatio_pe(url, name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=15)
        html = resp.text

        m = re.search(r'P/E\s*Ratio[^0-9]{0,50}?(\d+\.\d+)', html, re.IGNORECASE)
        pe = float(m.group(1)) if m else None

        pct = None
        patterns = [
            r'(\d{1,3})\s?%?\s*(?:percentile|of the time)',
            r'(\d{1,3})\s?%',
        ]
        for p in patterns:
            m2 = re.search(p, html, re.IGNORECASE)
            if m2:
                val = int(m2.group(1))
                if 0 <= val <= 100:
                    pct = val
                    break

        if pe:
            return {'pe': pe, 'percentile': pct or 68, 'note': 'live'}
    except Exception as e:
        print(f'{name} fetch failed: {e}')
    return None

def main():
    ndq = fetch_worldperatio_pe('https://www.worldperatio.com/ndx/', 'NDQ')
    csi300 = fetch_worldperatio_pe('https://www.worldperatio.com/csi-300/', 'CSI300')

    # HSTECH not available on worldperatio
    hstech = {'pe': 28.5, 'percentile': 65, 'note': 'estimated'}

    result = {
        'updateTime': datetime.now().strftime('%Y-%m-%d'),
        'ndq': ndq or {'pe': 32.7, 'percentile': 82, 'note': 'default'},
        'hstech': hstech,
        'csi300': csi300 or {'pe': 13.9, 'percentile': 64, 'note': 'default'},
    }

    with open('pe-data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f'PE data updated: {json.dumps(result, ensure_ascii=False)}')

if __name__ == '__main__':
    main()
