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

# Mapping Files
1. Have a mapping for degree names in IGP table to degree names in GES table. Will need to match by Universit **and** Degree Name.  Used to tie IGP to GES.

2. In the final dashboard, want to have a panel / view that compares the selected degree to other "related" degrees. Could use another mapping table OR a column where the value is the list of (University, degree_name) related degree programmes?

## IGP-GES Degree Mapping File

Issue regarding the mapping file used to tag IGP to GES. For NUS IGP, several degree programmes were consolidated under **one entry criteria**. Two such generic programmes: 

- Engineering (absorbing Biomed / Chem / Civil / etc)
- Humanities & Sciences (General FASS degree + specialized Science courses)

The consolidated entries only appear from AY 23 / 24 onwards, so it's just one year. 

To make things consistent across the IGP and GES tables:

- Will explode the records for the common courses to the individual ones. 
- For example will take the admissions data for the common engineering course and populate the individual engineering courses with it. 

- Use the <mark>SALARY TABLE AS THE STARTING POINT</mark>. i.e. use the GES course names as the base reference and match to the IGP records based on the GES degree names. Logical because there's no point including degrees with no graduated batches. 

Rationale is that when the user checks for their degree they are more likely to use the old name instead of the common course. This also preserves granularity and richness of information. 

Think I can just add a note to explain that it was merged in 2023

# TO DO
- Will need to add notes for the places for certain degrees for certain years. E.g. DSA in NUS has a huge jump after a few years because the cohort count is merged with the general intake. 