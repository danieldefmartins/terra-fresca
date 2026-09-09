# Terra Fresca project workflow

Every new fruit or vegetable must have its own product detail page when it is added to the homepage or catalog. Follow the existing produce page structure: varieties, Brazilian growing regions, availability, handling notes, organic status, volume/packing and inquiry links.

Research the agronomy for each new product using primary sources such as Embrapa, IAC, CEAGESP or official agricultural statistics. Record supporting links in `produce/data.py` and render them on the product page. Do not infer Terra Fresca's stock, best sellers, packing formats, certifications or destination eligibility from national production data; keep unconfirmed commercial details on request. Use availability prose when a reliable monthly calendar is unavailable.

Edit `index.src.html`, not generated `index.html`. Product content belongs in `produce/data.py`; templates belong in `buildproduce.py`. Reuse an existing dedicated product/type page where appropriate.

After product additions, run `python3 buildproduce.py`, `python3 build.py`, and `python3 buildblog.py` (the last refreshes the sitemap). Verify every new carousel link, page image and expected information section, and check desktop/mobile browsing. Homepage carousel autoplay continues during hover and vertical page scrolling. Only arrow navigation, horizontal wheel/swipe input, or keyboard arrow navigation stops autoplay. Vertical input must continue to scroll the page vertically. Touching and dragging the globe rotates only the globe; gestures outside its circular hit area scroll the page normally.

Language switching is shared in `scripts/languages.js` and `scripts/languages.css`, loaded by all three HTML builders. It uses on-demand automatic translation through GTranslate, not separate indexed language URLs. Keep the language selector on every new public page, preserve brand names and contact addresses, and verify Arabic text direction without reversing the carousel or animation coordinates. Check language switching, remembered choice on product navigation, return to English, and provider failure recovery after changes.
