SELECT
    round_id,
    round_number,
    stato
FROM sealed_rounds
WHERE auction_id = <ID_ASTA>
ORDER BY round_number;
