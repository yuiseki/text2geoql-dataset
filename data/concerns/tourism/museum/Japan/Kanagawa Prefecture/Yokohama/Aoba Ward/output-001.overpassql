[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Aoba Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
