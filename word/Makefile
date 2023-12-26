all:

fix:
	python ../scripts/word-fix.py

pickup:
	python ../scripts/pickup.py 1-error.xml */*.xml

word:
	python ../scripts/word.py --no-retry ../it init.xml .

check:
	grep developers.generativeai.google */*.xml || true
