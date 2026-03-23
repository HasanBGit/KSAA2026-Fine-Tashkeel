#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyze diacritic distribution differences between predictions and ground truth
"""

from pathlib import Path
from collections import Counter
import re

# Arabic diacritics
DIACRITICS = {
    '\u064B': 'Fathatan (ً)',
    '\u064C': 'Dammatan (ٌ)',
    '\u064D': 'Kasratan (ٍ)',
    '\u064E': 'Fatha (َ)',
    '\u064F': 'Damma (ُ)',
    '\u0650': 'Kasra (ِ)',
    '\u0651': 'Shadda (ّ)',
    '\u0652': 'Sukun (ْ)',
    '\u0670': 'Dagger Alif (ٰ)',
}

def count_diacritics(text):
    """Count occurrences of each diacritic in text"""
    counter = Counter()
    for char in text:
        if char in DIACRITICS:
            counter[char] += 1
    return counter

def analyze_files(pred_path, gt_path):
    """Analyze diacritic distribution between prediction and ground truth"""
    
    # Read files
    pred_text = Path(pred_path).read_text(encoding='utf-8')
    gt_text = Path(gt_path).read_text(encoding='utf-8')
    
    # Count diacritics
    pred_counts = count_diacritics(pred_text)
    gt_counts = count_diacritics(gt_text)
    
    # Calculate totals
    total_pred = sum(pred_counts.values())
    total_gt = sum(gt_counts.values())
    
    print("="*80)
    print("DIACRITIC DISTRIBUTION ANALYSIS")
    print("="*80)
    print(f"\nPrediction file: {pred_path}")
    print(f"Ground truth file: {gt_path}")
    print(f"\nTotal diacritics in predictions: {total_pred:,}")
    print(f"Total diacritics in ground truth: {total_gt:,}")
    print(f"Difference: {total_pred - total_gt:+,} ({(total_pred/total_gt-1)*100:+.2f}%)")
    
    print("\n" + "="*80)
    print("DETAILED BREAKDOWN BY DIACRITIC TYPE")
    print("="*80)
    print(f"\n{'Diacritic':<20} {'GT Count':>10} {'Pred Count':>10} {'Diff':>10} {'% Change':>10}")
    print("-"*80)
    
    # Sort by absolute difference
    all_diacs = set(pred_counts.keys()) | set(gt_counts.keys())
    diac_diffs = []
    
    for diac in all_diacs:
        gt_count = gt_counts.get(diac, 0)
        pred_count = pred_counts.get(diac, 0)
        diff = pred_count - gt_count
        if gt_count > 0:
            pct_change = (diff / gt_count) * 100
        else:
            pct_change = float('inf') if pred_count > 0 else 0.0
        
        diac_diffs.append((diac, gt_count, pred_count, diff, pct_change))
    
    # Sort by absolute percentage change
    diac_diffs.sort(key=lambda x: abs(x[4]), reverse=True)
    
    for diac, gt_count, pred_count, diff, pct_change in diac_diffs:
        name = DIACRITICS.get(diac, f'U+{ord(diac):04X}')
        if pct_change == float('inf'):
            pct_str = '+∞'
        else:
            pct_str = f"{pct_change:+.1f}%"
        print(f"{name:<20} {gt_count:>10,} {pred_count:>10,} {diff:>+10,} {pct_str:>10}")
    
    print("\n" + "="*80)
    print("TOP SYSTEMATIC ERRORS (by absolute count)")
    print("="*80)
    
    # Sort by absolute difference
    diac_diffs.sort(key=lambda x: abs(x[3]), reverse=True)
    
    print("\nTop 5 under/over-predictions:")
    for i, (diac, gt_count, pred_count, diff, pct_change) in enumerate(diac_diffs[:5], 1):
        name = DIACRITICS.get(diac, f'U+{ord(diac):04X}')
        direction = "OVERPREDICTION" if diff > 0 else "UNDERPREDICTION"
        if pct_change == float('inf'):
            pct_str = '+∞'
        else:
            pct_str = f"{abs(pct_change):.1f}%"
        print(f"\n{i}. {name} - {direction}")
        print(f"   Ground truth: {gt_count:,} | Predicted: {pred_count:,}")
        print(f"   Difference: {abs(diff):,} ({pct_str})")
    
    # Summary for paper
    print("\n" + "="*80)
    print("SUMMARY FOR PAPER")
    print("="*80)
    print("\nThree largest distribution shifts (by percentage):")
    diac_diffs.sort(key=lambda x: abs(x[4]), reverse=True)
    for i, (diac, gt_count, pred_count, diff, pct_change) in enumerate(diac_diffs[:3], 1):
        name = DIACRITICS.get(diac, f'U+{ord(diac):04X}')
        direction = "overprediction" if diff > 0 else "underprediction"
        if pct_change == float('inf'):
            continue
        print(f"• {name} {direction} ({pct_change:+.1f}%): {abs(diff):,} instances")
    
    return pred_counts, gt_counts


if __name__ == "__main__":
    pred_file = "outputs/dev_pred_text_only.txt"
    gt_file = "Public_Data_TrainDev/Dev/dev_gt_diac.txt"
    
    analyze_files(pred_file, gt_file)
