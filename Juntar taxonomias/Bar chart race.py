

top5_knowledge = (
    df_mx[df_mx['Label'] == 'Knowledge']
    .groupby('Competence', as_index=False)['Count']
    .sum()
    .sort_values('Count', ascending=False)
    .head(5)
)

top5_skill = (
    df_mx[df_mx['Label'] == 'Skill']
    .groupby('Competence', as_index=False)['Count']
    .sum()
    .sort_values('Count', ascending=False)
    .head(5)
)

top5_ability = (
    df_mx[df_mx['Label'] == 'Ability']
    .groupby('Competence', as_index=False)['Count']
    .sum()
    .sort_values('Count', ascending=False)
    .head(5)
)