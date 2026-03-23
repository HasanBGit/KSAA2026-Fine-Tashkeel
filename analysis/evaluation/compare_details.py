#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Detailed comparison tool for Arabic diacritization
Shows exactly where predictions differ from references
"""

import argparse
import re
import unicodedata


ARABIC_DIACRITICS = [
    '\u064B', '\u064C', '\u064D', '\u064E', '\u064F', 
    '\u0650', '\u0651', '\u0652', '\u0653', '\u0654',
    '\u0655', '\u0656', '\u0657', '\u0658', '\u0670'
]

ARABIC_LETTERS = set([
    'ا', 'أ', 'إ', 'آ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز',
    'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن',
    'ه', 'و', 'ي', 'ى', 'ة', 'ء', 'ئ', 'ؤ'
])


def remove_diacritics(text):
    pattern = '[' + ''.join(ARABIC_DIACRITICS) + ']'
    return re.sub(pattern, '', text)


def normalize_text(text):
    text = unicodedata.normalize('NFC', text)
    text = text.replace('\u0640', '')
    return text


def extract_letter_diacritic_pairs(text):
    pairs = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if char not in ARABIC_LETTERS:
            i += 1
            continue
        
        diacritics = []
        j = i + 1
        while j < len(text) and text[j] in ARABIC_DIACRITICS:
            diacritics.append(text[j])
            j += 1
        
        pairs.append((char, ''.join(diacritics)))
        i = j
    
    return pairs


def compare_words(pred_word, ref_word, word_idx):
    """Compare a single word and return detailed differences"""
    pred_pairs = extract_letter_diacritic_pairs(pred_word)
    ref_pairs = extract_letter_diacritic_pairs(ref_word)
    
    if len(pred_pairs) != len(ref_pairs):
        return None, None, None
    
    errors = []
    correct = 0
    total = len(pred_pairs)
    
    for i, ((pred_letter, pred_diac), (ref_letter, ref_diac)) in enumerate(zip(pred_pairs, ref_pairs)):
        if pred_letter != ref_letter:
            return None, None, None
        
        if pred_diac != ref_diac:
            # Get diacritic names
            pred_name = get_diacritic_name(pred_diac)
            ref_name = get_diacritic_name(ref_diac)
            errors.append({
                'position': i,
                'letter': pred_letter,
                'pred_diac': pred_diac,
                'ref_diac': ref_diac,
                'pred_name': pred_name,
                'ref_name': ref_name
            })
        else:
            correct += 1
    
    return correct, total, errors


def get_diacritic_name(diac):
    """Get human-readable name for diacritic(s)"""
    if not diac:
        return "None"
    
    names = {
        '\u064B': 'Fathatan',
        '\u064C': 'Dammatan',
        '\u064D': 'Kasratan',
        '\u064E': 'Fatha',
        '\u064F': 'Damma',
        '\u0650': 'Kasra',
        '\u0651': 'Shadda',
        '\u0652': 'Sukun',
        '\u0670': 'Dagger Alif',
    }
    
    parts = []
    for d in diac:
        parts.append(names.get(d, f'U+{ord(d):04X}'))
    
    return '+'.join(parts)


def analyze_line(pred_line, ref_line, line_idx, show_details=True):
    """Analyze a single line"""
    pred_line = normalize_text(pred_line.strip().lstrip('\ufeff'))
    ref_line = normalize_text(ref_line.strip().lstrip('\ufeff'))
    
    pred_base = remove_diacritics(pred_line)
    ref_base = remove_diacritics(ref_line)
    
    if pred_base != ref_base:
        return None
    
    pred_words = pred_line.split()
    ref_words = ref_line.split()
    
    if len(pred_words) != len(ref_words):
        return None
    
    line_stats = {
        'total_words': len(pred_words),
        'correct_words': 0,
        'incorrect_words': 0,
        'total_letters': 0,
        'correct_letters': 0,
        'word_errors': []
    }
    
    for word_idx, (pred_word, ref_word) in enumerate(zip(pred_words, ref_words)):
        correct, total, errors = compare_words(pred_word, ref_word, word_idx)
        
        if correct is None:
            continue
        
        line_stats['total_letters'] += total
        line_stats['correct_letters'] += correct
        
        if errors:
            line_stats['incorrect_words'] += 1
            if show_details:
                line_stats['word_errors'].append({
                    'word_idx': word_idx,
                    'pred_word': pred_word,
                    'ref_word': ref_word,
                    'errors': errors
                })
        else:
            line_stats['correct_words'] += 1
    
    return line_stats


def main():
    parser = argparse.ArgumentParser(description='Detailed comparison of Arabic diacritization')
    parser.add_argument('-p', '--pred', required=True, help='Path to predictions file')
    parser.add_argument('-r', '--ref', required=True, help='Path to reference file')
    parser.add_argument('-n', '--num-examples', type=int, default=5, 
                       help='Number of error examples to show (default: 5)')
    parser.add_argument('-l', '--line', type=int, help='Show details for specific line number')
    args = parser.parse_args()
    
    with open(args.pred, 'r', encoding='utf-8') as f:
        pred_lines = f.readlines()
    
    with open(args.ref, 'r', encoding='utf-8') as f:
        ref_lines = f.readlines()
    
    print("\n" + "="*80)
    print("DETAILED DIACRITIZATION COMPARISON")
    print("="*80)
    print(f"Predictions: {args.pred}")
    print(f"Reference:   {args.ref}")
    print(f"Total lines: {len(pred_lines)}")
    print("="*80)
    
    # If specific line requested
    if args.line:
        line_idx = args.line - 1
        if 0 <= line_idx < len(pred_lines):
            print(f"\n📍 LINE {args.line} DETAILED ANALYSIS")
            print("-" * 80)
            stats = analyze_line(pred_lines[line_idx], ref_lines[line_idx], line_idx, show_details=True)
            
            if stats:
                print(f"Words: {stats['correct_words']}/{stats['total_words']} correct")
                print(f"Letters: {stats['correct_letters']}/{stats['total_letters']} correct")
                print(f"Accuracy: {stats['correct_letters']/stats['total_letters']*100:.1f}%")
                
                if stats['word_errors']:
                    print(f"\n❌ ERRORS ({len(stats['word_errors'])} words with errors):")
                    for we in stats['word_errors']:
                        print(f"\n  Word {we['word_idx']+1}:")
                        print(f"    Pred: {we['pred_word']}")
                        print(f"    Ref:  {we['ref_word']}")
                        print(f"    Errors:")
                        for err in we['errors']:
                            print(f"      Letter '{err['letter']}' (pos {err['position']}): "
                                  f"{err['pred_name']} → {err['ref_name']}")
        return
    
    # Overall analysis
    total_stats = {
        'total_words': 0,
        'correct_words': 0,
        'total_letters': 0,
        'correct_letters': 0,
        'error_examples': []
    }
    
    for line_idx, (pred_line, ref_line) in enumerate(zip(pred_lines, ref_lines)):
        stats = analyze_line(pred_line, ref_line, line_idx, show_details=(line_idx < 10))
        
        if stats is None:
            continue
        
        total_stats['total_words'] += stats['total_words']
        total_stats['correct_words'] += stats['correct_words']
        total_stats['total_letters'] += stats['total_letters']
        total_stats['correct_letters'] += stats['correct_letters']
        
        # Collect error examples
        if len(total_stats['error_examples']) < args.num_examples and stats['word_errors']:
            for we in stats['word_errors'][:1]:  # One per line
                total_stats['error_examples'].append({
                    'line': line_idx + 1,
                    **we
                })
    
    # Print summary
    print("\n📊 OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total words:    {total_stats['total_words']:,}")
    print(f"Correct words:  {total_stats['correct_words']:,} ({total_stats['correct_words']/total_stats['total_words']*100:.1f}%)")
    print(f"Total letters:  {total_stats['total_letters']:,}")
    print(f"Correct letters: {total_stats['correct_letters']:,} ({total_stats['correct_letters']/total_stats['total_letters']*100:.1f}%)")
    
    # Print examples
    if total_stats['error_examples']:
        print(f"\n❌ ERROR EXAMPLES (showing {len(total_stats['error_examples'])} of many)")
        print("-" * 80)
        
        for i, ex in enumerate(total_stats['error_examples'], 1):
            print(f"\n{i}. Line {ex['line']}, Word {ex['word_idx']+1}")
            print(f"   Pred: {ex['pred_word']}")
            print(f"   Ref:  {ex['ref_word']}")
            print(f"   Errors:")
            for err in ex['errors']:
                print(f"     • Letter '{err['letter']}': {err['pred_name']} → should be {err['ref_name']}")
    
    print("\n" + "="*80)
    print("💡 TIP: Use -l <line_number> to see detailed analysis of a specific line")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
