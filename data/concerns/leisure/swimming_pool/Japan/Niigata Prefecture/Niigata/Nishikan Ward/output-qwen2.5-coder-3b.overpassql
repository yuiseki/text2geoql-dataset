[out:json][timeout:30];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:en"="Niigata"]->.inner;
(
  nwr["leisure"="swimming_pool"](area.inner)(area.outer);
);
out geom;
