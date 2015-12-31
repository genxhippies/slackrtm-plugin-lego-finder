import sys
from lego_finder import process_text

while True:
    line = sys.stdin.readline().rstrip('\n')
    process_text(line, "Test")
