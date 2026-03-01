option task = { 
  name: "alert_hga",
  every: 10s,
}

from(bucket: "lunar-mission")
  |> range(start: -1m)
  |> filter(fn: (r) => r._measurement == "comms")
  |> filter(fn: (r) => r._field == "ber")
  |> map(fn: (r) => ({ r with 
      _field: "ber_alert",
      level:
        if r._value > 0.05 then "CRIT"
        else if r._value > 0.01 then "WARN"
        else if r._value > 0.005 then "INFO"
        else "OK",
      message:
        if r._value > 0.05 then "CRITICAL: High Bit Error Rate. Signal lost."
        else if r._value > 0.01 then "WARNING: Signal quality degrading."
        else if r._value > 0.005 then "INFO: Minor signal noise detected."
        else "Signal quality nominal."
    }))
  |> keep(columns: ["_time", "_measurement", "_field", "_value", "level", "message"])
  |> to(bucket: "lunar-mission", org: "esa-sic")
