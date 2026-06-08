# Nutrition Datasets

NutriPrompt uses external nutrition datasets for experimentation and enrichment of nutritional analysis workflows.

## Current Dataset

### Food Nutrition Dataset

Source:
https://www.kaggle.com/datasets

Used for:

* Nutritional values
* Macronutrient analysis
* Sodium and fiber references
* Nutrition density experimentation
* Future recommendation systems

## Important Note

Raw datasets are intentionally excluded from this repository to:

* Keep the repository lightweight
* Avoid large unnecessary uploads
* Respect dataset licensing and attribution
* Improve repository maintainability

To reproduce the experiments:

1. Download the dataset manually from Kaggle
2. Place the extracted files inside:

```text
data/raw/kaggle/
```

Expected structure:

```text
data/raw/kaggle/
└── FINAL FOOD DATASET/
```
