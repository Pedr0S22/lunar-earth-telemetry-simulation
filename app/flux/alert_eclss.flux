option task = {name: "alert_eclss", every: 10s}

from(bucket: "lunar-mission")
    |> range(start: -1m)
    |> filter(fn: (r) => r._measurement == "eclss")
    |> filter(fn: (r) => r._field == "radiation")
    |> map(
        fn: (r) =>
            ({r with _field: "radiation_alert",
                level:
                    if r._value >= 5.0 then
                        "CRIT"
                    else if r._value >= 2.0 then
                        "WARN"
                    else if r._value >= 0.5 then
                        "INFO"
                    else
                        "OK",
                message:
                    if r._value >= 5.0 then
                        "CRITICAL: Radiation detected at Chernobyl levels!"
                    else if r._value >= 2.0 then
                        "WARNING: High radiation levels detected."
                    else if r._value >= 0.5 then
                        "INFO: Radiation slightly elevated."
                    else
                        "Normal radiation levels.",
            }),
    )
    |> keep(
        columns: [
            "_time",
            "_measurement",
            "_field",
            "_value",
            "level",
            "message",
        ],
    )
    |> to(bucket: "lunar-mission", org: "esa-sic")
