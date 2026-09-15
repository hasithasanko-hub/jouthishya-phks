හෙළ ජ්‍යෝතිෂ්‍ය — PHKS Creation Web Demo V4.1

මෙම package එක install නොකර browser එකෙන් test කිරීම සඳහා cloud deployment-ready build එකකි.

මෙහි fix කර ඇති ප්‍රධාන කරුණු:
1) Deep Analysis එක chart-specific dynamic කර ඇත.
2) ශක්තිමත් පැත්ත + දුර්වල/පීඩන පැත්ත + ඇතිවිය හැකි අත්දැකීම් + practical guidance පෙන්වයි.
3) එකම generic text හැම කෙනාටම නොඑන ලෙස lagna/moon/house lord/planet/aspect/dasha අනුව text වෙනස් වේ.
4) පීඩන ප්‍රතිඵල “නියත සිදුවීම්” ලෙස නොව සාම්ප්‍රදායික ජ්‍යෝතිෂ්‍ය ප්‍රවණතා ලෙස පෙන්වයි.
5) Cloud server startup bug fix: සියලු final engine overrides load වූ පසු පමණක් server start වේ.
6) 0.0.0.0 + PORT environment support add කර ඇත.
7) Render/Docker deployment files add කර ඇත.
8) /api/health health check තිබේ.

Render deploy:
- ZIP එක GitHub repository එකකට upload/extract කරන්න.
- Render > New > Web Service > repository connect කරන්න.
- render.yaml / Dockerfile detect කළ පසු deploy කරන්න.
- deploy අවසානයේ https://....onrender.com link එක ලැබේ.

සටහන: Cloud demo database host restart/deploy කිරීමේදී reset විය හැක. Customer production version සඳහා persistent database/cloud account වෙනම සකස් කළ යුතුය.

V4.2: Deep Analysis diversity improved. Malefic effects are planet+house specific; sections no longer default to delay language; experience patterns vary by chart factors.
