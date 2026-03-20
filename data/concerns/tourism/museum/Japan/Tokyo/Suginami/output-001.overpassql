[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Suginami"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
