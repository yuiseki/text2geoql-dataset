[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Higashikurume"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
