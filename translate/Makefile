SCRIPT = python ../scripts/translate.py ../it

translate:
	$(SCRIPT) gv Manx # unstable

_done:
	$(SCRIPT) ru Russian
	$(SCRIPT) uk Ukrainian
	$(SCRIPT) cs Czech
	$(SCRIPT) sk Slovak
	$(SCRIPT) hr Croatian
	$(SCRIPT) pl Polish
	$(SCRIPT) he Hebrew
	$(SCRIPT) ar Arabic
	$(SCRIPT) sv Swedish
	$(SCRIPT) da Danish
	$(SCRIPT) sw Swahili
	$(SCRIPT) th Thai
	$(SCRIPT) tr Turkish
	$(SCRIPT) hu Hungarian
	$(SCRIPT) fi Finnish
	$(SCRIPT) sl Slovene
	$(SCRIPT) id Indonesian
	$(SCRIPT) vi Vietnamese
	$(SCRIPT) bn Bengali
	$(SCRIPT) lv Latvian
	$(SCRIPT) lt Lithuanian
	$(SCRIPT) ia Interlingua --need-space # unstable
	$(SCRIPT) ro Romanian
	$(SCRIPT) nl Dutch
	$(SCRIPT) de German
	$(SCRIPT) no Norwegian
	$(SCRIPT) sr "Serbian (Latin)"
	$(SCRIPT) bg Bulgarian
	$(SCRIPT) pt Portuguese
	$(SCRIPT) es Spanish
	$(SCRIPT) fr French
	$(SCRIPT) et Estonian
	$(SCRIPT) ko Korean
	$(SCRIPT) zh Chinese
	$(SCRIPT) ja Japanese
	$(SCRIPT) hi Hindi
	$(SCRIPT) el "Modern Greek"
	$(SCRIPT) en English
	$(SCRIPT) eo "English and Esperanto" --no-retry # unstable

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
