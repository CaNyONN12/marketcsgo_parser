from CollectData import CollectData
import asyncio


def main():
    collector = CollectData()
    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(collector.collect())


main()
