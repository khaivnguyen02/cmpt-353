import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
pd.options.mode.chained_assignment = None  # default='warn'

OUTPUT_TEMPLATE = (
    "Initial T-test p-value: {initial_ttest_p:.3g}\n"
    "Original data normality p-values: {initial_weekday_normality_p:.3g} {initial_weekend_normality_p:.3g}\n"
    "Original data equal-variance p-value: {initial_levene_p:.3g}\n"
    "Transformed data normality p-values: {transformed_weekday_normality_p:.3g} {transformed_weekend_normality_p:.3g}\n"
    "Transformed data equal-variance p-value: {transformed_levene_p:.3g}\n"
    "Weekly data normality p-values: {weekly_weekday_normality_p:.3g} {weekly_weekend_normality_p:.3g}\n"
    "Weekly data equal-variance p-value: {weekly_levene_p:.3g}\n"
    "Weekly T-test p-value: {weekly_ttest_p:.3g}\n"
    "Mann-Whitney U-test p-value: {utest_p:.3g}"
)


def main():
    reddit_counts = sys.argv[1]
    counts = pd.read_json(reddit_counts, lines=True)

    # Filter: Values in 2012 and 2013 and in /r/canada subreddit only.
    counts = counts[(counts['date'].dt.year.isin([2012, 2013])) & (counts['subreddit'] == 'canada')]
    
    # Separate the weekdays from the weekends
    weekdays = counts[counts['date'].dt.weekday < 5]
    weekends = counts[counts['date'].dt.weekday >= 5]

    # Student's T-Test
    initial_ttest_p = stats.ttest_ind(weekdays['comment_count'], weekends['comment_count']).pvalue
    initial_weekday_normality_p = stats.normaltest(weekdays['comment_count']).pvalue
    initial_weekend_normality_p = stats.normaltest(weekends['comment_count']).pvalue
    initial_levene_p = stats.levene(weekdays['comment_count'], weekends['comment_count']).pvalue
    
    # Fix 1: transforming data
    transformed_weekdays = np.sqrt(weekdays['comment_count'])
    transformed_weekends = np.sqrt(weekends['comment_count'])

    transformed_weekday_normality_p = stats.normaltest(transformed_weekdays).pvalue
    transformed_weekend_normality_p = stats.normaltest(transformed_weekends).pvalue
    transformed_levene_p = stats.levene(transformed_weekdays, transformed_weekends).pvalue

    # Fix 2: the Central Limit Theorem
    weekdays['year'] = weekdays['date'].dt.isocalendar().year
    weekdays['week'] = weekdays['date'].dt.isocalendar().week

    weekends['year'] = weekends['date'].dt.isocalendar().year
    weekends['week'] = weekends['date'].dt.isocalendar().week

    weekdays_grouped = weekdays.groupby(by=['year','week']).mean(numeric_only=True).reset_index()
    weekends_grouped = weekends.groupby(by=['year','week']).mean(numeric_only=True).reset_index()

    weekly_weekday_normality_p = stats.normaltest(weekdays_grouped['comment_count']).pvalue
    weekly_weekend_normality_p = stats.normaltest(weekends_grouped['comment_count']).pvalue
    weekly_levene_p = stats.levene(weekdays_grouped['comment_count'], weekends_grouped['comment_count']).pvalue

    weekly_ttest_p = stats.ttest_ind(weekdays_grouped['comment_count'], weekends_grouped['comment_count']).pvalue

    # Fix 3: Non-parametric test
    utest_p = stats.mannwhitneyu(weekdays['comment_count'], weekends['comment_count']).pvalue

    print(OUTPUT_TEMPLATE.format(
        initial_ttest_p=initial_ttest_p,
        initial_weekday_normality_p=initial_weekday_normality_p,
        initial_weekend_normality_p=initial_weekend_normality_p,
        initial_levene_p=initial_levene_p,
        transformed_weekday_normality_p=transformed_weekday_normality_p,
        transformed_weekend_normality_p=transformed_weekend_normality_p,
        transformed_levene_p=transformed_levene_p,
        weekly_weekday_normality_p=weekly_weekday_normality_p,
        weekly_weekend_normality_p=weekly_weekend_normality_p,
        weekly_levene_p=weekly_levene_p,
        weekly_ttest_p=weekly_ttest_p,
        utest_p=utest_p,
    ))


if __name__ == '__main__':
    main()
