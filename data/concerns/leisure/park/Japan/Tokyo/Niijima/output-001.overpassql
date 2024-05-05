[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Niijima"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
