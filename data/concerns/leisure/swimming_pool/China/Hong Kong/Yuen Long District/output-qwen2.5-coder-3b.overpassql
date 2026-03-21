[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh-hk"="中華民國香港特別行政區"];
(
  nwr["leisure"="swimming_pool"](area.outer);
);
out geom;
