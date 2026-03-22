[out:json][timeout:30];
area["name:en"="Piedmont"]->.outer;
area["name:en"="Turin"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;