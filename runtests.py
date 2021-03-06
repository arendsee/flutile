#!/usr/bin/env python3

import flutile.functions as f
import unittest
import datetime
import sys


class TestIndexedAADiff(unittest.TestCase):
    def test_gapped_indices(self):
        self.assertEqual(f.gapped_indices("ATG"), ["1", "2", "3"])
        self.assertEqual(f.gapped_indices("--ATG"), ["-2", "-1", "1", "2", "3"])
        self.assertEqual(
            f.gapped_indices("--ATG--"), ["-2", "-1", "1", "2", "3", "3+1", "3+2"]
        )
        self.assertEqual(
            f.gapped_indices("--A--T-G--"),
            ["-2", "-1", "1", "1+1", "1+2", "2", "2+1", "3", "3+1", "3+2"],
        )
        self.assertEqual(f.gapped_indices("---"), ["-3", "-2", "-1"])

    #  def test_indexed_aa_diff_table(self):
    #      #  --GA--T--   index sequence
    #      #  AAT-GGTTT   reference sequence
    #      #  AATTGGATT   a compared sequence
    #      #  -------------------------------
    #      #  Site   Ref   S1
    #      #  -2     A
    #      #  -1     A
    #      #  1      T
    #      #  2      -     T
    #      #  2+1    G     T
    #      #  2+2    G
    #      #  3      T     G
    #      #  3+1    T
    #      #  3+2    T
    #      simple = [("Ind", "--GA--T--"), ("Ref", "AAT-GGTTT"),  ("S1", "AATTGGATT")]
    #      self.assertEqual(f.inexed_aa_diff_table(simple),
    #          (   ["Site", "Ref", "S1"],
    #            [
    #              [ "-2" , "A", ""  ],
    #              [ "-1" , "A", ""  ],
    #              [ "1"  , "T", ""  ],
    #              [ "2"  , "-", "T" ],
    #              [ "2+1", "G", "T" ],
    #              [ "2+2", "G", ""  ],
    #              [ "3"  , "T", "A" ],
    #              [ "3+1", "T", ""  ]
    #              [ "3+2", "T", ""  ]
    #            ]
    #          )


class TestParsers(unittest.TestCase):
    def test_aadiff(self):
        simple_seqs = [("A", "AAAAA"), ("B", "TAAAA"), ("C", "TAAAA"), ("D", "TAAAC")]
        self.assertEqual(
            list(f.aadiff_table(simple_seqs)),
            [
                ["site", "A", "B", "C", "D"],
                ["1", "A", "T", "T", "T"],
                ["5", "A", "", "", "C"],
            ],
        )

    def test_pident(self):
        self.assertEqual(f.pident("AAAAAAAAAA", "AAAAAAAAAA"), 1.0)
        self.assertEqual(f.pident("AAAAAAAAAA", "AAAAAAAAAT"), 0.9)
        self.assertEqual(f.pident("AAAAAA--AAAA", "AAAAAG--AAAT"), 0.8)
        # No ungapped aligned region
        self.assertEqual(f.pident("----AAAA", "AAAA----"), 0)
        # An error is raised if the sequences are not of equal length
        self.assertRaises(f.InputError, f.pident, "AAAAAAAAAA", "AAA")

    def test_parseOutDate(self):
        self.assertEqual(
            f.parseOutDate("ladida 2019-01-01 fodidu"), datetime.date(2019, 1, 1)
        )

        # extracts the FIRST date that is observed (is this really what I want?)
        self.assertEqual(
            f.parseOutDate("ladida 2019-01-01 fodidu 2018-02-02"),
            datetime.date(2019, 1, 1),
        )

    def test_components(self):
        self.assertEqual(f.components([]), [])
        self.assertEqual(f.components([(1, 2)]), [{1, 2}])
        self.assertEqual(f.components([(1, 2), (2, 3), (4, 5)]), [{1, 2, 3}, {4, 5}])
        self.assertEqual(
            f.components([(1, 2), (2, 3), (4, 5), (1, 5)]), [{1, 2, 3, 4, 5}]
        )
        self.assertEqual(
            f.components([(1, 2), (2, 3), (4, 5), (5, 1)]), [{1, 2, 3, 4, 5}]
        )
        self.assertEqual(
            f.components([(1, 2), (6, 7), (2, 3), (4, 5), (5, 1), (7, 8)]),
            [{1, 2, 3, 4, 5}, {6, 7, 8}],
        )

    def test_represent(self, maxDiff=300):
        fasta = [
            ("A|2019-06-01", "AAAAA"),
            ("B|2019-06-06", "AAAAA"),
            ("C|2019-06-06", "TTAAA"),
            ("D|2018-06-06", "AAAAA"),
        ]
        g, a = f.represent(fasta, max_day_sep=5, min_pident_sep=1.0, same_state=False)
        b = fasta[1:]
        self.assertEqual(sorted(a), b)

    def test_represent_states(self, maxDiff=300):
        fasta = [
            ("A|Iowa|2019-06-01", "AAAAA"),
            ("B|Iowa|2019-06-06", "AAAAA"),
            ("C|Iowa|2019-06-06", "TTAAA"),
            ("D|Iowa|2018-06-06", "AAAAA"),
        ]
        g, a = f.represent(fasta, max_day_sep=5, min_pident_sep=1.0, same_state=True)
        b = fasta[1:]
        self.assertEqual(sorted(a), b)

        fasta = [
            ("A|Iowa|2019-06-01", "AAAAA"),
            ("B|Nebraska|2019-06-06", "AAAAA"),
            ("C|Iowa|2019-06-06", "TTAAA"),
            ("D|Iowa|2018-06-06", "AAAAA"),
        ]
        g, a = f.represent(fasta, max_day_sep=5, min_pident_sep=1.0, same_state=True)
        self.assertEqual(sorted(a), fasta)


if __name__ == "__main__":
    unittest.main()
