හෙළ ජ්‍යෝතිෂ්‍ය V3.4 — TRIAL + PAID COMMERCIAL DESKTOP
=========================================================

CUSTOMER EXPERIENCE
-------------------
Customer ට Python install කරන්න ඕන නැහැ.
ඔහු/ඇය Hela_Jyotishya_Setup_v34_Trial_Paid.exe එක install කරලා Desktop shortcut එකෙන් software එක open කරනවා.

පළමු වර open කළාම:
1) දින 14 නොමිලේ අත්හදා බලන්න
2) දැනටමත් ගෙවූ License Key එකක් තිබේ නම් සක්‍රීය කරන්න
3) Monthly / Yearly / Lifetime plan එකක් මිලදී ගන්න

TRIAL
-----
- Default trial: 14 days
- commercial_config.json -> trial_days වෙනස් කරලා 7 / 14 / 30 කරන්න පුළුවන්.
- Trial එක PC/device එකට බැඳී ඇත.
- Uninstall + reinstall කළාම Windows user registry record එක නිසා සාමාන්‍යයෙන් trial එක නැවත ආරම්භ වෙන්නේ නැහැ.
- Computer date/time පසුපසට වෙනස් කළොත් basic clock rollback check එකක් තියෙනවා.

IMPORTANT:
මෙය local anti-reset protection එකක්. ගොඩක් customers ට commercial scale එකෙන් sell කරන final production version එකේ trial status cloud backend එකෙන් verify කිරීම තවත් ශක්තිමත් කරයි.

PAID
----
- Lemon Squeezy License API
- Monthly / Yearly / Lifetime
- Device activation
- Offline grace days: 3
- Expired/invalid license එකෙන් paid access නවතී.

PAYMENT SETUP
-------------
commercial_config.json තුළ:
checkout_links.monthly
checkout_links.yearly
checkout_links.lifetime
වලට Lemon Squeezy checkout URLs paste කරන්න.

CUSTOMER PC එකට API SECRET KEY එකක් දාන්න එපා.

SETUP.EXE BUILD කරන විදිහ
-------------------------
Developer Windows PC එකේ පමණක් BUILD_INSTALLER.cmd run කරන්න.
Developer PC එකට Python + Inno Setup අවශ්‍ය වෙන්න පුළුවන්.
CUSTOMER PC එකට ඒ දෙකෙන් එකක්වත් අවශ්‍ය නැහැ.

Build complete වුණාම release folder එකේ:
Hela_Jyotishya_Setup_v34_Trial_Paid.exe

Customerට දෙන්නේ ඒ Setup.exe එක විතරයි.

NOTE
----
Trial එකෙන් paid plan එකට ගියාම License Key එක Activate කරන්න. Paid license active වුණාම paid validation එක priority වෙනවා.
