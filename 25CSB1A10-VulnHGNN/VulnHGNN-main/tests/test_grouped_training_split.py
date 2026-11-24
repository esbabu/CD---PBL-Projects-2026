import unittest
from pathlib import Path

from src.train_pyg import split_by_source_file


class GroupedTrainingSplitTests(unittest.TestCase):
    def test_source_file_groups_do_not_cross_splits(self):
        graph_paths = [
            Path("alpha__main.pt"),
            Path("alpha__helper.pt"),
            Path("beta__main.pt"),
            Path("gamma__main.pt"),
            Path("gamma__helper.pt"),
            Path("delta__main.pt"),
            Path("epsilon__main.pt"),
        ]

        train, validation, test, sources = split_by_source_file(graph_paths, seed=7)

        self.assertFalse(set(sources["train"]) & set(sources["validation"]))
        self.assertFalse(set(sources["train"]) & set(sources["test"]))
        self.assertFalse(set(sources["validation"]) & set(sources["test"]))
        self.assertEqual(sorted(train + validation + test), list(range(len(graph_paths))))

    def test_requires_at_least_three_source_files(self):
        with self.assertRaisesRegex(ValueError, "At least three distinct source files"):
            split_by_source_file([Path("one__main.pt"), Path("two__main.pt")])


if __name__ == "__main__":
    unittest.main()
