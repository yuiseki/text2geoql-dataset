[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Aoba Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
