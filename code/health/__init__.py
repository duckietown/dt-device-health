from .health import run, just_check

def main():
    if 'just-check' in sys.argv:
        just_check()
    else:
        run(port=8085)

if __name__ == '__main__':
    main()
