import sys
import pandas as pd
from scipy import stats

OUTPUT_TEMPLATE = (
    '"Did more/less users use the search feature?" p-value:  {more_users_p:.3g}\n'
    '"Did users search more/less?" p-value:  {more_searches_p:.3g} \n'
    '"Did more/less instructors use the search feature?" p-value:  {more_instr_p:.3g}\n'
    '"Did instructors search more/less?" p-value:  {more_instr_searches_p:.3g}'
)


def main():
    searchdata_file = sys.argv[1]
    data = pd.read_json(searchdata_file, orient='records', lines=True)

    data['is_even_uid'] = data['uid'] % 2 == 0
    data['is_never_searched'] = data['search_count'] == 0

    contingency = pd.crosstab(data['is_even_uid'], data['is_never_searched'])
    _, more_users_p, _, _ = stats.chi2_contingency(contingency)

    even_uid = data[data['is_even_uid'] == True]
    odd_uid = data[data['is_even_uid'] == False]
    more_searches_p = stats.mannwhitneyu(even_uid['search_count'], odd_uid['search_count']).pvalue

    instr_data = data[data['is_instructor'] == True]
    contingency_instr = pd.crosstab(instr_data['is_even_uid'], instr_data['is_never_searched'])
    _, more_instr_p, _, _ = stats.chi2_contingency(contingency_instr)

    even_uid_instr = instr_data[instr_data['is_even_uid'] == True]
    odd_uid_instr = instr_data[instr_data['is_even_uid'] == False]
    more_instr_searches_p = stats.mannwhitneyu(even_uid_instr['search_count'], odd_uid_instr['search_count']).pvalue
    
    # Output
    print(OUTPUT_TEMPLATE.format(
        more_users_p=more_users_p,
        more_searches_p=more_searches_p,
        more_instr_p=more_instr_p,
        more_instr_searches_p=more_instr_searches_p,
    ))


if __name__ == '__main__':
    main()
