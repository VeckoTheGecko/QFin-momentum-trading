from unittest import TestCase
import pandas as pd

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Adding the above directory to the path

import breakout_lib as bl

df = pd.read_csv("data/USDT_ETH.csv")

df = pd.DataFrame(
    {
        'date':[1,2,3,4,5,6,7,8,9,10],
        'low': [1,2,3,4,5,6,7,8,9,10],
        'high':[1,2,3,4,5,6,7,8,9,10],
        'open':[1,2,3,4,5,6,7,8,9,10],
        'close':[1,2,3,4,5,6,7,8,9,10],
        'volume':[1,2,3,4,5,6,7,8,9,10],
        }
    )

class test_calcs(TestCase):
    def test_support(self):
        self.assertEqual(bl.return_support(df,5), 6)
        self.assertEqual(bl.return_support(df,4), 7)
        self.assertEqual(bl.return_support(df,3), 8)

    def test_resistance(self):
        self.assertEqual(bl.return_resistance(df,5), 10)
        self.assertEqual(bl.return_resistance(df,4), 10)
        self.assertEqual(bl.return_resistance(df,3), 10)

