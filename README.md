# gov-il-rss-telegram

<div dir="rtl">

העברת עדכוני RSS מאתר הממשלה (<a href="https://www.gov.il">gov.il</a>) לצ'אט טלגרם באמצעות GitHub Actions.

## רוב קוראי ה-RSS לא עובדים עם ערוצי RSS של gov.il

אתר gov.il מוגן על ידי מערכת ההגנה של Cloudflare, שמשתמשת ב-TLS fingerprinting כדי לחסום לקוחות HTTP שאינם דפדפנים. כלים סטנדרטיים כמו <code>curl</code>, <code>wget</code>, Python <code>requests</code> ורוב קוראי ה-RSS מקבלים שגיאת 403. זוהי <a href="https://openrss.org/blog/using-cloudflare-on-your-website-could-be-blocking-rss-users">בעיה ידועה</a> שמשפיעה על קוראי RSS רבים מול אתרים המוגנים על ידי Cloudflare.

הפרויקט הזה עוקף את החסימה באמצעות <a href="https://github.com/lexiforest/curl-impersonate">curl-impersonate</a> (דרך <a href="https://github.com/lexiforest/curl_cffi">curl_cffi</a>) שמחקה את חתימת ה-TLS של דפדפן Chrome. למרות שהפרויקט נבנה עבור gov.il, הוא יכול לעבוד עם כל ערוץ RSS שמוגן על ידי Cloudflare.

</div>

## Setup

### 1. Fork this repository

### 2. Create a Telegram bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive
4. Add the bot to your target chat/group
5. To get the chat ID, send a message in the chat, then visit:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Look for `"chat":{"id":...}` in the response.

<div dir="rtl">

### 3. איתור כתובות RSS

לכל משרד ממשלתי יש דף RSS בכתובת:

<pre dir="ltr">https://www.gov.il/he/departments/&lt;שם-המשרד&gt;/RSS</pre>

לדוגמה:
<ul>
<li>משרד הבריאות: <a href="https://www.gov.il/he/departments/ministry_of_health/RSS">https://www.gov.il/he/departments/ministry_of_health/RSS</a></li>
<li>ועדת הבחירות המרכזית: <a href="https://www.gov.il/he/departments/central-elections-committee/RSS">https://www.gov.il/he/departments/central-elections-committee/RSS</a></li>
</ul>

רשימת כל המשרדים זמינה בכתובת <a href="https://www.gov.il/he/departments/">https://www.gov.il/he/departments/</a> — הוסיפו <code>/RSS</code> לכתובת של כל משרד כדי לראות את הערוצים הזמינים.

כל דף RSS מציג ערוצי תוכן (פרסומים, חדשות, שירותים, התראות ועוד). דוגמאות לערוצים ממשרדים שונים:
<ul>
<li><a href="https://www.gov.il/he/api/PublicationApi/rss/503be068-3051-4dc0-bc61-65f0b33f0570">פרסומים — משרד התקשורת</a></li>
<li><a href="https://www.gov.il/he/api/ServiceApi/rss/f41159c1-7867-41c3-bc0a-cbfe0da1bb1a">שירותים — משרד האוצר</a></li>
<li><a href="https://www.gov.il/he/api/NewsApi/rss/6cbf57de-3976-484a-8666-995ca17899ec">חדשות — משרד החוץ</a></li>
<li><a href="https://www.gov.il/he/api/PublicationApi/rss/26857f24-4eaa-4032-a39d-5dc66d374ee3">פרסומים — ועדת הבחירות המרכזית</a></li>
<li><a href="https://www.gov.il/he/api/NewsApi/rss/e744bba9-d17e-429f-abc3-50f7a8a55667">חדשות — משרד ראש הממשלה</a></li>
</ul>

לחצו קליק ימני על שם הערוץ בדף ה-RSS של המשרד והעתיקו את כתובת הקישור.

</div>

### 4. Configure repository secrets

Go to your fork's **Settings > Secrets and variables > Actions** and add:

| Secret | Value |
|--------|-------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHAT_ID` | The target chat/group ID |
| `RSS_URLS` | Space-separated list of RSS feed URLs |

Example `RSS_URLS` value:
```
https://www.gov.il/he/api/PublicationApi/rss/104cb0f4-d65a-4692-b590-94af928c19c0 https://www.gov.il/he/api/NewsApi/rss/104cb0f4-d65a-4692-b590-94af928c19c0
```

### 5. Enable the workflow

Go to the **Actions** tab in your fork and enable workflows. The feed check runs every 6 hours by default. You can also trigger it manually via "Run workflow".

## How it works

1. GitHub Actions runs on a cron schedule
2. The script fetches each RSS feed using `curl_cffi` with Chrome TLS impersonation
3. New items are detected by comparing GUIDs against a cached list
4. New items are sent to Telegram with title, description, and link
5. Sent GUIDs are cached between runs to avoid duplicates

## Customization

To change the check frequency, edit the cron expression in `.github/workflows/gov-il-rss.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```
