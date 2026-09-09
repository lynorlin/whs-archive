@echo off
echo ========================================================
echo   WOODLAND HOUSE SCHOOL ARCHIVE - AUTO UPDATER
echo ========================================================
echo.
echo [1/3] Fetching 10 Years of History (Posts, Stories, Highlights)...
echo Please wait, this may take a few minutes if there are thousands of posts.
python sync_whs_data.py

echo.
echo [2/3] Rebuilding the Website with New Data...
python build_html.py
copy /Y index.html Editorial_Brutalism_Template\template.html >nul

echo.
echo [3/3] Pushing to the Internet (Vercel)...
vercel --prod --yes

echo.
echo ========================================================
echo   UPDATE COMPLETE! The website is fully synced.
echo ========================================================
pause
