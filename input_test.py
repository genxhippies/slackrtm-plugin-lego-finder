import sys
from lego_finder import _process_text

if __name__ == "__main__":
    while True:
        line = sys.stdin.readline().rstrip('\n')
        print "----"
        _process_text(line, "Test")
        print "----"
