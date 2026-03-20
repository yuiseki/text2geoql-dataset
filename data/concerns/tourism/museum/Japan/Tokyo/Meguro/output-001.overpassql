[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Meguro"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
