from .bot import main


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting the Meeting Bot. Goodbye!")
