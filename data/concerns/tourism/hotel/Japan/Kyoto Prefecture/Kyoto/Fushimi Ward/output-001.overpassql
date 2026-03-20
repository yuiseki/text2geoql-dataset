[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Fushimi Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
