# Experiment subset

To generate the subset used for this experiment, use the following command, inside the src folder:

```bash
python src/main.py
[?] Provide an identifier for this experiment (only lowercase and dashes allowed): primary-experiment-balanced
[?] Should feature selection be performed? (y/N): n
[?] Should data balancing be performed? (y/N): y
[?] Should data be shuffled? (y/N): n
[?] In which language should data be plotted?: 
 ❯ PT-BR
   EN
[?] The experiments will consider a single percentage or a range of percentages?: 
   range
 ❯ single
[?] Provide the percentage for the experiments: 10
[?] How many decimals would you like to use to present the percentage(s)?: 0
```
