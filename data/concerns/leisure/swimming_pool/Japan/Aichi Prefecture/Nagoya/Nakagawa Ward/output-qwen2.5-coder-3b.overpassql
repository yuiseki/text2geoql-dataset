[out:json][timeout:30];
area["name:en"="Aichi Prefecture"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["leisure"="swimming_pool"](area.inner)(area.outer);
);
out geom;
