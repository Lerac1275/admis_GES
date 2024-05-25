# NUS Data

## Processed scraped file
- From AY 22/23 onwards all specialized engineering courses were merged into a combined "Engineering" course intake. Require special treatment for this

- From AY 21/22 onwards all hard science courses and the *Arts & Social Sciences* major were merged into were merged into a combined *Humanities & Scieces* course intake. Require special treatment for this

# NTU Data

## Processed scraped file
- From AY 21/22 onwards, CoHASS Double Major programmes split into individual SOH Double Major & SSS Double Major Programmes. Require special treatment for this.


# Ideas

Ultimately want a data story for each selected degree. Elements should include Historical trends for admission + Graduate $$$ + Vacancies. 

- Want to either start or end with a single scatter plot (IGP vs GES) showing where that degree lies. 

Then transition into a storytelling mode displaying how that degree's stats compare to :
    - Other related degrees in the same field (in other universities)
    - Other degrees in the same faculty (if applicable)
    - Other degrees in the home university 

For the comparison piece could play around with a couple of metrics & measures. 

Metrics could be: 
- Ranks (Out of university / all courses)
- Absolute values

Measures could be:
- Average % $$$ / RP / GPA change in last 3 years
- Change in vacancies
- Entry criteria to $$$ ratio
- some measure of $$$ & vacancy

1. Have a mapping for degree names in IGP table to degree names in GES table. Will need to match by Faculty **and** Degree. 

2. In the final dashboard, want to have a panel / view that compares the selected degree to other "related" degrees. Could use another mapping table OR a column where the value is the list of (University, degree_name) related degree programmes?