SCRIPT = python ../scripts/translate.py ../it

pickup:
	for d in ??; do python ../scripts/$@.py $$d/*/*.xml > $$d/error.txt; done

translate:

_done:
	$(SCRIPT) ar Arabic
	$(SCRIPT) bg Bulgarian
	$(SCRIPT) bn Bengali
	$(SCRIPT) cs Czech
	$(SCRIPT) da Danish
	$(SCRIPT) de German
	$(SCRIPT) el "Modern Greek"
	$(SCRIPT) en English
	$(SCRIPT) eo "English and Esperanto" --no-retry # unstable
	$(SCRIPT) es Spanish
	$(SCRIPT) et Estonian
	$(SCRIPT) fi Finnish
	$(SCRIPT) fr French
	$(SCRIPT) gv Manx # unstable
	$(SCRIPT) he Hebrew
	$(SCRIPT) hi Hindi
	$(SCRIPT) hr Croatian
	$(SCRIPT) hu Hungarian
	$(SCRIPT) ia Interlingua --need-space # unstable
	$(SCRIPT) id Indonesian
	$(SCRIPT) ja Japanese
	$(SCRIPT) ko Korean
	$(SCRIPT) lt Lithuanian
	$(SCRIPT) lv Latvian
	$(SCRIPT) nl Dutch
	$(SCRIPT) no Norwegian
	$(SCRIPT) pl Polish
	$(SCRIPT) pt Portuguese
	$(SCRIPT) ro Romanian
	$(SCRIPT) ru Russian
	$(SCRIPT) sk Slovak
	$(SCRIPT) sl Slovene
	$(SCRIPT) sr "Serbian (Latin)"
	$(SCRIPT) sv Swedish
	$(SCRIPT) sw Swahili
	$(SCRIPT) th Thai
	$(SCRIPT) tr Turkish
	$(SCRIPT) uk Ukrainian
	$(SCRIPT) vi Vietnamese
	$(SCRIPT) zh Chinese

_error:
	$(SCRIPT) af Afrikaans
	$(SCRIPT) am Amharic
	$(SCRIPT) be Belarusian
	$(SCRIPT) ca Catalan
	$(SCRIPT) cy Welsh
	$(SCRIPT) eu Basque
	$(SCRIPT) fa Persian
	$(SCRIPT) ga Irish
	$(SCRIPT) gd "Scottish Gaelic"
	$(SCRIPT) gu Gujarati
	$(SCRIPT) hy Armenian
	$(SCRIPT) is Icelandic
	$(SCRIPT) ka Georgian
	$(SCRIPT) km Khmer
	$(SCRIPT) kw Cornish # unstable
	$(SCRIPT) mk Macedonian
	$(SCRIPT) mn Mongolian
	$(SCRIPT) mr Marathi
	$(SCRIPT) ms Malay
	$(SCRIPT) mt Maltese
	$(SCRIPT) my Burmese
	$(SCRIPT) ne Nepali
	$(SCRIPT) pa Punjabi
	$(SCRIPT) rw Kinyarwanda
	$(SCRIPT) sq Albanian
	$(SCRIPT) ta Tamil
	$(SCRIPT) tl Tagalog
	$(SCRIPT) ur Urdu
	$(SCRIPT) yi Yiddish

check:
	grep developers.generativeai.google */*/*.xml || true
