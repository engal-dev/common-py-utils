import argparse
from string_utils import are_strings_similar

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testa la funzione are_strings_similar.")
    parser.add_argument("str1", type=str, help="Prima stringa da confrontare")
    parser.add_argument("str2", type=str, help="Seconda stringa da confrontare")
    parser.add_argument("--threshold", type=float, default=0.85, help="Soglia di similarità (default: 0.85)")
    args = parser.parse_args()

    is_similar, score = are_strings_similar(args.str1, args.str2, args.threshold)
    print(f"Simili: {is_similar} (score: {score:.3f}, threshold: {args.threshold})") 