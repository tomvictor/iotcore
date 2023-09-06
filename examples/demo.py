from iotcore import IotCore
def main():
    iot = IotCore()
    iot.start_broker()
    # iot.background_loop_forever()

    while True:
        pass


if __name__ == "__main__":
    main()
