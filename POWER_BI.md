# Construire le rapport Power BI

Cette livraison contient les CSV et le plan du rapport. Le fichier .pbix reste à construire par toi dans Power BI Desktop (Windows).

## Import

Importer `outputs/test_predictions.csv`, `outputs/test_metrics.csv`, `outputs/feature_importance.csv`, `outputs/calibration.csv` et `outputs/validation_metrics.csv`.
Vérifier les types avec paramètres régionaux anglais États-Unis si le point décimal est mal lu. Les tables métriques sont globales et ne doivent pas être liées artificiellement aux clients. Seule la table de prédictions sert aux filtres clients.

## Mesures DAX dans test_predictions

```dax
Clients = COUNTROWS(test_predictions)
Default Rate = AVERAGE(test_predictions[actual_default])
Mean Predicted PD = AVERAGE(test_predictions[predicted_probability])
Flagged Clients = SUM(test_predictions[predicted_default])
TP = COUNTROWS(FILTER(test_predictions, test_predictions[actual_default] = 1 && test_predictions[predicted_default] = 1))
FP = COUNTROWS(FILTER(test_predictions, test_predictions[actual_default] = 0 && test_predictions[predicted_default] = 1))
FN = COUNTROWS(FILTER(test_predictions, test_predictions[actual_default] = 1 && test_predictions[predicted_default] = 0))
Precision = DIVIDE([TP], [TP] + [FP])
Recall = DIVIDE([TP], [TP] + [FN])
```

Si ton éditeur DAX attend des points-virgules, remplacer les virgules des arguments.

## Page 1 : Profils du jeu de test

Cartes : Clients, Default Rate, Mean Predicted PD. Histogramme des probabilités estimées. Effectif et taux de défaut par risk_band. Filtres : AGE, SEX et risk_band. Afficher « 6 000 clients du test — prototype académique, données historiques ».

## Page 2 : Performances

Cartes globales ROC-AUC, Average Precision et Brier depuis test_metrics. Matrice : actual_default en lignes, predicted_default en colonnes, nombre de ID en valeur. Courbe de calibration : mean_probability en X et observed_default_rate en Y, avec une diagonale si possible. Les indicateurs globaux du CSV restent fixes quand on filtre les clients ; le signaler explicitement. Les mesures DAX Precision et Recall se recalculent sur le segment filtré.

## Page 3 : Facteurs et erreurs

Barres des 10 principales importances par permutation. Tableau ID / probabilité / défaut réel / type d'erreur. Les importances sont globales sur validation, pas une explication de chaque client. SEX est disponible pour une première exploration descriptive, sans preuve d'équité.

Utiliser un fond clair, bleu marine, une couleur d'alerte orange, des pourcentages avec une décimale. Ne jamais présenter la somme des probabilités comme une perte monétaire.
