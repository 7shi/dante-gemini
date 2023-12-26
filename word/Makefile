all:

pickup:
	python ../scripts/$@.py 1-error.xml */*.xml

word:
	python ../scripts/word.py --no-retry ../it init.xml .

check:
	grep developers.generativeai.google */*.xml || true
