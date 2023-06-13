[Reference](https://www.influxdata.com/blog/getting-started-influxdb-grafana/)

Initialization commands:

```
influx setup --name mydb --host http://localhost:8086 \
 -u my-name -p my-password -o my-org \
 -b my-bucket -t my-token -r 0 -f
```

Docker compose:
`docker compose up`