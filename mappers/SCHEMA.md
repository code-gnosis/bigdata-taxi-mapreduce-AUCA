# Cleaned record schema  (/taxi_project/input/cleaned/)

Pipe-delimited, NO header row. The header is stripped during cleaning precisely because
Hadoop splits files across mappers and only one split would ever contain it.

| idx | field            | type  | notes                          |
|-----|------------------|-------|--------------------------------|
| 0   | pickup_datetime  | str   | YYYY-MM-DD HH:MM:SS            |
| 1   | dropoff_datetime | str   | YYYY-MM-DD HH:MM:SS            |
| 2   | passenger_count  | int   | 1..8                           |
| 3   | trip_distance    | float | miles, > 0                     |
| 4   | PULocationID     | int   | 1..265                         |
| 5   | DOLocationID     | int   | 1..265                         |
| 6   | payment_type     | int   | 1=Credit 2=Cash 3=No charge 4=Dispute |
| 7   | fare_amount      | float | > 0                            |
| 8   | tip_amount       | float | >= 0                           |
| 9   | tolls_amount     | float | >= 0                           |
| 10  | total_amount     | float | > 0                            |
| 11  | hour             | int   | 0..23  (derived at clean time) |
| 12  | dayofweek        | int   | 0=Mon .. 6=Sun (derived)       |
| 13  | duration_min     | float | derived                        |
