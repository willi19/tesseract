from src import intrinsic_calibrater
import time

for i in range(0, 4):
    capturer = intrinsic_calibrater.IntrinsicCalibrater(i)
    capturer.run()
    time.sleep(1)