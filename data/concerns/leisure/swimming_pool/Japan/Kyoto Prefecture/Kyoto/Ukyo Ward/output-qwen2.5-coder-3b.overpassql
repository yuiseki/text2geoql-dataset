[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kyoto Prefecture"]->.inner;
(
  nwr["leisure"="swimming_pool"](area.inner)(area.outer);
);
out geom;
