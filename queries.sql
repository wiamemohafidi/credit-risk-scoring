-- Exécuter dans SQLite sur outputs/credit_risk.sqlite
-- Échantillon de test uniquement ; montants en NT$, pas en euros.
SELECT COUNT(*) AS clients, AVG(actual_default) AS default_rate,
       AVG(predicted_probability) AS mean_predicted_pd
FROM test_predictions;

SELECT risk_band, COUNT(*) AS clients, AVG(actual_default) AS observed_default_rate,
       AVG(predicted_probability) AS mean_predicted_pd
FROM test_predictions GROUP BY risk_band;

SELECT actual_default, predicted_default, COUNT(*) AS clients
FROM test_predictions GROUP BY actual_default, predicted_default;

SELECT ID, predicted_probability, actual_default, error_type
FROM test_predictions WHERE error_type = 'false_negative'
ORDER BY predicted_probability ASC LIMIT 20;
