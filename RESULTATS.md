# Première exécution — données UCI

Modèle sélectionné sur validation : forest_calibrated. Test indépendant de 6 000 clients.

| Mesure | Valeur test |
|---|---:|
| ROC-AUC | 0.7736 |
| Average Precision | 0.5468 |
| Brier | 0.1370 |
| Log-loss | 0.4362 |
| Précision au seuil retenu | 52.5% |
| Rappel au seuil retenu | 56.4% |
| Seuil choisi sur validation (F1) | 0.24 |
| Taux de défaut observé test | 22.1% |

Au seuil de 0.24, 749 défauts sont détectés et 578 manqués ; 677 non-défaillants sont signalés à tort. Ces erreurs illustrent le compromis du seuil. Le score n'est pas une validation métier ni réglementaire.

Reproduction : voir requirements.txt et outputs/run_metadata.json. Les résultats peuvent varier selon versions et plateforme. Le rapport Power BI n'est pas encore construit.
