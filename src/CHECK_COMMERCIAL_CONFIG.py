import json
from pathlib import Path
p=Path('commercial_config.json')
d=json.loads(p.read_text(encoding='utf-8'))
assert d.get('provider') == 'lemonsqueezy'
assert d.get('license_required') is True
links=d.get('checkout_links') or {}
missing=[k for k in ('monthly','yearly','lifetime') if not str(links.get(k,'')).strip()]
print('License provider:', d.get('provider'))
print('License required:', d.get('license_required'))
if missing:
    print('WARNING: Checkout links are still blank:', ', '.join(missing))
    print('The installer can be built, but purchase buttons for blank plans will show a setup warning.')
else:
    print('Checkout links: OK')
print('Commercial config check OK')
